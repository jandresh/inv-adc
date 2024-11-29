from flask import (
    abort,
    Flask,
    request,
    Response,
)
from flask_cors import (
    CORS,
)
import json
import pymongo
import re
import requests

app = Flask(__name__)
CORS(app)


def object_to_response(object):
    response = Response(
        response=json.dumps(object, default=str), mimetype="application/json"
    )
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response


@app.route("/")
def root():
    return """db endpoints:
/
/mongo-db-create    POST\n
/mongo-db-list      GET\n
/mongo-db-delete    POST\n
/mongo-coll-create  POST\n
/mongo-coll-list    POST\n
/mongo-coll-delete  POST\n
/mongo-doc-insert   POST\n
/mongo-doc-list     POST\n
/mongo-doc-delete   POST\n
/mongo-doc-find     POST\n
/mongo-doc-distinct POST\n
/mongo-doc-update   POST\n
/pipeline1          GET\n
/pipeline2          GET
"""


# *****mongo_db_create()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali"}' http://localhost:5001/mongo-db-create


@app.route("/mongo-db-create", methods=["POST"])
def mongo_db_create():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json["db_name"]
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        client[db_name]
    except:
        success = 1

    return object_to_response([{"exit": success}])


# *****mongo_db_list()******
# Este metodo es invocado de esta forma:
# curl http://localhost:5001/mongo-db-list


@app.route("/mongo-db-list", methods=["GET"])
def mongo_db_list():
    client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")

    return object_to_response([{"databases": list(client.list_database_names())}])


# *****mongo_db_delete()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali"}' http://localhost:5001/mongo-db-delete


@app.route("/mongo-db-delete", methods=["POST"])
def mongo_db_delete():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json["db_name"]
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        client.drop_database(db_name)
    except:
        success = 1

    return object_to_response([{"exit": success}])


# *****mongo_coll_create()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali", "coll_name" : "Breast"}' http://localhost:5001/mongo-coll-create


@app.route("/mongo-coll-create", methods=["POST"])
def mongo_coll_create():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json["db_name"]
        coll_name = request.json["coll_name"]
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        db = client[db_name]
        collection = db[coll_name]
    except:
        success = 1

    return object_to_response([{"exit": success}])


# *****mongo_coll_list()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali"}' http://localhost:5001/mongo-coll-list


@app.route("/mongo-coll-list", methods=["POST"])
def mongo_coll_list():
    if not request.json:
        abort(400)
    client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
    db_name = request.json["db_name"]
    db = client[db_name]
    return object_to_response([{"collections": db.list_collection_names()}])


# *****mongo_coll_delete()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali", "coll_name" : "Breast"}' http://localhost:5001/mongo-coll-delete


@app.route("/mongo-coll-delete", methods=["POST"])
def mongo_coll_delete():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json["db_name"]
        coll_name = request.json["coll_name"]
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        db = client[db_name]
        collection = db[coll_name]
        collection.drop()
    except:
        success = 1
    return object_to_response([{"exit": success}])


# *****mongo_doc_insert()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali", "coll_name" : "Breast", "document" : {"doc_id" : "123456", "doc_name" : "Breast cancer history"}}' http://localhost:5001/mongo-doc-insert
# {"db_name": "users", "coll_name": "adc_cali", "document": {"name": "Jaime Hurtado", "email": "jandresh@gmail.com", "password": "Univalle#2004822"}}


@app.route("/mongo-doc-insert", methods=["POST"])
def mongo_doc_insert():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json["db_name"]
        coll_name = request.json["coll_name"]
        document = request.json["document"]
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        db = client[db_name]
        collection = db[coll_name]
        collection.insert_one(document)
    except:
        success = 1
    return object_to_response([{"exit": success}])


# *****mongo_doc_update()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali", "coll_name" : "Breast", "document" : {"doc_id" : "123456", "doc_name" : "Breast cancer history"}}' http://localhost:5001/mongo-doc-insert
# curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali", "coll_name" : "Breast3", "filter": {"author": "jandresh@correounivalle.edu.co"}, "document" : {"related" : {"$each": ["jandresh@gmail.com", "jhurtado@fluidattacks.com", "jaime.hurtado@coreunivalle.edu.co"]}}, "add_to_set": true}' http://localhost:5001/mongo-doc-update


@app.route("/mongo-doc-update", methods=["POST"])
def mongo_doc_update():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json["db_name"]
        coll_name = request.json["coll_name"]
        filter_ = request.json["filter"]
        document = request.json["document"]
        add_to_set = (
            request.json["add_to_set"] if "add_to_set" in request.json else False
        )
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        db = client[db_name]
        collection = db[coll_name]
        if add_to_set:
            collection.update_one(filter_, {"$addToSet": document}, True)
        else:
            collection.update_one(filter_, {"$set": document}, True)
    except:
        success = 1
    return object_to_response([{"exit": success}])


# *****mongo_doc_list()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali", "coll_name" : "Breast"}' http://localhost:5001/mongo-doc-list


@app.route("/mongo-doc-list", methods=["POST"])
def mongo_doc_list():
    if not request.json:
        abort(400)

    db_name = request.json["db_name"]
    coll_name = request.json["coll_name"]
    client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
    db = client[db_name]
    collection = db[coll_name]
    data = []
    for doc in collection.find():
        doc["_id"] = str(doc["_id"])
        data.append(doc)
    return object_to_response(data)


# *****mongo_doc_delete()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali", "coll_name" : "Breast", "query" : {"doc_name" : "Breast cancer history"}}' http://localhost:5001/mongo-doc-delete


@app.route("/mongo-doc-delete", methods=["POST"])
def mongo_doc_delete():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json["db_name"]
        coll_name = request.json["coll_name"]
        query = request.json["query"]
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        db = client[db_name]
        collection = db[coll_name]
        collection.delete_one(query)
    except:
        success = 1
    return object_to_response([{"exit": success}])


# *****mongo_doc_find()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali", "coll_name" : "Breast", "query" : {"doc_name" : "Breast cancer history"}, "projection" : {}}' http://localhost:5001/mongo-doc-find


@app.route("/mongo-doc-find", methods=["POST"])
def mongo_doc_find():
    if not request.json:
        abort(400)
    try:
        db_name = request.json["db_name"]
        coll_name = request.json["coll_name"]
        query = request.json["query"]
        projection = request.json.get("projection")
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        db = client[db_name]
        collection = db[coll_name]
        out = collection.find(query, projection)
    except:
        out = None
    data = []
    for doc in out:
        doc["_id"] = str(doc["_id"])
        data.append(doc)
    return object_to_response(data)


# *****mongo_doc_distinct()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali", "coll_name" : "author_vs_doc_id2", "field" : "author", "query" : {}, "options" : {}}' http://localhost:5001/mongo-doc-distinct | jq


@app.route("/mongo-doc-distinct", methods=["POST"])
def mongo_doc_distinct():
    if not request.json:
        abort(400)
    db_name = request.json["db_name"]
    coll_name = request.json["coll_name"]
    field = request.json["field"]
    query = request.json["query"]
    client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
    db = client[db_name]
    collection = db[coll_name]
    out = collection.distinct(field, query)
    return object_to_response([{"result": out}])
