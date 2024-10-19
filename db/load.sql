\COPY Users(id, email, password, firstname, lastname) FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(id)+1 FROM Purchases),
                         false);


\COPY Cart FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV;
SELECT pg_catalog.setval('public.cart_order_id_seq', 
                        (SELECT MAX(order_id) + 1 FROM Cart),
                        false);

\COPY CartProducts FROM 'CartProducts.csv' WITH DELIMITER ',' NULL '' CSV;