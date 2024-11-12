\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV;
-- Adjusting the sequence for Users' auto-generated primary key:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id) + 1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV;
-- Adjusting the sequence for Products' auto-generated primary key:
SELECT pg_catalog.setval('public.products_product_id_seq',
                         (SELECT MAX(product_id) + 1 FROM Products),
                         false);

\COPY Reviews FROM 'Reviews.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.reviews_review_id_seq',
                         (SELECT MAX(review_id)+1 FROM reviews),
                         false);
\COPY Reviews FROM 'Reviews.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.reviews_review_id_seq',
                         (SELECT MAX(review_id)+1 FROM reviews),
                         false);

\COPY Cart(order_id, user_id, created_at, total_price, purchase_status, coupon_code) FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV;
SELECT pg_catalog.setval('public.cart_order_id_seq',
                         (SELECT MAX(order_id) + 1 FROM Cart),
                         false);
\COPY Cart(order_id, user_id, created_at, total_price, purchase_status, coupon_code) FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV;
SELECT pg_catalog.setval('public.cart_order_id_seq',
                         (SELECT MAX(order_id) + 1 FROM Cart),
                         false);

\COPY CartProducts FROM 'CartProducts.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY Coupons FROM 'Coupons.csv' WITH DELIMITER ',' CSV;

\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV;

