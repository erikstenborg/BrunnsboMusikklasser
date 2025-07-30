-- Brunnsbo Musikklasser Database Export
-- Generated on 2025-07-30
-- Copy these statements and run them in your production database

-- First, ensure the tables exist (they should be created automatically by your app)

-- Export Admin Users
INSERT INTO admin_users (id, username, email, password_hash, active, created_at, last_login) VALUES 
(1, 'admin', 'admin@brunnsbomusikklasser.nu', 'scrypt:32768:8:1$VT36Up4YvZGExnxr$f53abf7ac9a9852b6f4cb71b9d225a69e08c2a78d2364045af126c38605997fa09a1464ac3f543a497875c562457756a1282380e772ddecde7b48fb9126f3842', true, '2025-07-29 09:59:26.705822', '2025-07-29 10:17:15.918331')
ON CONFLICT (id) DO UPDATE SET
    username = EXCLUDED.username,
    email = EXCLUDED.email,
    password_hash = EXCLUDED.password_hash,
    active = EXCLUDED.active,
    created_at = EXCLUDED.created_at,
    last_login = EXCLUDED.last_login;

-- Export Events
INSERT INTO event (id, title, description, event_date, location, ticket_url, is_active, created_at) VALUES 
(1, 'Julkonsert 2025', 'Vår traditionella julkonsert med alla våra musikklasser. Ett magiskt evenemang där eleverna får visa upp vad de lärt sig under terminen.', '2025-12-15 18:00:00', 'Johannebergskyrkan', 'https://example.com/tickets/julkonsert', true, '2025-07-29 09:59:26.834591'),
(2, 'Vårkonsert 2026', 'Avslutning på läsåret med en härlig vårkonsert där alla klasser medverkar.', '2026-05-20 19:00:00', 'Annedalskyrkan', '', false, '2025-07-29 09:59:26.834595'),
(3, '40-årsjubileum Festkonsert', 'En extra festlig konsert för att fira Brunnsbo Musikklassers 40-årsjubileum! Med tidigare elever, nuvarande elever och lärare.', '2025-10-10 18:30:00', 'Frihamnskyrkan', 'https://www.nortic.se/ticket/event/70581', true, '2025-07-29 09:59:26.834597')
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    event_date = EXCLUDED.event_date,
    location = EXCLUDED.location,
    ticket_url = EXCLUDED.ticket_url,
    is_active = EXCLUDED.is_active,
    created_at = EXCLUDED.created_at;

-- Update sequences to prevent ID conflicts
SELECT setval('admin_users_id_seq', (SELECT MAX(id) FROM admin_users));
SELECT setval('event_id_seq', (SELECT MAX(id) FROM event));

-- Verify the data was imported
SELECT 'Admin Users Count:' as info, COUNT(*) as count FROM admin_users
UNION ALL
SELECT 'Events Count:' as info, COUNT(*) as count FROM event;