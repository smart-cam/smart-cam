from util.db import DynamoDBUtils
import os

# Create all Classes
db = DynamoDBUtils()

#db.purge_table()

#db.display_items()

#db.create_full_items(num_items=500, start_time=1459472400)

#db.delete_by_id('Entrance')

#db.add_classified()

#db.reset_classified()

print "\n\n\n"

cnt = 0
for row in db.get_classified_items():
    cnt += 1
print "# Classified Item Count", cnt

cnt = 0
d = {}
for row in db.get_unclassified_items():
    d[row['RASP_NAME']] = d.get(row['RASP_NAME'],0) + 1
    cnt += 1
print "# Unclassified Item Count", cnt
print "# Unclassified Items", d

cnt = 0
for row in db.get_processed_items():
    cnt += 1
print "\n# Processed Item Count", cnt

cnt = 0
d = {}
for row in db.get_unprocessed_items():
    d[row['RASP_NAME']] = d.get(row['RASP_NAME'],0) + 1
    cnt += 1
print "# Unprocessed Item Count", cnt
print "# Unprocessed Items", d

