
# Overview
The idea of this implementation is to use the [Apriori algorithm](https://en.wikipedia.org/wiki/Apriori_algorithm) to implement a list of Frequently Bought Together items. For right now the assumption is to just pass one item (product) as an input and get a list of up to 3 items. 

## Setup 
Start your environment with

```bash
python3 -m venv myenv
source myenv/bin/activate

pip3 install -r requirements.txt


deactivate
```

## Support threshold
To determine the list of frequently bought together items, we need to set a support threshold. The support threshold represents the minimum frequency at which items need to occur together to be considered as frequently bought together. You can adjust the support threshold based on your specific requirements and dataset. Experimenting with different values can help you find the optimal threshold for your analysis.
We set 
```
min_threshold=2
```

## Generating test data
Generates orders in JSON format and saves them to file in /data/ directory or in a (local) MongoDB database "my_mongodb" in a collection "orders". 
You can pass as an input the number of orders you'd like to generate
```
# Example usage
python3 generate_orders.py True 150
```
