import json
import pandas as pd
from mlxtend.frequent_patterns import fpgrowth, apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from pymongo import MongoClient
from bson import ObjectId

def find_frequently_bought_together(transactions):
    # Convert transactions to a DataFrame suitable for the mlxtend library
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df = pd.DataFrame(te_ary, columns=te.columns_)
    #print (df)

    # Apply the Apriori algorithm
    #frequent_itemsets = apriori(df, min_support=0.01, use_colnames=True)
    frequent_itemsets = fpgrowth(df, min_support=0.02, use_colnames=True)
    #print(frequent_itemsets)

    # Generate association rules where the lift is at least 2
    fbt_list = association_rules(frequent_itemsets, metric="lift", min_threshold=2)
    print (fbt_list)

    serialize_to_mongo(fbt_list)

    return fbt_list
 
def serialize_to_mongo(fbt_list):
    # Convert frozenset to list for JSON serialization
    def convert_frozenset(data):
        if isinstance(data, list):
            return [convert_frozenset(item) for item in data]
        elif isinstance(data, dict):
            return {key: convert_frozenset(value) for key, value in data.items()}
        elif isinstance(data, frozenset):
            return list(data)
        elif isinstance(data, ObjectId):
            return str(data)
        else:
            return data

    # Convert DataFrame to a list of dictionaries
    records = fbt_list.to_dict(orient='records')
    # Convert non-serializable objects in the records
    for record in records:
        for key, value in record.items():
            if isinstance(value, frozenset):
                record[key] = convert_frozenset(value)
    #fbt_list = convert_frozenset(fbt_list)

    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')

    # Access the database
    db = client['my_mongo']

    # Access the collection
    collection = db['frequently_bought_together']

    # Insert the data into the collection
    collection.insert_many(records)

    # Close the MongoDB connection
    client.close()


def get_frequently_bought_together_rules(rules, item):
    # Sort rules by descending lift
    filtered_rules = rules[(rules['antecedents'].apply(lambda x: item in x)) | 
                            (rules['consequents'].apply(lambda x: item in x))]
    filtered_rules = filtered_rules.sort_values(by='lift', ascending=False)
    #print(filtered_rules)
    
    # Get the first row for antecedents and append to frequently_bought_together
    frequently_bought_together = []
    antecedents = list(filtered_rules.iloc[0]['antecedents'])
    consequents = list(filtered_rules.iloc[0]['consequents'])
    print("Lift:", filtered_rules.iloc[0]['lift'])
    # If item in antecedents, remove item from antecedents and append to frequently_bought_together
    if item in antecedents:
        antecedents.remove(item)
    else: # If item in consequents, remove item from consequents and append to frequently_bought_together 
        consequents.remove(item)
    
    frequently_bought_together = antecedents + consequents
        
    return frequently_bought_together

# Load the JSON data
with open('data/order_items_100.json', 'r') as f:
    data = json.load(f)

# Extract items from each order
orders = data['data']
transactions = []

#transactions needs a list of items for each order
for order in orders:
    items = [item['name'] for item in order['relationships']['items']['data']]
    transactions.append(items)

# Example usage
item = 'Red Hat'
fbt_list = find_frequently_bought_together(transactions)
result = get_frequently_bought_together_rules(fbt_list, item)

print("Items frequently bought together with", item, ":", result)