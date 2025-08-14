#!/usr/bin/env python3
"""
Quick verification script to test critical application functionality
Prevents server crashes and template errors
"""
import sys
from app import app

def test_critical_routes():
    """Test that critical routes don't crash"""
    print("Testing critical application routes...")
    
    with app.test_client() as client:
        # Test public routes
        public_routes = [
            ('/', 'Homepage'),
            ('/om-oss', 'About page'),
            ('/evenemang', 'Events page'),
            ('/ansokan', 'Application page'),
            ('/login', 'Login page'),
            ('/register', 'Registration page')
        ]
        
        passed = 0
        failed = 0
        
        for route, name in public_routes:
            try:
                response = client.get(route)
                if response.status_code == 500:
                    print(f"❌ {name} ({route}): Server error (500)")
                    failed += 1
                elif response.status_code in [200, 302, 404]:
                    print(f"✅ {name} ({route}): OK ({response.status_code})")
                    passed += 1
                else:
                    print(f"⚠️  {name} ({route}): Unexpected status ({response.status_code})")
                    failed += 1
            except Exception as e:
                print(f"❌ {name} ({route}): Exception - {str(e)}")
                failed += 1
        
        print(f"\nRoute Test Results: {passed} passed, {failed} failed")
        return failed == 0

def test_template_syntax():
    """Test that templates render without syntax errors"""
    print("\nTesting template rendering...")
    
    with app.test_client() as client:
        # Test routes that use complex templates
        template_routes = [
            ('/', 'Homepage template'),
            ('/evenemang', 'Events template'),
            ('/ansokan', 'Application template')
        ]
        
        passed = 0
        failed = 0
        
        for route, name in template_routes:
            try:
                response = client.get(route)
                if response.status_code == 500:
                    print(f"❌ {name}: Template error")
                    failed += 1
                else:
                    print(f"✅ {name}: Renders correctly")
                    passed += 1
            except Exception as e:
                print(f"❌ {name}: Exception - {str(e)}")
                failed += 1
        
        print(f"Template Test Results: {passed} passed, {failed} failed")
        return failed == 0

def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Brunnsbo Musikklasser - Application Verification")
    print("=" * 60)
    
    routes_ok = test_critical_routes()
    templates_ok = test_template_syntax()
    
    print("\n" + "=" * 60)
    if routes_ok and templates_ok:
        print("✅ All tests passed! Application is stable.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check output above.")
        sys.exit(1)

if __name__ == '__main__':
    main()