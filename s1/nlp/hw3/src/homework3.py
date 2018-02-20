import glob
import pickle
import gzip
import urllib
import xml.etree.ElementTree
import xml.etree.ElementTree as ET
from collections import defaultdict

import networkx
from GoogleScraper import scrape_with_config, GoogleSearchError
from SPARQLWrapper import SPARQLWrapper, JSON
from nltk import Tree

from src.howdoesittastelike import nlp as en_nlp, disk_cache

# wiki_path = "/mnt/netbook/home/obafedyrider/babelfied-wikipediaXML/"
wiki_path = "/media/awok/02bf03c5-0155-4f12-b5fb-623e6d27ab31/opt/babelfied-wikipediaXML/"

archives_path = "{}/*".format(wiki_path)
FOOD_OR_TOOL = """
PREFIX schema: <http://schema.org/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT ?x ?country ?article WHERE {
{?x wdt:P31 wd:Q39546.}
 UNION
{?x wdt:P31 wd:Q2095.}
?article schema:about ?x .
?article schema:inLanguage "en" .
?article schema:isPartOf <https://en.wikipedia.org/> .
}
LIMIT 200
"""

ANIMALS_SPARQL = """
PREFIX schema: <http://schema.org/>

SELECT DISTINCT ?x ?article WHERE {
  ?x wdt:P31 wd:Q16521.
  ?x wdt:P105 wd:Q68947.
  ?article schema:about ?x.
  ?article schema:inLanguage "en".
  ?article schema:isPartOf <https://en.wikipedia.org/>.
}
LIMIT 200
"""


def generate_interesting_archives(keyword):
    pages = google_wikipedia_pages(keyword)
    archives = pages[keyword]
    for archive_name in archives:
        try:
            yield get_archive_path(archive_name)
        except IndexError:
            print("COULD NOT DECODE", archive_name, "PATH")


@disk_cache
def get_archive_path(archive_name):
    normalized_name = archive_name.replace("_", "+")
    archive_glob = "{}/{}.xml.gz".format(archives_path, normalized_name)
    try:
        archive_path = glob.glob(archive_glob)[0]
    except IndexError:
        try:
            normalized_name = urllib.parse.quote_plus(archive_name.replace("_", " "))
            archive_glob = "{}/{}.xml.gz".format(archives_path, normalized_name)
            archive_path = glob.glob(archive_glob)[0]
        except IndexError as e:
            # print("[ERROR] lookup failed", archive_name)
            raise e
    return archive_path


@disk_cache
def google_wikipedia_pages(keyword):
    interesting_pages = defaultdict(set)
    config = {
        'scrape_method': 'http',
        'use_own_ip': 'True',
        'search_engines': 'google',
        # 'search_engines': 'duckduckgo',
        'num_pages_for_keyword': 10,
        'do_caching': 'True',
        'keyword': '"{}" site:https://en.wikipedia.org/ -title:Talk'.format(keyword),
    }
    try:
        scraper_search = scrape_with_config(config)
    except GoogleSearchError as e:
        print("ERROR:", e)
    else:
        # for search in sqlalchemy_session.query(ScraperSearch).all():
        for serp in scraper_search.serps:
            for link in serp.links:
                if link.link_type == 'results':
                    page = link.link.split("/")[-1]
                    page = page.split("&")[0]
                    interesting_pages[keyword].add(page)  # url parsing is hard
    return dict(interesting_pages)


def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_


def extract_paths(sent):
    print_tree(sent)
    graph = networkx.Graph()
    root = sent.root
    graph.add_node(root)
    frontier = list(root.children)
    for child in frontier:
        graph.add_node(child)
        graph.add_edge(root, child)

    while frontier:
        node = frontier.pop(0)

        children = list(node.children)
        frontier.extend(children)

        for child in children:
            graph.add_node(child)
            graph.add_edge(node, child)
    paths = networkx.shortest_path(graph)

    # Need to create a layout when doing
    # separate calls to draw nodes and edges
    # pos = networkx.spring_layout(graph)
    # networkx.draw_networkx_nodes(graph, pos, cmap=plt.get_cmap('jet'))
    # networkx.draw_networkx_edges(graph, pos, edgelist=graph.edges(), edge_color='r', arrows=True)

    # for src in list(paths.keys()):
    #     for dst in list(paths[src].keys()):
    #         paths[src][dst] = paths[src][dst][1:-1]
    #         if not paths[src][dst]:
    #             del paths[src][dst]
    return [paths[src][dst] for src in paths for dst in paths[src]]


