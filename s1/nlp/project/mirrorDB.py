import pymongo
import knowledge
import datetime
with open("/tmp/last_db_sync", "a") as fout:
    fout.write(repr(datetime.datetime.now()) + "\n")

URI = "localhost:27017"
client = pymongo.MongoClient(URI)
db = client['nlp_projectDB']
try:
    db.create_collection(name='knowledge_base')
except pymongo.errors.CollectionInvalid:
    pass

last_id = db.knowledge_base.count()
total_entries = knowledge.items_number_from(last_id)
items_left = knowledge.items_number_from(last_id)
if items_left == 0:
    print("nothing to do")
else:
    print("starting from ", last_id, items_left)
    count = last_id
    for users_batch in knowledge.batches_from(last_id):
        count += len(users_batch)
        db.knowledge_base.insert_many(users_batch)
        print((count*100) / total_entries, "%")
