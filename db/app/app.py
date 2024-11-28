import csv
from flask import (
    abort,
    Flask,
    jsonify,
    request,
    Response,
)
from flask_cors import (
    CORS,
)
import json
import mysql.connector
import pymongo
import re
import requests

app = Flask(__name__)
CORS(app)

config = {
    "user": "adccali",
    "password": "adccali",
    "host": "mysql",
    "port": "3306",
    "database": "adccali",
}


def post_json_request(url, obj):
    return requests.post(url, json=obj).json()


def object_to_response(object):
    response = Response(
        response=json.dumps(object, default=str), mimetype="application/json"
    )
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response


def execute_mysql_query(query, connection):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        columns = cursor.description
        results = [
            {columns[index][0]: column for index, column in enumerate(value)}
            for value in cursor.fetchall()
        ]
    except Exception as e:
        print(str(e))
        results = [{"error": str(e)}]
    cursor.close()

    return results


def execute_mysql_query2(query, connection):
    result = 0
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        print(str(e))
        result = 1
    cursor.close()

    return result


def txt2text(path):
    with open(path, mode="r", encoding="utf-8") as f:
        text_str = f.read()
        f.close()

    return text_str


def str2eq(pattern, sentences_str):
    pattern = re.compile(pattern)
    match = ""
    sentences = []
    while match != None:
        match = pattern.search(sentences_str)
        if match != None:
            sentences.append(sentences_str[: match.start()].split())
            sentences_str = sentences_str[match.end() :]

    return sentences


