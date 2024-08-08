import argparse
import json
import pandas as pd
from mlxtend.frequent_patterns import fpgrowth, apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from pymongo import MongoClient
from bson import ObjectId

def find_frequently_bought_together(transactions, save_to_db=False):
    # Convert transactions to a DataFrame suitable for the mlxtend library
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df = pd.DataFrame(te_ary, columns=te.columns_)
    print("DataFrame:\n")
    print (df)

    # Apply the Apriori algorithm. The minimum support is set to 0.02.
    # The support is computed as the fraction transactions_where_item(s)_occur / total_transactions.
    frequent_itemsets = fpgrowth(df, min_support=0.02, use_colnames=True)
    print("Frequent Itemsets:\n")
    print(frequent_itemsets)

    # Generate association rules where the lift is at least 2
    # The lift metric is commonly used to measure how much more often 
    # the antecedent and consequent of a rule A->C occur together
    # than we would expect if they were statistically independent. 
    # If lift = 1, then A and C are independent. If lift > 1, then A and C are dependent.
    fbt_list = association_rules(frequent_itemsets, metric="lift", min_threshold=0.3)
    print("Association Rules:\n")
    print (fbt_list)

    #serialize_to_mongo(fbt_list)
    if save_to_db:
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


def main():

     # Check if the database should be cleared (using the --reset flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    parser.add_argument("--json", type=str, help="The JSON file for orders to process")
    parser.add_argument("--save_to_db", action="store_true", help="Save the frequently bought together rules to the database.")
    args = parser.parse_args()
    
    # Load the JSON data
    json_filepath = args.json
    with open(json_filepath, 'r') as f: 
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
    fbt_list = find_frequently_bought_together(transactions, args.save_to_db)
    result = get_frequently_bought_together_rules(fbt_list, item)

    print("Items frequently bought together with", item, ":", result)

if __name__ == "__main__":
    main()
