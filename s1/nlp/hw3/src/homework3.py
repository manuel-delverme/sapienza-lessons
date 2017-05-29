from nltk import Tree
import urllib
import networkx as nx
from GoogleScraper import scrape_with_config, GoogleSearchError
from GoogleScraper.database import ScraperSearch, SERP, Link
from collections import defaultdict
import nltk
import xml.etree.ElementTree as ET
import gzip
import glob
from src.howdoesittastelike import nlp as en_nlp

wiki_path = "/mnt/netbook/home/obafedyrider/babelfied-wikipediaXML/"

archives_path = "{}/*".format(wiki_path)

print(en_nlp("the cake is a lie"))


def generate_interesting_archives(verbs):
    pages = google_wikipedia_pages(verbs)
    for verb in verbs:
        archives = pages[verb]
        for archive_name in archives:
            normalized_name = archive_name.replace("_", "+")
            archive_glob = "{}/{}.xml.gz".format(archives_path, normalized_name)
            try:
                try:
                    archive_path = glob.glob(archive_glob)[0]
                except IndexError as e:
                    normalized_name = urllib.parse.quote_plus(archive_name.replace("_", " "))
                    archive_glob = "{}/{}.xml.gz".format(archives_path, normalized_name)
                    archive_path = glob.glob(archive_glob)[0]
            except Exception as e:
                print("ERROR", e)
                raise e
            yield archive_path


def google_wikipedia_pages(keywords):
    interesting_pages = defaultdict(list)
    config = {
        'SCRAPING': {
            'scrape_method': 'http',
            'use_own_ip': 'True',
            # 'keyword': 'Let\'s go bubbles!',
            'search_engines': 'google',
            'num_pages_for_keyword': 1
        },
        # 'SELENIUM': {
        #     'sel_browser': 'chrome',
        # },
        'GLOBAL': {
            'do_caching': 'True'
        }
    }

    for keyword in keywords:
        config['keyword'] = '"{}" site:https://en.wikipedia.org/ -title:Talk'.format(keyword)
        try:
            sqlalchemy_session = scrape_with_config(config)
        except GoogleSearchError as e:
            print("ERROR:", e)
        for search in sqlalchemy_session.query(ScraperSearch).all():
            for serp in search.serps:
                for link in serp.links:
                    if link.link_type == 'results':
                        interesting_pages[keyword].append(link.link.split("/")[-1])  # url parsing is hard
    return dict(interesting_pages)


def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_


def main():
    # global en_nlp
    verbs = ["tastes like"]
    for wikipedia_archive_path in generate_interesting_archives(verbs):
        print("unzippping", wikipedia_archive_path)
        with gzip.open(wikipedia_archive_path) as fin:
            xml_page = ET.parse(fin)
        print("parsing xml")
        annotations = xml_page.findall("annotations")[0]

        text_xml_node = xml_page.find('text')
        doc = en_nlp(text_xml_node.text.split("\n")[0])
        mergelist = {}
        print_tree(doc)
        len_sum = 0
        indices = [0]
        for idx, tok in enumerate(doc._py_tokens):
            len_sum += len(tok) + 1
            indices.append(len_sum)
        # for np in parsed_tree.noun_chunks:
        #     tok = np.merge(np.root.tag_, np.text, np.root.ent_type_)
        #     print_tree(parsed_tree)

        for annotation in annotations:
            mention = annotation.find("mention").text
            start = indices[int(annotation.find("anchorStart").text)]
            end = indices[int(annotation.find("anchorEnd").text)]
            bid = annotation.find("babelNetID").text
            print("merging", doc.text[start:end])
            tok = doc.merge(start, end, bid=bid, mention=mention)
            print_tree(doc)

        # sents = nltk.sent_tokenize(node.text.lower())
        for sent in doc.sents:
            for verb in verbs:
                if verb in sent.text.lower():
                    print("FOUND", verb, "IN", sent)
                    # print_tree(sent)
                    # _ = input()


def print_tree(doc):
    # for tok in doc:
    #     print(tok.text)
    _ = [to_nltk_tree(sent.root).pretty_print() for sent in doc.sents]
    # build_tree(sent)


def build_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_


# for np in doc.noun_chunks:
#     print(
#             "text,", np.text,
#             "root.text", np.root.text,
#             "root,dep_", np.root.dep_,
#             "root,head.text", np.root.head.text)
#     # I I nsubj like
#     # green eggs eggs dobj like
#     # ham ham conj eggs
if __name__ == "__main__":
    main()
