from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random

num_users = 100
num_products = 2000
num_carts = 1000
max_products_per_cart = 50

Faker.seed(0)
fake = Faker()

seller_user_ids = []
product_ids = []

# Function to get CSV writer
def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

# Generate users
def gen_users(num_users):
    with open('db/generated/Users.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        custom_user_id = 0
        custom_email = 'test@test.com'
        custom_password = generate_password_hash('123')
        custom_firstname = 'Test'
        custom_lastname = 'Test'
        custom_address = '123 Towerview St, Durham, NC'
        custom_seller = True
        custom_balance = 500.00
        writer.writerow([custom_user_id, custom_email, custom_password, custom_firstname, custom_lastname, custom_address, custom_seller, custom_balance])
        if custom_seller:
            seller_user_ids.append(custom_user_id)
        
        for uid in range(1, num_users + 1):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            address = fake.address().replace("\n", ", ")
            seller = fake.boolean(chance_of_getting_true=10)
            balance = round(random.uniform(0, 1000), 2)
            if seller:
                seller_user_ids.append(uid)
            writer.writerow([uid, email, password, firstname, lastname, address, seller, balance])
        print(f'{num_users} generated')
    return

# Generate products
def gen_products(num_products, num_users):
    products = []
    with open('db/generated/Products.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(1, num_products + 1):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=4)[:-1]
            price = round(random.uniform(5, 500), 2)
            available = fake.boolean()
            seller_id = random.choice(seller_user_ids) if seller_user_ids else 1
            product_quantity = fake.random_int(min=1, max=100)
            products.append((pid, name, price, available, seller_id, product_quantity))
            writer.writerow([pid, name, price, available, seller_id, product_quantity])
            product_ids.append(pid)
        print(f'{num_products} generated')
    return products

# Generate carts
def gen_carts(num_carts, num_users):
    with open('db/generated/Cart.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Carts...', end=' ', flush=True)
        for order_id in range(1, num_carts + 1):
            if order_id % 50 == 0:
                print(f'{order_id}', end=' ', flush=True)
            user_id = fake.random_int(min=0, max=num_users) 
            created_at = fake.date_time_this_year(before_now=True, after_now=False)             
            total_price = round(random.uniform(10, 1000), 2)
            purchase_status = random.choice(['Completed', 'Cancelled'])
            coupon_code = fake.bothify(text='???-##', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ') if fake.boolean(chance_of_getting_true=20) else None
            writer.writerow([order_id, user_id, created_at, total_price, purchase_status, coupon_code])
        print(f'{num_carts} generated')
    return


def gen_cart_products(num_carts, max_products_per_cart, products):
    cart_products_data = {}
    order_ids = list(range(1, num_carts + 1))
    random.shuffle(order_ids)

    # FULFILLED_PERCENTAGE below is the percentage of carts that are fulfilled
    # The rest are incomplete (i.e. 1 - FULFILLED_PERCENTAGE)
    # Remember to keep this number high otherwise you will end up with a lot of orders that 
    # are unfulfilled, and each order may have a lot of other items to go one by one to fulfill
    # which will make be a pain to do manually

    FULFILLED_PERCENTAGE = 0.995
    num_carts_with_all_fulfilled = int(num_carts * FULFILLED_PERCENTAGE)
    carts_with_all_fulfilled = set(order_ids[:num_carts_with_all_fulfilled])

    with open('db/generated/CartProducts.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('CartProducts...', end=' ', flush=True)
        for order_id in range(1, num_carts + 1):
            cart_products_data[order_id] = []
            num_products_in_cart = fake.random_int(min=1, max=max_products_per_cart)
            selected_products = random.sample(products, min(num_products_in_cart, len(products)))
            for product in selected_products:
                pid, _, _, available, _, product_quantity = product
                if available and product_quantity > 0:
                    quantity = fake.random_int(min=1, max=min(5, product_quantity))
                    seller_id = random.choice(seller_user_ids) if seller_user_ids else 1
                    unit_price = round(random.uniform(5, 500), 2)

                    # Set fulfillment_status based on whether the order is selected
                    if order_id in carts_with_all_fulfilled:
                        fulfillment_status = 'Fulfilled'
                    else:
                        fulfillment_status = random.choice(['Incomplete', 'Fulfilled'])

                    writer.writerow([order_id, pid, seller_id, quantity, unit_price, fulfillment_status])
                    cart_products_data[order_id].append(fulfillment_status)
        print(f'CartProducts for {num_carts} carts generated')
    return cart_products_data


# Generate orders
def gen_orders(num_carts, num_users, cart_products_data):
    with open('db/generated/Orders.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Orders...', end=' ', flush=True)
        for order_id in range(1, num_carts + 1):
            if order_id % 50 == 0:
                print(f'{order_id}', end=' ', flush=True)
            user_id = fake.random_int(min=0, max=num_users)  
            created_at = fake.date_time_this_year(before_now=True, after_now=False)             
            total_price = round(random.uniform(10, 1000), 2)
            item_statuses = cart_products_data.get(order_id, [])
            if all(status == 'Fulfilled' for status in item_statuses):
                fulfillment_status = 'Fulfilled'
            else:
                fulfillment_status = 'Incomplete'
            coupon_code = fake.bothify(text='???-##', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ') if fake.boolean(chance_of_getting_true=20) else None
            writer.writerow([order_id, user_id, created_at, total_price, fulfillment_status, coupon_code])
        print(f'{num_carts} generated')
    return


# Generate coupons
def gen_coupons(num_coupons=50):
    with open('db/generated/Coupons.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Coupons...', end=' ', flush=True)
        for _ in range(num_coupons):
            coupon_code = fake.bothify(text='???-##', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            discount_percentage = fake.random_int(min=1, max=100)
            writer.writerow([coupon_code, discount_percentage])
        print(f'{num_coupons} generated')
    return

# Generate reviews
def gen_reviews(num_reviews=500, num_users=num_users, num_products=num_products):
    with open('db/generated/Reviews.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Reviews...', end=' ', flush=True)
        for review_id in range(1, num_reviews + 1):
            if review_id % 100 == 0:
                print(f'{review_id}', end=' ', flush=True)
            user_id = fake.random_int(min=0, max=num_users)  
            seller_id = random.choice(seller_user_ids) if seller_user_ids else 1
            reviewer_type = random.choice(['buyer', 'seller'])
            product_id = random.choice(product_ids)
            stars = fake.random_int(min=1, max=5)
            review_text = fake.text(max_nb_chars=200)
            time_written = fake.date_time_this_year(before_now=True, after_now=False)   
            upvotes = fake.random_int(min=0, max=100)
            writer.writerow([review_id, user_id, seller_id, reviewer_type, product_id, stars, review_text, time_written, upvotes])
        print(f'{num_reviews} generated')
    return

# Generate the data
gen_users(num_users)
products = gen_products(num_products, num_users)
gen_carts(num_carts, num_users)
cart_products_data = gen_cart_products(num_carts, max_products_per_cart, products)
gen_orders(num_carts, num_users, cart_products_data)
gen_coupons()
gen_reviews()
