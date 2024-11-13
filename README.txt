Team Name: BazingaMart

Team Roles:
1. Lucy Kopin - Users Guru
2. Shivam Mani - Social Guru
3. Kat Holo - Sellers Guru
4. Katie Xu - Products Guru
5. Philip Lee - Carts Guru

Link to gitlab: https://gitlab.oit.duke.edu/lbk15/cs-316-mini-amazon-project-24-fall

Milestone 3:
Link to video: https://duke.zoom.us/rec/share/5s5DI-qc4bQDjm4HI4AStBuHO0zaTjS7uDuD0tsDrWMM0tSGbaPrhwrcI01NzL0S.FRz7omfrfbPK5gN5?startTime=1729543717000
Where to find end points:
1. Users Guru: Given a user id, find all purchases of that user.
    - inside of models/purchases.py in the get_all_by_user(uid) function
2. Products Guru: Given an integer k, find top k most expensive products.
    - inside of models/product.py in the get_top_k_expensive(k) function
3. Carts Guru: Given a user id, find the items in the cart for that user.
    - inside of models/cart_items.py in the get_all_items(user_id) function
4. Sellers Guru: Given id of a merchant/seller, find the products that are in their inventory.
    -inside of models/inventory_items in the get_all_by_user(seller_id) function
5. Social Guru: Given a user id, find the 5 most recent feedback they posted.
    - inside models/reviews.py, in the get_recent_feedback(user_id, limit=5) function.

Milestone 3:
Link to video: https://duke.zoom.us/rec/share/5s5DI-qc4bQDjm4HI4AStBuHO0zaTjS7uDuD0tsDrWMM0tSGbaPrhwrcI01NzL0S.FRz7omfrfbPK5gN5?startTime=1729543717000
Where to find end points:
1. Users Guru: Given a user id, find all purchases of that user.
    - inside of models/purchases.py in the get_all_by_user(uid) function
2. Products Guru: Given an integer k, find top k most expensive products.
    - inside of models/product.py in the get_top_k_expensive(k) function
3. Carts Guru: Given a user id, find the items in the cart for that user.
    - inside of models/cart_items.py in the get_all_items(user_id) function
4. Sellers Guru: Given id of a merchant/seller, find the products that are in their inventory.
    - -inside of models/inventory_items in the get_all_by_user(seller_id) function
5. Social Guru: Given a user id, find the 5 most recent feedback they posted.
    - inside models/reviews.py, in the get_recent_feedback(user_id, limit=5) function.

Milestone 4:
Link to video: https://duke.zoom.us/rec/play/pgtW8oIfcpS-7kh3s_GH9KzGGDn6TXzlRrKSVA7JNtZGzkB0xFr1C-joDbqerurJPq8YGc9JlSfMHpqw.Br3noU9xHdAkh-hR?canPlayFromShare=true&from=share_recording_detail&startTime=1731439501000&componentName=rec-play&originRequestUrl=https%3A%2F%2Fduke.zoom.us%2Frec%2Fshare%2F8Qnjsho-aiTpoNmhklsGEbFhi1noEgG8DWE1e5sKveT5IsgiUmrhcRuGvyi4mizX.5J5irZP_RQtXPH48%3FstartTime%3D1731439501000
1. Users Guru:
    - Updated gen.py to generate appropriate data for new schema & updated features to use large data
    - Added address as a user field in database
    - Added ability to edit any subset of user information except user id
    - Added public view page & ability to view your personal public page
    - Added ability to add and withdraw from balance
    - Added pagination to products on index.html

2. Products Guru:


3. Carts Guru:
    - Added update quantity, remove rows, delete cart, submit cart functionality for carts.
    - Added orders table to record a cart submission
    - Made orders paginated and added the order list and detail order view pages to user home.
    - Added coupon table and coupon functionality for price discounts.
    - Generated data for carts, cart products, and orders.
    - UI updates via pagination / grid browsing.

4. Sellers Guru
    -Updated gen.py to randomly populate and generate large testing database
    -Debugged gen.py and generated data -Created template to implement pagination across most pages (Inventory, Products, Reviews)
    -Added Seller View pages/buttons of View Inventory and Fulfillment Center
    -UI updates via pagination, reflecting updated database schema
5. Social Guru: 