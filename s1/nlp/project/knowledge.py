import requests

with open("_PRIVATE_babelkey") as fin:
    _babelkey = fin.read()[:-1]

_url = "http://151.100.179.26:8080/KnowledgeBaseServer/rest-api/{}"
_header = "Content-Type: application/json"


def items_number_from(start_id=0):
    response = requests.get(
        _url.format("items_number_from"),
        params={
            'id': start_id,
            'key': _babelkey,
        })
    count = response.json()
    return count


def items_from(start_id=0):
    last_id = start_id
    while True:
        response = requests.get(
            _url.format("items_from"),
            params={
                'id': last_id,
                'key': _babelkey,
            })
        batch = response.json()
        if not batch:
            yield StopIteration

        last_id = len(batch) + 1
        yield from batch


def add_item(item, dry_run=False):
    assert (item['question'])
    assert (item['answer'])
    assert (item['relation'])
    assert (item['context'])
    assert (item['domains'])
    assert (item['c1'])
    assert (item['c2'])

    response = requests.post(
        _url.format("add_item" if dry_run else "add_item_test"),
        params={'key': _babelkey, },
        data=item,
    )
    success = response.body == "1"
    return success


def add_items(items, dry_run=False):
    for item in items:
        # TODO: use add_items endpoint
        add_item(item, dry_run)


if __name__ == "__main__":
    print(items_number_from(0))
    for idx, itm in enumerate(items_from(0)):
        if idx > 10: break
        print(itm)
