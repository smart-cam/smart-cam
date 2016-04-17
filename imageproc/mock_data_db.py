from util.db import DynamoDBUtils
import os

# Create all Classes
db = DynamoDBUtils()

#db.purge_table()

#db.display_items()

#db.create_full_items(num_items=500, start_time=1459472400)

db.delete_by_id('Entrance')
