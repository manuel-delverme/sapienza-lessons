import requests
import math
from collections import Counter
import pickle
from functools import lru_cache
from typing import List, Dict, AnyStr
from collections import defaultdict
import sqliteshelve as shelve

API_ENDPOINT = "https://api.edamam.com/search?"
API_ID = "c31346ed"
API_KEY = "8f8ddfde6c9fd54070517b1396c3f12a"

def retrieve_request_url(recipe_name):
    url = API_ENDPOINT + "app_id=" + API_ID + "&" + "app_key=" + API_KEY + "&q=" + recipe_name
    return url


def get_recipes(recipe_name: str) -> List[Dict[AnyStr, Dict[AnyStr, AnyStr]]]:
    try:
        return recipe_db[recipe_name]
    except KeyError:
        url = retrieve_request_url(recipe_name)
        print("GET", recipe_name)
        response = requests.get(url)
        json = response.json()

        if len(json['hits']) == 0:
            recipe_db[recipe_name] = None
        else:
            recipe_db[recipe_name] = [hit['recipe'] for hit in json['hits']]
    return recipe_db[recipe_name]


def recipe_to_vect(recipe_name):
    core = ['sugar', 'salt', 'oil', 'flour', 'herbs', 'cheese', 'cider', 'lemon', 'garlic', 'milk', 'pepper',
            'chicken', 'soda', 'water', 'butter', 'prosciutto', 'baking powder', 'lard', 'basil', 'egg', 'yeast']
    features = dict()
    for k in core:
        features[k] = 0
    recipes = get_recipes(recipe_name)
    for recipe_json in recipes:  # TODO: add more than 10hits fetching
        for ingredient in recipe_json['ingredients']:
            found = False
            for k in core:
                if k in ingredient['text'].lower():
                    found = True
                    features[k] += ingredient['weight']
            if not found:
                print('?', ingredient['text'])
    for k in features:
        features[k] /= len(recipes)
    return features

def recipe_words(recipe_name):
    recipes = get_recipes(recipe_name)
    if not recipes:
        raise ValueError("food not found")
    words = ' '.join([entry['text'].lower() for rj in recipes for entry in rj['ingredients']])
    return words

def recipes_ingredients(recipe_name):
    recipes = get_recipes(recipe_name)
    if not recipes:
        return []
    recipes = [entry['text'].lower() for rj in recipes for entry in rj['ingredients']]
    return recipes

def cache_tf_idf():
    # words = Counter()
    df = defaultdict(int)
    nr_recipes = 0
    with open("food_names.lst.bak") as fin:
        for food in fin:
            name = food[:-1].lower().split(" ")[0]
            try:
                recipe = recipe_words(name).split(" ")
            except ValueError:
                pass
            except requests.exceptions.SSLError:
                pass
            # except Exception as e:
            #     print("stopping with:", repr(e), e)
            #     break
            else:
                nr_recipes += 1
                for word in set(recipe):
                    df[word] += 1
                # words.update(recipe)
    # with open("wordsCounter.pkl", "wb") as fout:
    #     pickle.dump(words, fout)
    # # assume any word appears at least one time e.g. there is an recipe that just list all the words
    print("got", nr_recipes, "recipes")
    for k in list(df.keys()):
        if df[k] == 1:
            del df[k]
        else:
            df[k] = df[k] / nr_recipes
    with open("documentFreq.pkl", "wb") as fout:
        pickle.dump(dict(df), fout)
    # total = sum(words.values())
    # for k in words:
    #     words[k] = words[k]/total
    # with open("termFreq.pkl", "wb") as fout:
    #     pickle.dump(words, fout)

def weight_recipe_terms(recipe):
    with open("documentFreq.pkl", "rb") as fin:
        df = pickle.load(fin)
    with open("termFreq.pkl", "rb") as fin:
        tf = pickle.load(fin)
    weights = []
    for word in recipe.split(" "):
        if word not in tf:
            weight = 1 * -math.log(1)
        else:
            weight = tf[word] * -math.log(df[word])
        weights.append(weight)
    return weights

def query_knowledge(dish_name):
    recipes = recipes_ingredients(dish_name)
    for recipe in recipes:
        x = weight_recipe_terms(recipe)
        for word, xi in sorted(zip(recipe, x), key=lambda x:x[1]):
            print(word, xi)

def main():
    try:
        query_knowledge("pizza")
    except FileNotFoundError:
        print("generating df")
        cache_tf_idf()

if __name__ == "__main__":
    recipe_db = shelve.open("cache/recipes.sqlite")
    try:
        main()
    finally:
        recipe_db.close()
