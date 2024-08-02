from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

# Configuration for MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/my_mongo"
mongo = PyMongo(app)
db = mongo.db
collection = db.frequently_bought_together

@app.route('/')
def index():
    return "Welcome to the MongoDB REST API!"

# Show the results with the hightest lift
@app.route('/frequently_bought_together/<id>', methods=['GET'])
def get_item(id):
    # Define the filter
    print(id)
    query_filter = {
        '$or': [
            {'antecedents': f'{id}'},
            {'consequents': f'{id}'}
        ]
    }
    print(query_filter)
    # Define the sort criteria
    sort_criteria = [('lift', -1)]

    # Perform the query
    results = collection.find(query_filter).sort(sort_criteria)
    print(results)

    # Get the first result
    item = results[0]
    if item:
        #item['_id'] = str(item['_id'])  # Convert ObjectId to string
        return jsonify(item['antecedents'] + item['consequents'])
    else:
        return jsonify({'error': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