def print_tree(root):
    _ = [to_nltk_tree(root).pretty_print()]


def build_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_


def fetch_wiki_xml(wikipedia_archive_path):
    article_path = wikipedia_archive_path[:-3]
    try:
        with open(article_path) as fin:
            xml_page = ET.parse(fin)
            # print("\t\t\treading", article_path)
    except (FileNotFoundError, xml.etree.ElementTree.ParseError):
        try:
            with gzip.open(wikipedia_archive_path) as fin:
                print("\t\t\tunzippping", wikipedia_archive_path)
                content = fin.read()
                xml_page = ET.ElementTree(ET.fromstring(content))
                with open(article_path, "wb") as fout:
                    fout.write(content)
        except (FileNotFoundError, xml.etree.ElementTree.ParseError) as e:
            print("SKIPPING", wikipedia_archive_path, e)
            raise e
            # with tarfile.open(
            #         "/media/awok/02bf03c5-0155-4f12-b5fb-623e6d27ab31/opt/babelfied-wikipediaXML.tar.gz") as tar:
            #     member = "/".join(article_path.split("/")[-3:])
            #     tar.extract(member=member, path=wikipedia_archive_path)
            # xml_page = fetch_wiki_xml(wikipedia_archive_path)
    return xml_page


# @disk_cache BROKEN!
def extract_sents(wikipedia_archive_path):
    bids = {}
    if ".txt" == wikipedia_archive_path[-4:]:
        with open(wikipedia_archive_path) as fin:
            doc = en_nlp(fin.read())
    else:
        try:
            xml_page = fetch_wiki_xml(wikipedia_archive_path)
        except FileNotFoundError:
            return [], {}
        annotations = xml_page.findall("annotations")[0]
        text_xml_node = xml_page.find('text')
        if text_xml_node.text is None:
            return [], {}
        doc = en_nlp(text_xml_node.text)
        for annotation in reversed(annotations):
            mention = annotation.find("mention").text
            start = int(annotation.find("anchorStart").text)
            end = int(annotation.find("anchorEnd").text)
            bid = annotation.find("babelNetID").text
            bids[mention] = bid
            span = doc[start:end]
            span.merge(bid=bid, mention=mention)
    return list(doc.sents), bids


def fitler_paths(paths, patterns):
    good_paths = []
    triples = []
    for path in paths:
        for pattern_words, pattern_poss in patterns:
            pattern_followed = False
            word, pos = pattern_words[0], pattern_poss[0]
            for path_pos, tok in enumerate(path):
                if word == str(tok) and tok.pos_ == pos:
                    pattern_start = path_pos
                    word_found = 1
                    for word, pos, tok in zip(pattern_words[1:], pattern_poss[1:], path[pattern_start + 1:]):
                        if word != str(tok) or pos != tok.pos_:
                            break
                        else:
                            word_found += 1
                    if word_found == len(pattern_words):
                        pattern_followed = True
                        break
            if pattern_followed and len(path) > len(pattern_words) + 1:
                pre = path[:pattern_start]
                pattern = path[pattern_start:pattern_start + len(pattern_words)]
                post = path[pattern_start + len(pattern_words):]

                pre_text = " ".join(map(str, pre))
                pattern_text = " ".join(map(str, pattern))
                post_text = " ".join(map(str, post))

                if len(pre) == 1 and pre[0].pos_ == "NOUN" and len(post) == 1 and post[0].pos_ == "NOUN":
                    triples.append((pre_text, pattern_text, post_text))
                    good_paths.append(path)
    return good_paths


def is_same(tok, required_tok):
    return (str(tok) == required_tok[0] or required_tok == "") and (
        tok.pos_ == required_tok[1] or required_tok[1] == "")


def extract_triples(root, pattern):
    # print_tree(root)
    passtrough = ["it", "that"]
    if pattern['self'][0] in ("confused"):
        passtrough.append("not")
    lefts = root.lefts
    if pattern['self'][0] in ("able", "similar"):
        lefts = ["it"]
    for left in (l for l in lefts if str(l).lower() in passtrough or l.pos_ in ("NOUN", "PROPN")):
        # if left.pos_ == "NOUN":
        # if pattern['lefts'] and is_same(left, pattern['lefts'][0]):
        for right in root.rights:
            if 'y' in pattern:
                y_pos = pattern['y']
            else:
                y_pos = ("NOUN", "PROPN")
            if pattern['rights'] and is_same(right, pattern['rights'][0]):
                for rightright in right.children:
                    if rightright.pos_ in y_pos:
                        # other = " ".join(map(str, rightright.subtree))
                        # other = str(rightright)
                        if str(left) == "not":
                            left = "it"
                        triple = [left, tuple([root, right]), rightright]
                        yield triple
            else:
                if right.pos_ in y_pos:
                    triple = [left, tuple([root]), right]
                    yield triple


