CREATE TABLE Users (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    balance DECIMAL(12,2) DEFAULT 100000000.00
);

CREATE TABLE Products (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    available BOOLEAN DEFAULT TRUE
);

CREATE TABLE Purchases (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    quantity INT NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    time_purchased timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);

CREATE TABLE Cart (
    order_id INT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    user_id INT NOT NULL REFERENCES Users(id),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    total_price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    purchase_status VARCHAR(50) NOT NULL DEFAULT 'Pending'
);

CREATE TABLE CartProducts (
    order_id INT NOT NULL REFERENCES Cart(order_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES Products(id),
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (order_id, product_id)
);

CREATE TABLE Inventory (
    seller_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(255) UNIQUE NOT NULL,
    product_quantity INT NOT NULL DEFAULT 1,
    PRIMARY KEY (product_id, seller_id)
);

CREATE TABLE Reviews (
    review_id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    user_id INT NOT NULL REFERENCES Users(id),
    reviewer_type VARCHAR(50) NOT NULL,
    product_id INT REFERENCES Products(id),
    stars INT CHECK (stars BETWEEN 1 AND 5),
    review_text TEXT,
    time_written TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    upvotes INT NOT NULL DEFAULT 0
);