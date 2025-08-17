"""
Swish Payment Service
Handles Swish m-commerce API integration for payment processing
"""

import requests
import json
import uuid
import os
from datetime import datetime
from decimal import Decimal
from flask import current_app, url_for
from models import SwishPayment
from app import db


class SwishService:
    """Service class for handling Swish payments"""
    
    # Swish API endpoints
    BASE_URL_TEST = "https://mss.cpc.getswish.net/swish-cpcapi/api"
    BASE_URL_PROD = "https://cpc.getswish.net/swish-cpcapi/api"
    
    def __init__(self):
        self.base_url = self.BASE_URL_TEST if current_app.config.get('SWISH_TEST_MODE', True) else self.BASE_URL_PROD
        self.payee_alias = current_app.config.get('SWISH_PAYEE_ALIAS')  # Merchant Swish number
        self.cert_path = current_app.config.get('SWISH_CERT_PATH')
        self.cert_password = current_app.config.get('SWISH_CERT_PASSWORD')
        self.ca_cert_path = current_app.config.get('SWISH_CA_CERT_PATH')
    
    def create_payment_request(self, amount, message, payer_alias=None, payee_alias=None, reference=None, 
                             user_id=None, application_id=None, event_id=None):
        """
        Create a new Swish payment request
        
        Args:
            amount (Decimal): Payment amount in SEK
            message (str): Message to show to payer (max 50 chars)
            payer_alias (str, optional): Payer's phone number
            reference (str, optional): Merchant reference
            user_id (int, optional): Associated user ID
            application_id (int, optional): Associated application ID
            event_id (int, optional): Associated event ID
            
        Returns:
            SwishPayment: Created payment record
        """
        
        # Generate unique identifiers
        payment_id = uuid.uuid4().hex.upper()
        callback_identifier = uuid.uuid4().hex
        
        if not reference:
            reference = f"BMK-{datetime.now().strftime('%Y%m%d')}-{payment_id[:8]}"
        
        # Create payment record in database
        payment = SwishPayment()
        payment.id = payment_id
        payment.payee_payment_reference = reference
        payment.payer_alias = payer_alias
        payment.payee_alias = payee_alias or self.payee_alias
        payment.amount = amount
        payment.currency = 'SEK'
        payment.message = message[:50]  # Ensure max 50 characters
        payment.callback_url = url_for('swish_callback', payment_id=payment_id, _external=True)
        payment.callback_identifier = callback_identifier
        payment.user_id = user_id
        payment.application_id = application_id
        payment.event_id = event_id
        
        db.session.add(payment)
        db.session.commit()
        
        # Prepare API request
        request_data = {
            "payeePaymentReference": reference,
            "callbackUrl": payment.callback_url,
            "payeeAlias": payee_alias or self.payee_alias,
            "amount": str(amount),
            "currency": "SEK",
            "message": message[:50],
            "callbackIdentifier": callback_identifier
        }
        
        # Add payer alias if provided (for m-commerce)
        if payer_alias:
            request_data["payerAlias"] = payer_alias
        
        try:
            # Make API request to Swish
            response = self._make_api_request(
                method='PUT',
                endpoint=f'/v2/paymentrequests/{payment_id}',
                data=request_data
            )
            
            if response.status_code == 201:
                # Payment request created successfully
                payment.status = 'PENDING'
                db.session.commit()
                
                current_app.logger.info(f"Swish payment request created: {payment_id}")
                return payment
            else:
                # Handle error response
                payment.status = 'ERROR'
                if response.status_code == 422:
                    error_data = response.json()
                    payment.error_code = error_data[0].get('errorCode') if error_data else 'UNKNOWN'
                    payment.error_message = error_data[0].get('errorMessage') if error_data else 'Validation error'
                else:
                    payment.error_code = str(response.status_code)
                    payment.error_message = f"HTTP {response.status_code}: {response.reason}"
                
                db.session.commit()
                current_app.logger.error(f"Swish payment request failed: {payment.error_message}")
                return payment
                
        except Exception as e:
            payment.status = 'ERROR'
            # Truncate error message to fit database field
            error_msg = str(e)
            if len(error_msg) > 950:  # Leave some margin
                error_msg = error_msg[:950] + "...[truncated]"
            payment.error_message = error_msg
            db.session.commit()
            current_app.logger.error(f"Swish API error: {str(e)}")
            return payment
    
    def get_payment_status(self, payment_id):
        """
        Retrieve payment status from Swish API
        
        Args:
            payment_id (str): Swish payment request ID
            
        Returns:
            dict: Payment status information
        """
        try:
            response = self._make_api_request(
                method='GET',
                endpoint=f'/v1/paymentrequests/{payment_id}'
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                current_app.logger.error(f"Failed to get payment status: {response.status_code}")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error getting payment status: {str(e)}")
            return None
    
    def cancel_payment(self, payment_id):
        """
        Cancel a pending payment request
        
        Args:
            payment_id (str): Swish payment request ID
            
        Returns:
            bool: True if cancelled successfully
        """
        try:
            cancel_data = [{
                "op": "replace",
                "path": "/status",
                "value": "cancelled"
            }]
            
            response = self._make_api_request(
                method='PATCH',
                endpoint=f'/v1/paymentrequests/{payment_id}',
                data=cancel_data,
                content_type='application/json-patch+json'
            )
            
            if response.status_code == 200:
                # Update local payment record
                payment = SwishPayment.query.get(payment_id)
                if payment:
                    payment.status = 'CANCELLED'
                    payment.date_cancelled = datetime.utcnow()
                    db.session.commit()
                
                current_app.logger.info(f"Swish payment cancelled: {payment_id}")
                return True
            else:
                current_app.logger.error(f"Failed to cancel payment: {response.status_code}")
                return False
                
        except Exception as e:
            current_app.logger.error(f"Error cancelling payment: {str(e)}")
            return False
    
    def process_callback(self, payment_id, callback_data, callback_identifier):
        """
        Process callback from Swish with payment status update
        
        Args:
            payment_id (str): Swish payment request ID
            callback_data (dict): Callback payload from Swish
            callback_identifier (str): Callback identifier for validation
            
        Returns:
            bool: True if processed successfully
        """
        try:
            payment = SwishPayment.query.get(payment_id)
            if not payment:
                current_app.logger.error(f"Payment not found for callback: {payment_id}")
                return False
            
            # Validate callback identifier
            if payment.callback_identifier != callback_identifier:
                current_app.logger.error(f"Invalid callback identifier for payment: {payment_id}")
                return False
            
            # Update payment status
            payment.status = callback_data.get('status', payment.status)
            
            if payment.status == 'PAID':
                payment.payment_reference = callback_data.get('paymentReference')
                payment.date_paid = datetime.utcnow()
                current_app.logger.info(f"Swish payment completed: {payment_id}")
            elif payment.status in ['DECLINED', 'ERROR', 'CANCELLED']:
                payment.error_code = callback_data.get('errorCode')
                payment.error_message = callback_data.get('errorMessage', '')
                current_app.logger.info(f"Swish payment {payment.status.lower()}: {payment_id}")
            
            db.session.commit()
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error processing Swish callback: {str(e)}")
            return False
    
    def _make_api_request(self, method, endpoint, data=None, content_type='application/json'):
        """
        Make authenticated request to Swish API
        
        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            data (dict): Request payload
            content_type (str): Content-Type header
            
        Returns:
            requests.Response: API response
        """
        url = self.base_url + endpoint
        headers = {'Content-Type': content_type}
        
        # Configure SSL certificates
        cert = None
        if self.cert_path and self.cert_password:
            cert = (self.cert_path, self.cert_password)
        
        verify = self.ca_cert_path if self.ca_cert_path else True
        
        # Make request
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, cert=cert, verify=verify)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data, cert=cert, verify=verify)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, cert=cert, verify=verify)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response


def format_swish_amount(amount):
    """
    Format amount for Swish API (string with max 2 decimal places)
    
    Args:
        amount (Decimal or float): Amount to format
        
    Returns:
        str: Formatted amount
    """
    return "{:.2f}".format(Decimal(str(amount)))


def validate_swish_phone(phone_number):
    """
    Validate Swedish phone number for Swish
    Format: Country code + phone number without leading zero
    Example: 46712345678
    
    Args:
        phone_number (str): Phone number to validate
        
    Returns:
        str or None: Formatted phone number or None if invalid
    """
    import re
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone_number)
    
    # Check if it's a Swedish mobile number
    if digits.startswith('46'):
        # Already has country code
        if len(digits) >= 11 and len(digits) <= 13:
            return digits
    elif digits.startswith('07'):
        # Swedish mobile starting with 07, convert to international format
        if len(digits) == 10:
            return '46' + digits[1:]  # Remove leading 0, add country code
    elif len(digits) == 9 and digits.startswith('7'):
        # Swedish mobile without leading 0
        return '46' + digits
    
    return None