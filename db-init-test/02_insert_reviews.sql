-- INSERT statements for review table
-- Note: id is auto-increment, so it's not included in the INSERT statements
-- IMPORTANT: This table depends on product_id from the product table and user_id from the users table
-- Make sure to insert products and users first, then update the foreign key values below

INSERT INTO public.review (name, comment, rating, user_id, product_id, created_at, updated_at) VALUES
('John Smith', 'Excellent headphones! Great sound quality and comfortable to wear.', 5, 4, 1, '2024-01-15 10:30:00', '2024-01-15 10:30:00'),
('Sarah Johnson', 'Good case, fits perfectly and provides good protection.', 4, 4, 2, '2024-01-16 14:20:00', '2024-01-16 14:20:00'),
('Mike Wilson', 'Amazing laptop stand! Very sturdy and adjustable.', 5, 4, 3, '2024-01-17 09:15:00', '2024-01-17 09:15:00'),
('Emily Davis', 'Great keyboard for gaming and typing. RGB lighting is awesome!', 4, 4, 4, '2024-01-18 16:45:00', '2024-01-18 16:45:00'),
('David Brown', 'Perfect gaming mouse with precise tracking.', 5, 4, 5, '2024-01-19 11:30:00', '2024-01-19 11:30:00'),
('Lisa Anderson', 'USB hub works great, all ports function properly.', 3, 4, 6, '2024-01-20 13:20:00', '2024-01-20 13:20:00'),
('Tom Garcia', 'Wireless charger is fast and convenient.', 4, 4, 7, '2024-01-21 15:10:00', '2024-01-21 15:10:00'),
('Anna Martinez', 'Amazing sound quality! Perfect for outdoor activities.', 5, 4, 8, '2024-01-22 12:00:00', '2024-01-22 12:00:00'),
('Chris Lee', 'Monitor stand is very well built and functional.', 4, 4, 9, '2024-01-23 08:45:00', '2024-01-23 08:45:00'),
('Rachel Taylor', 'Great webcam for video calls, crystal clear quality.', 4, 4, 10, '2024-01-24 17:30:00', '2024-01-24 17:30:00'),
('James White', 'Headphones are good but could be more comfortable for long use.', 3, 4, 1, '2024-01-25 10:15:00', '2024-01-25 10:15:00'),
('Maria Rodriguez', 'Case is okay, but the material could be better.', 3, 4, 2, '2024-01-26 14:40:00', '2024-01-26 14:40:00'),
('Kevin Thompson', 'Laptop stand is exactly what I needed for my setup.', 5, 4, 3, '2024-01-27 09:30:00', '2024-01-27 09:30:00'),
('Jennifer Clark', 'Keyboard is fantastic! Love the mechanical switches.', 5, 4, 4, '2024-01-28 16:20:00', '2024-01-28 16:20:00'),
('Robert Lewis', 'Gaming mouse has excellent precision and build quality.', 4, 4, 5, '2024-01-29 11:45:00', '2024-01-29 11:45:00');
