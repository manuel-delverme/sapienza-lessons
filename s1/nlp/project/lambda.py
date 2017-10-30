import requests
import json
import pprint
import difflib
import glob
from utils import disk_cache

def post_sample(access_token, text, intent):
    headers = { 'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token,}

    body = [{
        "text": text,
        "entities": [
            { "entity": "intent", "value": intent }
        ]
    }]

    output = requests.post('https://api.wit.ai/samples', data=json.dumps(body), headers=headers).json()
    return output

@disk_cache
def load_pattern_list():
    patterns = []
    gathered = 0
    total = 0
    for file_name in glob.glob("patterns/*"):
        print("FILE:", file_name)
        with open(file_name) as fin:
            for row in fin:
                total += 1
                try:
                    question, target = parse_row(row)
                    patterns.append((question, target))
                except ValueError as e:
                    print("SKIP", row, e)
                    continue
                else:
                    gathered += 1
    print("kept", gathered/total)
    return patterns

def parse_row(entry, stem=False):
    entry = entry.strip("\n").lower()
    if "\t" not in entry:
        print("SKIPPING", entry)
        raise ValueError()
    question, target = entry.split("\t")
    target = target.strip()
    target = target.strip("\"\'")
    question = question.strip()
    question = question.strip("\"\'")
    if "?" in target:
        question, target = target, question
    if "2" in target:
        target = target.replace("2", "to")

    if target not in relations:
        # raises ValueError if no close match
        new_target, = difflib.get_close_matches(target, relations, n=1)
        target = new_target
    return question, target

# @disk_cache
def load_domain_list():
    with open("chatbot_maps/domains_to_relations.tsv") as fin:
        relations = set()
        for row in fin:
            relations.update(row.strip("\n").lower().split("\t")[1:])
    relations.remove("")
    relations = list(relations)
    return relations


relations = load_domain_list()
def main():
    access_token = "D5CBU67EQTN2RDNQC77V6SFBJ465UVCJ"
    data = load_pattern_list()
    for text, intent in data:
        output = post_sample(access_token, text, intent)
        print(output)

main()
