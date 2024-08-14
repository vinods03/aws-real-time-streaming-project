import random
import copy
from datetime import datetime
from uuid import uuid4


customer_ids = ['c100','c101','c102','c103','c104','c105','c106','c107','c108','c109','c110']
seller_ids = ['s100','s101','s102','s103','s104','s105','s106','s107','s108','s109','s110']
products = [
    {'code': 'p101', 'name': 'abc', 'price': 100},
    {'code': 'p102', 'name': 'def', 'price': 200},
    {'code': 'p103', 'name': 'ghi', 'price': 300},
    {'code': 'p104', 'name': 'jkl', 'price': 400},
    {'code': 'p105', 'name': 'mno', 'price': 500},
    {'code': 'p106', 'name': 'pqr', 'price': 600},
    {'code': 'p107', 'name': 'stu', 'price': 700},
    {'code': 'p108', 'name': 'vwx', 'price': 800},
    {'code': 'p109', 'name': 'yza', 'price': 900},
    {'code': 'p110', 'name': 'bcd', 'price': 1000},
]

def make_order():

    order_id = str(uuid4())
    customer_id = random.choice(customer_ids)
    seller_id = random.choice(seller_ids)
    order_purchase_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    num_products_in_order = random.randint(1,len(products))
    products_in_order = []
    products_not_yet_present_in_order = copy.copy(products)

    for i in range(0, num_products_in_order):
        product = random.choice(products_not_yet_present_in_order)
        products_in_order.append({'product_code': product['code'], 'product_name': product['name'], 'product_price': product['price'], 'product_qty': random.randint(1,5)})
        products_not_yet_present_in_order.remove(product)

    final_order = {
        'order_id': order_id,
        'customer_id': customer_id,
        'seller_id': seller_id,
        'products': products_in_order,
        'order_purchase_timestamp': order_purchase_timestamp
    }

    return final_order
