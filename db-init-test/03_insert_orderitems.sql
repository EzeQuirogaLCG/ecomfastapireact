-- INSERT statements for orderitems table
-- Note: id is auto-increment, so it's not included in the INSERT statements
-- IMPORTANT: This table depends on order_id from the orders table
-- Make sure to insert orders first, then update the order_id values below

INSERT INTO public.orderitems (name, quantity, price, order_id) VALUES
('Wireless Bluetooth Headphones', 2, 15000, 1),
('Smartphone Case', 1, 2500, 1),
('Laptop Stand', 1, 8000, 2),
('Mechanical Keyboard', 1, 12000, 2),
('Gaming Mouse', 2, 6000, 2),
('USB-C Hub', 1, 4500, 3),
('Wireless Charger', 3, 3500, 3),
('Bluetooth Speaker', 1, 9000, 4),
('Monitor Stand', 1, 5500, 4),
('Webcam', 1, 11000, 5),
('Wireless Bluetooth Headphones', 1, 15000, 5),
('Smartphone Case', 2, 2500, 6),
('Laptop Stand', 1, 8000, 6),
('Mechanical Keyboard', 1, 12000, 7),
('Gaming Mouse', 1, 6000, 7),
('USB-C Hub', 2, 4500, 7),
('Wireless Charger', 1, 3500, 8),
('Bluetooth Speaker', 2, 9000, 8),
('Monitor Stand', 1, 5500, 9),
('Webcam', 1, 11000, 9);
