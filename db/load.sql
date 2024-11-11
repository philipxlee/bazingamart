\COPY Users(id, email, password, firstname, lastname) FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_product_id_seq',
                         (SELECT MAX(product_id)+1 FROM Products),
                         false);

\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(id)+1 FROM Purchases),
                         false);

\COPY Reviews FROM 'Reviews.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.reviews_review_id_seq',
                         (SELECT MAX(review_id)+1 FROM reviews),
                         false);

\COPY Cart(order_id, user_id, created_at, total_price, purchase_status, coupon_code) FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV;
SELECT pg_catalog.setval('public.cart_order_id_seq',
                         (SELECT MAX(order_id) + 1 FROM Cart),
                         false);

\COPY CartProducts(order_id, product_id, quantity, unit_price) FROM 'CartProducts.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY Coupons(coupon_code, discount_percentage) FROM 'Coupons.csv' WITH DELIMITER ',' CSV;

--\COPY Inventory FROM 'Inventory.csv' WITH DELIMITER ',' NULL '' CSV;