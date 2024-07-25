import json
import uuid
import os
import random
from pymongo import MongoClient
import sys

# List of items to choose from
items_list = [
    {"name": "Red Hat", "sku": "PcmProdSku2_837138451048"},
    {"name": "Green Shoe", "sku": "PcmProdSku1_820633028024"},
    {"name": "White Socks", "sku": "PIMBundle-sku-122527558739"},
    {"name": "Blue Jeans", "sku": "PcmProdSku3_837138451055"},
    {"name": "Yellow Shirt", "sku": "PcmProdSku4_837138451062"},
    {"name": "Black Belt", "sku": "PcmProdSku5_837138451069"},
    {"name": "Purple Scarf", "sku": "PcmProdSku6_837138451076"},
    {"name": "Orange Gloves", "sku": "PcmProdSku7_837138451083"},
    {"name": "Pink Hat", "sku": "PcmProdSku8_837138451090"},
    {"name": "Brown Boots", "sku": "PcmProdSku9_837138451097"}
]

def generate_order(order_id):
    num_items = random.randint(2, 4)
    selected_items = random.sample(items_list, num_items)
    items_data = [
        {
            "type": "item",
            "id": str(uuid.uuid4()),
            "name": item["name"],
            "sku": item["sku"]
        }
        for item in selected_items
    ]
    return {
        "id": str(uuid.uuid4()),
        "type": "order",
        "status": "complete",
        "payment": "paid",
        "customer": {
            "name": f"Customer {order_id}",
            "email": f"customer{order_id}@example.com"
        },
        "relationships": {
            "items": {
                "data": items_data
            }
        }
    }




def insert_data_to_mongodb(data):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')

    # Access the database
    db = client['my_mongo']

    # Access the collection
    collection = db['orders']

    # Insert the data into the collection
    collection.insert_many(data['data'])

    # Close the MongoDB connection
    client.close()


def save_orders(data_loc, add_data_to_mongodb=False, num_records=100):
    print(data_loc)

    if add_data_to_mongodb:
        insert_data_to_mongodb(data_loc)



    print(f"Generated {num_records} orders.")

# Generate and save orders
add_data_to_mongodb = bool(sys.argv[1])  # Set to True if data should be added to MongoDB, False otherwise
num_records = int(sys.argv[2]) if len(sys.argv) > 1 else 50  # Number of records to generate and save

orders = [generate_order(i) for i in range(1, num_records)]

data = {
    "data": orders
}
# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# Save the JSON data to a file
with open(f'data/order_items_{num_records}.json', 'w') as f:
    json.dump(data, f, indent=2)
    
save_orders(data, add_data_to_mongodb, num_records)
# Example usage
# python3 generate_orders.py True 150

