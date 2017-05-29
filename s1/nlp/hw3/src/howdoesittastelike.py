import pickle
import re
from collections import defaultdict
from typing import List, Dict, AnyStr

import numpy as np
import spacy
from sklearn.neighbors import NearestNeighbors

import sqliteshelve

spacy_classifier = None


def nlp(word):
    global spacy_classifier
    if not spacy_classifier:
        spacy_classifier = spacy.load("en")
    return spacy_classifier(word)


API_ENDPOINT = "https://api.edamam.com/search?"
API_ID = "c31346ed"
API_KEY = "8f8ddfde6c9fd54070517b1396c3f12a"


def disk_cache(f):
    cache_file = "cache/{}.pkl".format(f.__name__)

    def wrapper(*args, **kwargs):
        try:
            with open(cache_file, "rb") as fin:
                retr = pickle.load(fin)
        except FileNotFoundError:
            retr = f(*args, **kwargs)
            with open(cache_file, "wb") as fout:
                pickle.dump(retr, fout)
        return retr

    return wrapper


def retrieve_request_url(recipe_name):
    url = API_ENDPOINT + "app_id=" + API_ID + "&" + "app_key=" + API_KEY + "&q=" + recipe_name
    return url


def get_recipes(recipe_name: str) -> List[Dict[AnyStr, Dict[AnyStr, AnyStr]]]:
    global recipes_db
    try:
        return recipes_db[recipe_name]
    except KeyError:
        print("SKIPPING", recipe_name)
        recipes_db[recipe_name] = None
    return recipes_db[recipe_name]


class RecipeNotFoundError(Exception):
    pass


def get_recipe_ingredients(recipe_name):
    try:
        recipe_ingredients = ingredients_db[recipe_name]
    except KeyError:
        recipes = get_recipes(recipe_name)
        if not recipes:
            raise RecipeNotFoundError("recipe not found")

        recipe_ingredients = defaultdict(int)
        badwords = ['cup', 'gram', 'teaspoon', 'tablespoon', 'spoon', 'ounce', 'kg', 'g', 'tb', 'tsp', 'tbsp', 'x',
                    'pound', 'piece', 'oz']
        badwords.extend([b + "s" for b in badwords])
        badwords = set(badwords)

        all_ingredients = []
        for rj in recipes:
            for ingredient in rj['ingredients']:
                ingredient['weight'] /= rj['totalWeight'] * len(recipes)
                all_ingredients.append(ingredient)

        for entry in all_ingredients:
            text = entry['text'].lower()
            text = re.sub("\(([^()]+)\)", "", text)
            ingredients = []
            for sent_tree in nlp(text).sents:
                for word in sent_tree:
                    if word.pos_ == "NOUN" and word.text not in badwords:
                        text = re.sub("[^a-z\s]", "", word.text)
                        while "  " in text:
                            text = text.replace("  ", " ")
                        text = text.strip()
                        if len(text) > 1:
                            if text[-1] == "s":
                                text = text[:-1]
                            if text not in badwords:
                                ingredients.append(text)
            if ingredients:
                ingredients_str = (" ".join(ingredients)).strip()
                recipe_ingredients[ingredients_str] += entry['weight']
        recipe_ingredients = dict(recipe_ingredients)
        ingredients_db[recipe_name] = recipe_ingredients
    return recipe_ingredients


def query_knowledge(food_to_dim, dish_name):
    x = np.zeros(shape=(1, len(food_to_dim)), dtype=np.float32)
    ingredients = get_recipe_ingredients(dish_name)
    for ingredient, weight in ingredients.items():
        idx = food_to_dim[ingredient]
        x[0, idx] = weight
    return x


@disk_cache
def generate_lookup():
    idx = 0
    ridx = 0
    food_to_dim = {}
    recipe_to_dim = {}
    global recipes_db

    for recipe_name in list(recipes_db.keys()):
        print("generating", recipe_name, "lookup")
        try:
            recipe = get_recipe_ingredients(recipe_name)
        except RecipeNotFoundError:
            pass
        else:
            if recipe_name not in recipe_to_dim:
                recipe_to_dim[recipe_name] = ridx
                ridx += 1

            for ingredient, quantity in recipe.items():
                if ingredient not in food_to_dim:
                    food_to_dim[ingredient] = idx
                    idx += 1
    return food_to_dim, recipe_to_dim


def query_knowledge_thread(data):
    print("query: ", data[0])
    try:
        return query_knowledge(data[1], data[0])
    except RecipeNotFoundError:
        return np.array(False)


@disk_cache
def calculate_recipe_vectors(food_to_dim):
    global recipes_db
    thread_data = ((food_name, food_to_dim) for food_name in list(recipes_db.keys()))
    # with mp.Pool() as pool:
    # X = pool.map(query_knowledge_thread, thread_data)
    X = map(query_knowledge_thread, thread_data)
    X = [xi for xi in X if xi.any()]
    X = np.vstack(X)
    return X


# 5706 normalizer
def main():
    print("lookup")
    food_to_dim, recipe_to_dim = generate_lookup()
    print("calc vectors")
    X = calculate_recipe_vectors(food_to_dim)

    print("build tree")
    tree = NearestNeighbors(n_neighbors=5, algorithm='ball_tree', metric="euclidean").fit(X)

    for food_name in list(recipes_db.keys())[:10]:
        print_similar_foods(food_to_dim, recipe_to_dim, tree, food_name)

    print_similar_foods(food_to_dim, recipe_to_dim, tree, "pizza")
    print_similar_foods(food_to_dim, recipe_to_dim, tree, "valentina")


def print_similar_foods(food_to_dim, recipe_to_dim, model, food_name):
    try:
        X_full = query_knowledge(food_to_dim, food_name)
    except RecipeNotFoundError:
        print(food_name, "found no recipe")
    else:
        print("foods most similar to:", food_name, "recipe:")
        ingredients = get_recipe_ingredients(food_name)
        print([(name, int(weight * 100)) for name, weight in sorted(ingredients.items(), key=lambda x: -x[1]) if
               weight > 0.01])
        print("-" * 30)

        # indices = model.ann(X_full, 5, votes_required=4)
        distances, indices = model.kneighbors(X_full)
        for distance, idx in zip(distances[0], indices[0]):
            similar_recipe_name = [k for k in recipe_to_dim if recipe_to_dim[k] == idx][0]
            ingredients = get_recipe_ingredients(similar_recipe_name)
            print(similar_recipe_name, int(distance * 100),
                  [(name, int(weight * 100)) for name, weight in sorted(ingredients.items(), key=lambda x: -x[1]) if
                   weight > 0.01])


if __name__ == "__main__":
    recipes_db = sqliteshelve.open("cache/recipes.sqlite")
    ingredients_db = sqliteshelve.open("cache/ingredients.sqlite")
    try:
        main()
    finally:
        recipes_db.close()
        ingredients_db.close()
