import pymongo
import tqdm

client = pymongo.MongoClient('localhost')
db = client['nlp_projectDB']['knowledge_base']

for record in tqdm.tqdm(db.find(), total=db.count()):
    if "bn:" in record['c1'] or "bn:" in record['c2']:
       record['disabled'] = True
        db.save(record)
    # fields = record['c1'].split("::")
    """
    e = False
    if len(fields) == 2:
        e = True
        if "bn" in fields[0]:
            record['c1'] = fields[1]
        else:
            record['c1'] = fields[0]
        if "bn" in fields[0] and "bn" in fields[1]:
            continue
    fields = record['c2'].split("::")
    if len(fields) == 2:
        e = True
        if "bn" in fields[0]:
            record['c2'] = fields[1]
        else:
            record['c2'] = fields[0]
        if "bn" in fields[0] and "bn" in fields[1]:
            continue
    if e:
        db.save(record)
    """
