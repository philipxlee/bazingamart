from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random

num_users = 100
num_products = 2000
num_purchases = 2500
num_carts = 100
max_products_per_cart = 50

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')


def gen_users(num_users):
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            balance = 0.0 
            writer.writerow([uid, email, password, firstname, lastname, balance])
        print(f'{num_users} generated')
    return


def gen_products(num_products):
    available_pids = []
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=4)[:-1]
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            available = fake.random_element(elements=('true', 'false'))
            if available == 'true':
                available_pids.append(pid)
            writer.writerow([pid, name, price, available])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids


def gen_purchases(num_purchases, available_pids):
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            time_purchased = fake.date_time()
            writer.writerow([id, uid, pid, time_purchased])
        print(f'{num_purchases} generated')
    return


def gen_carts(num_carts, num_users, available_pids):
    with open('Cart.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('Carts...', end=' ', flush=True)
        for order_id in range(1, num_carts + 1):
            if order_id % 50 == 0:
                print(f'{order_id}', end=' ', flush=True)
            user_id = fake.random_int(min=1, max=num_users)
            created_at = fake.date_time_between(start_date='-6m', end_date='now')
            total_price = 0.00
            purchase_status = random.choice(['Pending', 'Completed', 'Cancelled'])
            writer.writerow([order_id, user_id, created_at, total_price, purchase_status])
        print(f'{num_carts} generated')
    return


def gen_cart_products(num_carts, max_products_per_cart, available_pids):
    with open('CartProducts.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        print('CartProducts...', end=' ', flush=True)
        for order_id in range(1, num_carts + 1):
            num_products = fake.random_int(min=1, max=max_products_per_cart)
            selected_pids = random.sample(available_pids, min(num_products, len(available_pids)))
            for pid in selected_pids:
                quantity = fake.random_int(min=1, max=5)
                unit_price = float(fake.pydecimal(left_digits=3, right_digits=2, positive=True))
                writer.writerow([order_id, pid, quantity, unit_price])
        print(f'CartProducts for {num_carts} carts generated')
    return


available_pids = gen_products(num_products)
gen_users(num_users)
gen_purchases(num_purchases, available_pids)
gen_carts(num_carts, num_users, available_pids)
gen_cart_products(num_carts, max_products_per_cart, available_pids)
