CREATE TYPE product_category AS ENUM (
    'Electronics',
    'Home & Kitchen',
    'Books',
    'Clothing',
    'Beauty & Personal Care',
    'Sports & Outdoors',
    'Toys & Games',
    'Food & Beverages',
    'Automotive',
    'Health & Wellness'
);

CREATE TABLE Users (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL DEFAULT ' ',
    seller BOOLEAN DEFAULT FALSE,
    balance DECIMAL(12,2) DEFAULT 0
);

CREATE TABLE Products (
    product_id INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    seller_id INT NOT NULL REFERENCES Users(id),
    product_quantity INT NOT NULL DEFAULT 1,
    description TEXT,
    image VARCHAR(255),
    category product_category NOT NULL,
    PRIMARY KEY (product_id, seller_id)
);

CREATE TABLE Cart (
    order_id INT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    user_id INT NOT NULL REFERENCES Users(id),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    total_price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    purchase_status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    coupon_code VARCHAR(50)
);

CREATE TABLE CartProducts (
    order_id INT NOT NULL REFERENCES Cart(order_id) ON DELETE CASCADE,
    product_id INT NOT NULL,
    seller_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(12,2) NOT NULL,
    fulfillment_status VARCHAR(50) NOT NULL DEFAULT 'Incomplete',
    PRIMARY KEY (order_id, product_id, seller_id),
    FOREIGN KEY (product_id, seller_id) REFERENCES Products(product_id, seller_id)
);


CREATE TABLE Coupons (
    coupon_code VARCHAR(50) PRIMARY KEY,
    discount_percentage INT NOT NULL CHECK (discount_percentage > 0 AND discount_percentage <= 100)
);

CREATE TABLE Orders (
    order_id INT PRIMARY KEY REFERENCES Cart(order_id),
    user_id INT NOT NULL REFERENCES Users(id),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    total_price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    fulfillment_status VARCHAR(50) NOT NULL DEFAULT 'Incomplete',
    coupon_code VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);


CREATE TABLE Reviews (
    review_id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    user_id INT NOT NULL REFERENCES Users(id),
    seller_id INT NOT NULL REFERENCES Users(id),
    reviewer_type VARCHAR(50) NOT NULL,
    product_id INT,
    stars INT CHECK (stars BETWEEN 1 AND 5),
    review_text TEXT,
    time_written TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    upvotes INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_product FOREIGN KEY (product_id, seller_id) REFERENCES Products(product_id, seller_id) ON DELETE CASCADE
);