def gather_wiki_links(results):
    paths = []
    for result in results["results"]["bindings"]:
        entity_id = result['article']["value"].split("/")[-1]
        entity_id = urllib.parse.unquote(entity_id)
        try:
            paths.append(get_archive_path(entity_id))
        except IndexError:
            pass
    return paths


def gather_patterns():
    patterns = {
        'confused': {
            'lefts': [],
            # 'self': ("confused", "VERB"),
            # 'rights': [("with", "")],
            'self': ("similar", ""),
            'rights': [("to", "")],
            'pages': gather_wiki_links(sparqlery(ANIMALS_SPARQL)),
        },
        'tastes': {
            'lefts': [],
            'self': ("tastes", "VERB"),
            'rights': [("like", "ADP")],
            'pages': generate_interesting_archives("tastes like")
        },
        'part': {
            'lefts': [],
            'self': ("has", "VERB"),
            'rights': [],
            'pages': gather_wiki_links(sparqlery(FOOD_OR_TOOL))
        },
        'activity': {
            'lefts': [],
            'self': ("able", ""),
            'rights': [],
            'y': ["VERB"],
            'pages': gather_wiki_links(sparqlery(ANIMALS_SPARQL))
        },
        'color': {
            'lefts': [],
            'self': ("color", ""),
            'rights': [("is"), ],
            'pages': gather_wiki_links(sparqlery(FOOD_OR_TOOL))
        }
    }
    return patterns


def walk_unzipped_wikipedia():
    for i in range(1, 667):
        archive_glob = "{}/{}.xml".format(archives_path.replace("*", str(i)), "*")
        for path in glob.glob(archive_glob):
            yield path + ".gz"


def walk_wikipedia():
    for i in range(1, 667):
        archive_glob = "{}/{}.xml.gz".format(archives_path.replace("*", str(i)), "*")
        for path in glob.glob(archive_glob):
            yield path


def defie(pattern_description, pages=walk_wikipedia()):
    gathered_triples = set()
    context = defaultdict(list)
    for wikipedia_archive_path in pages:
        sents, bids = extract_sents(wikipedia_archive_path)
        for sent in sents:
            roots = [root for root in sent if list(root.children)]
            for root in roots:
                if str(root) == pattern_description['self'][0]:
                    # print_tree(root)
                    triples = extract_triples(root, pattern_description)
                    for triple in triples:
                        for i, t in enumerate(triple):
                            if str(t).lower() in ("that", "it"):
                                page_name = wikipedia_archive_path.split("/")[-1].split(".")
                                page_name = "".join(p for p in page_name if p not in ("tar", "gz", "xml"))
                                triple[i] = page_name + ":WIKIPAGE"
                        for i, t in enumerate(triple):
                            if str(t) in bids:
                                triple[i] = str(triple[i]) + ":" + bids[str(t)]
                            elif not isinstance(t, tuple):
                                print("[???]", t)
                        x, r, y = triple
                        row = "{}, {}, {}".format(str(x), " ".join(map(str, r)), str(y))
                        gathered_triples.add(row)
                        context[row].append(str(sent))
    return gathered_triples, context


@disk_cache
def sparqlery(query):
    sparql = SPARQLWrapper('https://query.wikidata.org/sparql', returnFormat=JSON)
    sparql.setQuery(query)
    results = sparql.query().convert()
    return results


def main():
    # triples = {}
    patterns = gather_patterns()
    for pattern_id, pattern_description in patterns.items():
        try:
            raise FileNotFoundError()
            with open("results/" + pattern_id) as fin:
                tuples = fin.read()
            if not tuples or len(tuples.split("\n")) < 20:
                raise FileNotFoundError()
        except (FileNotFoundError,):
            print("[PARSING]", pattern_id)
            pages = pattern_description['pages']
            gathered_triples, context = defie(pattern_description, pages=pages)
            # triples[pattern_id] = gathered_triples
            with open("results/" + pattern_id, 'w') as fout:
                fout.write("\n".join(map(str, gathered_triples)) + "\n")
            with open("results/context_" + pattern_id, 'wb') as fout:
                pickle.dump(context, fout)
            print("[DONE]", pattern_id)


if __name__ == "__main__":
    main()
