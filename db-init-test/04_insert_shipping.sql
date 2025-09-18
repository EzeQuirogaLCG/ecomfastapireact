-- INSERT statements for shipping table
-- Note: id is auto-increment, so it's not included in the INSERT statements
-- IMPORTANT: This table depends on order_id from the orders table
-- Make sure to insert orders first, then update the order_id values below

INSERT INTO public.shipping (address, "postalCode", country, city, order_id) VALUES
('123 Main Street, Apt 4B', 10001, 'United States', 'New York', 1),
('456 Oak Avenue, Suite 200', 90210, 'United States', 'Beverly Hills', 2),
('789 Pine Road', 60601, 'United States', 'Chicago', 3),
('321 Elm Street', 33101, 'United States', 'Miami', 4),
('654 Maple Drive', 98101, 'United States', 'Seattle', 5),
('987 Cedar Lane', 75201, 'United States', 'Dallas', 6),
('147 Birch Boulevard', 30301, 'United States', 'Atlanta', 7),
('258 Spruce Street', 02101, 'United States', 'Boston', 8),
('369 Willow Way', 80201, 'United States', 'Denver', 9),
('741 Ash Avenue', 85001, 'United States', 'Phoenix', 10);
