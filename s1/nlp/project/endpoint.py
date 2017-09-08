#!flask/bin/python
import pymongo
import flask

app = flask.Flask(__name__)
client = pymongo.MongoClient("tuamadre.net:80")
db = client['nlp_projectDB']


@app.route('/find', methods=['POST'])
def find():
    search_filter = flask.request.form.to_dict()
    if not search_filter:
        return flask.jsonify({'error': "go crash tommaso's server thanks"})
    results = db.knowledge_base.find(search_filter).limit(100)
    return flask.jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