@app.route("/")
def root():
    return """db endpoints:
/
/init               GET\n
/pattern2mysql      POST\n
/search2mysql       POST\n
/txt2patterns       GET\n
/patterns           GET\n
/searches           GET\n
/mysql-query        POST\n
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


# *****init()******
# Este metodo es invocado de esta forma:
# curl http://localhost:5001/init


@app.route("/init", methods=["GET"])
def init():
    connection = mysql.connector.connect(**config)
    error = execute_mysql_query2(
        """CREATE TABLE patterns (
                    id INT(10) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    patternid INT(10) NOT NULL,
                    pattern TEXT NOT NULL,
                    db TEXT NOT NULL,
                    description TEXT
                )""",
        connection,
    )
    error += execute_mysql_query2(
        """CREATE TABLE searches (
                    patid INT(10) NOT NULL,
                    docid INT(10) NOT NULL,
                    title TEXT,
                    abs TEXT,
                    ftext MEDIUMTEXT,
                    PRIMARY KEY (patid,docid)
                )""",
        connection,
    )
    if error:
        print("Error on tables creation")
    connection.close()

    return object_to_response([{"exit": error}])


# *****patten_insert()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "pattern": "Cancer de piel", "db": "PUBMED", "description": "Cancer muy comun"}' http://localhost:5001/pattern2mysql


@app.route("/pattern2mysql", methods=["POST"])
def pattern_insert():
    if not request.json:
        abort(400)
    connection = mysql.connector.connect(**config)
    pattern = request.json["pattern"]
    db = request.json["db"]
    description = request.json["description"]
    query = (
        'INSERT INTO patterns (pattern, db, description) VALUES ("%s", "%s", "%s");'
        % (pattern, db, description)
    )
    error = execute_mysql_query2(query, connection)
    result = [{"output": "Pattern can't be inserted"}]
    if not error:
        result = execute_mysql_query("SELECT * FROM patterns", connection)
    connection.close()

    return jsonify(result)


# *****search_insert()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "patternid": "1", "docid": "CORE", "title": "Test title", "abstract": "Abstract: This is a test", "fulltext": "Tele, abstract, body"}' http://localhost:5001/search2mysql


@app.route("/search2mysql", methods=["POST"])
def search_insert():
    if not request.json:
        abort(400)
    connection = mysql.connector.connect(**config)
    patternid = request.json["patternid"]
    docid = request.json["docid"]
    title = request.json["title"]
    abstract = request.json["abstract"]
    fulltext = request.json["fulltext"]
    file_name = "{}.csv".format(patternid)
    try:
        with open(file_name, mode="a") as file:
            writer = csv.writer(
                file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            writer.writerow(
                [
                    patternid,
                    docid,
                    " ".join(
                        map(
                            str,
                            re.findall("[a-zA-Z]\w+[.,;:]*", title.capitalize()),
                        )
                    ),
                    " ".join(
                        map(
                            str,
                            re.findall("[a-zA-Z]\w+[.,;:]*", abstract.capitalize()),
                        )
                    ),
                    " ".join(
                        map(
                            str,
                            re.findall("[a-zA-Z]\w+[.,;:]*", fulltext.capitalize()),
                        )
                    ),
                ]
            )
            file.close()
        result = 0
    except:
        result = 1
    connection.close()

    return jsonify(result=result)


# *****txt_patterns_file_insert()******
# Este metodo es invocado de esta forma:
# curl http://<host>:5001/txt2patterns


@app.route("/txt2patterns", methods=["GET"])
def txt_patterns_file_insert():
    connection = mysql.connector.connect(**config)
    patterns_text = txt2text("patterns.txt")
    search_queries = str2eq(r"\n", patterns_text)
    error_count = 0
    patternid = 1
    for query_words in search_queries:
        pattern = ""
        for i in range(len(query_words)):
            if i == len(query_words) - 1:
                pattern += "abs:%s" % (query_words[i])
            else:
                pattern += "abs:%s AND " % (query_words[i])
        query = (
            'INSERT INTO patterns (patternid, pattern, db, description) VALUES (%d, "%s", "%s", "%s");'
            % (patternid, pattern, "ARXIV", "Corpus 1")
        )
        error_count += execute_mysql_query2(query, connection)
        pattern = "abstract:("
        for i in range(len(query_words)):
            if i == len(query_words) - 1:
                pattern += "%s)" % (query_words[i])
            else:
                pattern += "%s AND " % (query_words[i])
        query = (
            'INSERT INTO patterns (patternid, pattern, db, description) VALUES (%d, "%s", "%s", "%s");'
            % (patternid, pattern, "CORE", "Corpus 1")
        )
        error_count += execute_mysql_query2(query, connection)
        pattern = ""
        for i in range(len(query_words)):
            if i == len(query_words) - 1:
                pattern += "%s[Title/Abstract]" % (query_words[i])
            else:
                pattern += "%s[Title/Abstract] AND " % (query_words[i])
        query = (
            'INSERT INTO patterns (patternid, pattern, db, description) VALUES (%d, "%s", "%s", "%s");'
            % (patternid, pattern, "PUBMED", "Corpus 1")
        )
        error_count += execute_mysql_query2(query, connection)
        patternid += 1
    if not error_count:
        result = execute_mysql_query("SELECT * FROM patterns", connection)
    else:
        result = [{"error": "%i Patterns can't be inserted" % (error_count)}]
    connection.close()

    return object_to_response(result)


# *****patterns()******
# Este metodo es invocado de esta forma:
# curl http://<host>:5001/patterns


@app.route("/patterns", methods=["GET"])
def patterns():
    connection = mysql.connector.connect(**config)
    results = execute_mysql_query("SELECT * FROM patterns", connection)
    connection.close()

    return object_to_response(results)


# *****searches()******
# Este metodo es invocado de esta forma:
# curl http://<host>:5001/searches


@app.route("/searches", methods=["GET"])
def searches():
    connection = mysql.connector.connect(**config)
    results = execute_mysql_query("SELECT * FROM searches", connection)
    connection.close()

    return object_to_response(results)


# *****mysql-query()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"query" : "select * from searches"}' http://localhost:5001/mysql-query


@app.route("/mysql-query", methods=["POST"])
def mysql_query():
    if not request.json:
        abort(400)
    query = request.json["query"]
    connection = mysql.connector.connect(**config)
    results = execute_mysql_query(str(query), connection)
    connection.close()

    return object_to_response(results)


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
        insert_id = collection.insert_one(document)
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
