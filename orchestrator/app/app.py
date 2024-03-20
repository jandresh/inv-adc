import base64
from datetime import (
    datetime,
)
from enum import Enum
from flask import (
    Flask,
    abort,
    jsonify,
    request,
    Response,
)
from flask_cors import (
    CORS,
)
import json
import requests
import sys
import time
import networkx as nx
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
CORS(app)


class PipelineStatus(str, Enum):
    ERROR = "ERROR"
    FINISHED = "FINISHED"
    RUNNING = "RUNNING"
    STARTING = "STARTING"


class PipelineType(str, Enum):
    METADATA = "METADATA"
    ADJACENCY = "ADJACENCY"


def post_json_request(url, obj):
    return requests.post(url, json=obj).json()


def get_json_orcid_request(name):
    url = "https://pub.sandbox.orcid.org/v3.0/expanded-search"
    headers = {
        "Accept": "application/json",
    }
    # params = (('q', f'{id_type}-self:{doc_id}'),)
    name = name.split()
    params = (
        ("q", f"family-name:{name[0]}+AND+given-names:{name[1]}&start=0&ro=1"),
    )
    return requests.get(url, headers=headers, params=params).json()


def object_to_response(object):
    response = Response(
        response=json.dumps(object), mimetype="application/json"
    )
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response


def db_url(db):
    if db == "PUBMED":
        return "http://metapub:5000/query"
    elif db == "ARXIV":
        return "http://arxiv:5000/query"
    elif db == "CORE":
        return "http://core:5000/query"

    return ""


container = "orchestrator"


def create_logger(microservice):
    create_state_db = post_json_request(
        "http://db:5000/mongo-db-create", {"db_name": "app_state"}
    )
    create_state_coll = post_json_request(
        "http://db:5000/mongo-coll-create",
        {"db_name": "app_state", "coll_name": f"{container}_{microservice}"},
    )

    return create_state_db["exit"] == 0 and create_state_coll["exit"] == 0


def state_logger(microservice, state):
    return post_json_request(
        "http://db:5000/mongo-doc-insert",
        dict(
            db_name="app_state",
            coll_name=f"{container}_{microservice}",
            document=dict(datetime=datetime.now().isoformat(), state=state),
        ),
    )


def pipeline_logger(
    type: PipelineType,
    organization: str,
    project: str,
    actual_pattern: str,
    percent: int,
    status: PipelineStatus,
    message: str,
):
    post_json_request(
        "http://db:5000/mongo-doc-insert",
        dict(
            db_name=organization,
            coll_name=f"pipeline#{type.value.lower()}#{project}",
            document=dict(
                datetime=datetime.now().isoformat(),
                actual_pattern=actual_pattern,
                percent=percent,
                status=status,
                message=message,
            ),
        ),
    )


#
# Este metodo retorna informacion de microservicios disponibles
#


@app.route("/")
def root():
    return "orchestrator endpoints: /"


@app.route("/pipeline3", methods=["GET"])
def pipeline3():
    try:
        patterns_list = post_json_request(
            "http://db:5000/mysql-query", {"query": "select * from patterns"}
        )
    except:
        patterns_list = None
    create_metadata_db = post_json_request(
        "http://db:5000/mongo-db-create", {"db_name": "metadata"}
    )
    create_authors_db = post_json_request(
        "http://db:5000/mongo-db-create", {"db_name": "authors"}
    )
    actual_pattern = 1
    if (
        patterns_list is not None
        and create_metadata_db == 0
        and create_authors_db == 0
    ):
        for pattern in patterns_list:
            create_mongo_coll_metadata = post_json_request(
                "http://db:5000/mongo-coll-create",
                {
                    "db_name": "metadata",
                    "coll_name": f"metadata_{actual_pattern}",
                },
            )
            create_mongo_coll_author_vs_doc_id = post_json_request(
                "http://db:5000/mongo-coll-create",
                {
                    "db_name": "authors",
                    "coll_name": "author_vs_doc_id_{}".format(actual_pattern),
                },
            )
            if pattern["db"] == "PUBMED":
                try:
                    pmids_json = post_json_request(
                        "http://metapub:5000/pmids",
                        {"query": pattern["pattern"]},
                    )
                    pmids = pmids_json["pmids"]
                except:
                    pmids = None
                if pmids is not None:
                    for pmid in pmids:
                        if pmid is not None:
                            try:
                                metadata_json = post_json_request(
                                    "http://metapub:5000/metadata",
                                    {"id": "{}".format(pmid)},
                                )
                            except:
                                metadata_json = None
                            if metadata_json:
                                try:
                                    if metadata_json["abstract"] is not None:
                                        text = metadata_json["abstract"]
                                    elif metadata_json["title"] is not None:
                                        text = metadata_json["title"]
                                    else:
                                        text = ""
                                    lang_json = post_json_request(
                                        "http://preprocessing:5000/text2lang",
                                        {"text": text},
                                    )
                                except:
                                    lang_json["lang"] = ""
                            if metadata_json is not None:
                                success_doc_insert = 1
                                try:
                                    success_doc_insert = post_json_request(
                                        "http://db:5000/mongo-doc-insert",
                                        {
                                            "db_name": "metadata",
                                            "coll_name": f"metadata_{actual_pattern}",
                                            "document": {
                                                "pat_id": pattern["id"]
                                                if pattern["id"] is not None
                                                else "",
                                                "pmid": metadata_json["pmid"]
                                                if metadata_json["pmid"]
                                                is not None
                                                else "",
                                                "coreid": "",
                                                "doi": metadata_json["doi"]
                                                if metadata_json["doi"]
                                                is not None
                                                else "",
                                                "title": metadata_json["title"]
                                                if metadata_json["title"]
                                                is not None
                                                else "",
                                                "abstract": metadata_json[
                                                    "abstract"
                                                ]
                                                if metadata_json["abstract"]
                                                is not None
                                                else "",
                                                "authors": metadata_json[
                                                    "authors"
                                                ]
                                                if metadata_json["authors"]
                                                is not None
                                                else "",
                                                "org": "",
                                                "url": metadata_json["url"]
                                                if metadata_json["url"]
                                                is not None
                                                else "",
                                                "year": metadata_json["year"]
                                                if metadata_json["year"]
                                                is not None
                                                else "",
                                                "lang": lang_json["lang"]
                                                if lang_json["lang"]
                                                is not None
                                                else "",
                                            },
                                        },
                                    )
                                except:
                                    print(
                                        f"Exception on can't insert document for {pmid}"
                                    )
                                if success_doc_insert == 0:
                                    print(
                                        f"Inserted on mongo a doc for {pmid}"
                                    )
                                for author in list(metadata_json["authors"]):
                                    # try:
                                    #     # orcid = get_json_orcid_request(str(author))['expanded-result'][0]['orcid-id']
                                    #     orcid = ""
                                    # except:
                                    #     orcid = ""
                                    print(
                                        f"Inserted on mongo a doc for {author}"
                                    )
                                    sys.stdout.flush()
                                    success_author_insert = 1
                                    try:
                                        success_author_insert = post_json_request(
                                            "http://db:5000/mongo-doc-insert",
                                            {
                                                "db_name": "authors",
                                                "coll_name": f"author_vs_doc_id_{actual_pattern}",
                                                "document": {
                                                    "author": author,
                                                    "doc_id": metadata_json[
                                                        "pmid"
                                                    ]
                                                    if metadata_json["pmid"]
                                                    is not None
                                                    else "",
                                                    # "orcid" : orcid,
                                                    # Afiliacion y correo
                                                },
                                            },
                                        )
                                    except:
                                        success_author_insert = 1
            actual_pattern += 1
    return jsonify(patterns_list)


@app.route("/pipeline4", methods=["GET"])
def pipeline4():
    db_name = "network"
    create_network_db = post_json_request(
        "http://db:5000/mongo-db-create", {"db_name": db_name}
    )
    coll_list = post_json_request(
        "http://db:5000/mongo-coll-list", {"db_name": "authors"}
    )
    coll_name = "works_global"
    create_mongo_coll_metadata = post_json_request(
        "http://db:5000/mongo-coll-create",
        {
            "db_name": db_name,
            "coll_name": coll_name,
        },
    )
    author_list = post_json_request(
        "http://db:5000/mongo-doc-distinct",
        {
            "db_name": "authors",
            "coll_name": "author_vs_doc_id_global",
            "field": "author.name",
            "query": {},
        },
    )
    for author in author_list[0]["result"]:
        works_obj = post_json_request(
            "http://db:5000/mongo-doc-find",
            {
                "db_name": "authors",
                "coll_name": "author_vs_doc_id_global",
                "query": {"author.name": author},
                "projection": {"doc_id": 1},
            },
        )
        works = []
        for work in works_obj:
            works.append(str(work["doc_id"]))
        try:
            success_works_insert = post_json_request(
                "http://db:5000/mongo-doc-insert",
                {
                    "db_name": db_name,
                    "coll_name": coll_name,
                    "document": {
                        "author": author,
                        "works": works,
                    },
                },
            )
        except:
            print("error on works insert")
        print(f"Author: {author}, works: {works}")
    # for collection in coll_list['collections']:
    #     coll_name = f"works{collection.replace('author_vs_doc_id', '')}"
    #     create_mongo_coll_metadata = post_json_request(
    #         'http://db:5000/mongo-coll-create',
    #         {
    #             "db_name" : db_name,
    #             "coll_name" : coll_name,
    #         }
    #     )
    #     author_list = post_json_request(
    #         'http://db:5000/mongo-doc-distinct',
    #         {"db_name" : "authors", "coll_name" : collection, "field" : "author", "query" : {}, "options" : {}}
    #     )
    #     for author in author_list['result']:
    #         works_obj = post_json_request(
    #             'http://db:5000/mongo-doc-find',
    #             {"db_name" : "authors", "coll_name" : collection, "query" : {"author" : author}, "projection" : {"doc_id": 1}}
    #         )
    #         works = []
    #         for work in works_obj:
    #             works.append(str(work['doc_id']))
    #         try:
    #             success_works_insert = post_json_request(
    #                 'http://db:5000/mongo-doc-insert',
    #                 {
    #                     "db_name" : db_name,
    #                     "coll_name" : coll_name,
    #                     "document" : {
    #                         "author" : author,
    #                         "works" : works,
    #                     }
    #                 }
    #             )
    #         except:
    #             print("error on works insert")
    #         print(f"Author: {author}, works: {works}")
    return jsonify(author_list)


@app.route("/pipeline5", methods=["GET"])
def pipeline5():
    db_name = "network"
    create_network_db = post_json_request(
        "http://db:5000/mongo-db-create", {"db_name": db_name}
    )
    coll_list = post_json_request(
        "http://db:5000/mongo-coll-list", {"db_name": "authors"}
    )
    for collection in list(
        filter(
            lambda coll: coll.endswith("global"),
            list(coll_list[0]["collections"]),
        )
    ):
        coll_name = f"related{collection.replace('author_vs_doc_id', '')}"
        works_coll = f"works{collection.replace('author_vs_doc_id', '')}"
        print(f"coll name: {coll_name}, coll list: {works_coll}")
        create_mongo_coll_metadata = post_json_request(
            "http://db:5000/mongo-coll-create",
            {
                "db_name": db_name,
                "coll_name": coll_name,
            },
        )
        author_list = post_json_request(
            "http://db:5000/mongo-doc-distinct",
            {
                "db_name": "network",
                "coll_name": works_coll,
                "field": "author",
                "query": {},
            },
        )
        for author in author_list[0]["result"]:
            author_works = post_json_request(
                "http://db:5000/mongo-doc-find",
                {
                    "db_name": db_name,
                    "coll_name": works_coll,
                    "query": {"author": author},
                    "projection": {"works": 1},
                },
            )
            if author_works != []:
                for work in list(set(author_works[0]["works"])):
                    authors_related = post_json_request(
                        "http://db:5000/mongo-doc-find",
                        {
                            "db_name": db_name,
                            "coll_name": works_coll,
                            "query": {"works": work},
                            "projection": {"author": 1},
                        },
                    )
                    for author_related in authors_related:
                        try:
                            success_related_insert = post_json_request(
                                "http://db:5000/mongo-doc-insert",
                                {
                                    "db_name": db_name,
                                    "coll_name": coll_name,
                                    "document": {
                                        "author": author,
                                        "related": {
                                            "author": author_related["author"],
                                            "doc_id": work,
                                        },
                                    },
                                },
                            )
                        except:
                            print("error on related insert")
                        print(
                            f"a_author: {author}, b_author: {author_related['author']}, related_docs: {work}"
                        )
                    state_logger(
                        "pipeline_5",
                        dict(
                            stage=1,
                            description="related authors creation",
                            data=dict(author=author),
                        ),
                    )
    return jsonify(author_list)


@app.route("/pipeline6", methods=["GET"])
def pipeline6():
    db_name = "arrays"
    create_array_db = post_json_request(
        "http://db:5000/mongo-db-create", {"db_name": db_name}
    )
    coll_list = post_json_request(
        "http://db:5000/mongo-coll-list", {"db_name": "network"}
    )
    related_coll_list = list(
        filter(lambda x: x[0] == "r", coll_list["collections"])
    )
    for collection in related_coll_list:
        coll_name = f"authors{collection.replace('related', '')}"
        create_mongo_coll = post_json_request(
            "http://db:5000/mongo-coll-create",
            {
                "db_name": db_name,
                "coll_name": coll_name,
            },
        )
        data = post_json_request(
            "http://db:5000/mongo-doc-list",
            {"db_name": "network", "coll_name": collection},
        )
        author_list_json = post_json_request(
            "http://db:5000/mongo-doc-distinct",
            {
                "db_name": "authors",
                "coll_name": f"author_vs_doc_id{collection.replace('related', '')}",
                "field": "author",
                "query": {},
                "options": {},
            },
        )
        author_list = author_list_json["result"]
        author_number = len(author_list)
        sys.stdout.flush()
        print(f"AuthorNumber={author_number}")
        authors_array = [
            [0 for col in range(author_number)] for row in range(author_number)
        ]
        for i in range(author_number):
            for j in range(author_number):
                for doc in data:
                    if doc["author"] == author_list[i]:
                        if doc["related"]["author"] == author_list[j]:
                            authors_array[i][j] += 1
                            print(
                                f"author: {doc['author']}, related: {doc['related']['author']}, authors_array[{i}][{j}]={authors_array[i][j]}"
                            )
                            sys.stdout.flush()
        try:
            success_array_insert = post_json_request(
                "http://db:5000/mongo-doc-insert",
                {
                    "db_name": db_name,
                    "coll_name": coll_name,
                    "document": {
                        "authors_list": author_list,
                        "array": authors_array,
                    },
                },
            )
        except:
            print("error on array insert")
        print(f"Processed coll_name={coll_name}")
        state_logger(
            "pipeline_6",
            dict(
                stage=1,
                description="authors array creation",
                data=dict(coll_name=coll_name),
            ),
        )
    return jsonify(author_list)


@app.route("/pipeline7", methods=["GET"])
def pipeline7():
    maxdocs = 10000
    microservice_name = "pipeline7"
    while not create_logger(microservice_name):
        time.sleep(10)
        print("no db connection")
    state_logger(
        microservice_name,
        dict(
            stage=0,
            description="Pipeline 7 start",
            data=dict(pattern=0, success=False),
        ),
    )
    try:
        patterns_list = post_json_request(
            "http://db:5000/mysql-query", {"query": "select * from patterns"}
        )
    except:
        patterns_list = None
    create_metadata_db = post_json_request(
        "http://db:5000/mongo-db-create", {"db_name": "metadata"}
    )
    create_mongo_coll_metadata_global = post_json_request(
        "http://db:5000/mongo-coll-create",
        {"db_name": "metadata", "coll_name": f"metadata_global"},
    )
    create_authors_db = post_json_request(
        "http://db:5000/mongo-db-create", {"db_name": "authors"}
    )
    create_mongo_coll_author_vs_doc_id_global = post_json_request(
        "http://db:5000/mongo-coll-create",
        {"db_name": "authors", "coll_name": "author_vs_doc_id_global"},
    )
    errors = 0
    if (
        patterns_list is not None
        and create_metadata_db["exit"] == 0
        and create_mongo_coll_metadata_global["exit"] == 0
        and create_authors_db["exit"] == 0
        and create_mongo_coll_author_vs_doc_id_global["exit"] == 0
    ):
        state_logger(
            microservice_name,
            dict(
                stage=1,
                description="Pattern list received",
                data=dict(pattern=0, success=False),
            ),
        )
        for pattern in patterns_list:
            if pattern["db"] == "CORE" or pattern["db"] == "ARXIV":
                post_json_request(
                    "http://db:5000/mongo-coll-create",
                    {
                        "db_name": "metadata",
                        "coll_name": f"metadata_{pattern['patternid']}",
                    },
                )
                print(f"metadata_{pattern['patternid']}")
                post_json_request(
                    "http://db:5000/mongo-coll-create",
                    {
                        "db_name": "authors",
                        "coll_name": f"author_vs_doc_id_{pattern['patternid']}",
                    },
                )
                sys.stdout.flush()
                try:
                    result = post_json_request(
                        db_url(pattern["db"]),
                        {
                            "query": pattern["pattern"],
                            "patternid": pattern["patternid"],
                            "maxdocs": maxdocs,
                        },
                    )["exit"]
                except:
                    result = 1
                state_logger(
                    microservice_name,
                    dict(
                        stage=2,
                        description="metadata creation",
                        data=dict(
                            pattern=pattern["patternid"], success=result == 0
                        ),
                    ),
                )
                errors += result

    return object_to_response({"errors": errors})


# *****metadata_pipeline()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"organization" : "correounivalle", "project" : "BreastCancer"}' http://localhost:5004/metadata-pipeline


@app.route("/metadata-pipeline", methods=["POST"])
def metadata_pipeline():
    if not request.json:
        abort(400)
    success = 0
    pattern_id, pattern_index = ("", 0)
    try:
        organization = request.json["organization"]
        project = request.json["project"]
        project_info = post_json_request(
            "http://db:5000/mongo-doc-find",
            {
                "db_name": organization,
                "coll_name": "projects",
                "query": {"name": project},
                "projection": {"maxDocs": 1},
            },
        )
        patterns = post_json_request(
            "http://db:5000/mongo-doc-list",
            {"db_name": organization, "coll_name": f"patterns#{project}"},
        )
        for index, pattern in enumerate(patterns):
            pattern_id, pattern_index = (pattern["_id"], index)
            pipeline_logger(
                PipelineType.METADATA,
                organization,
                project,
                pattern_id,
                int(pattern_index / len(patterns) * 100),
                PipelineStatus.RUNNING,
                f"Processing pattern {pattern['pattern']}",
            )
            fill_metadata_result = post_json_request(
                db_url("CORE"),
                {
                    "query": pattern["pattern"],
                    "patternid": pattern["_id"],
                    "maxdocs": int(project_info[0]["maxDocs"])
                    if project_info
                    else 100,
                    "organization": organization,
                    "project": project,
                },
            )
            print(f"fill_metadata: {fill_metadata_result}", flush=True)
            if fill_metadata_result and fill_metadata_result["exit"] == 0:
                pipeline_logger(
                    PipelineType.METADATA,
                    organization,
                    project,
                    pattern_id,
                    int(pattern_index / len(patterns) * 100),
                    PipelineStatus.RUNNING,
                    f"Processed pattern {pattern['pattern']}",
                )
            else:
                pipeline_logger(
                    PipelineType.METADATA,
                    organization,
                    project,
                    pattern_id,
                    int(pattern_index / len(patterns) * 100),
                    PipelineStatus.ERROR,
                    f"Error in Processing pattern {pattern['pattern']}",
                )

    except Exception as ex:
        pipeline_logger(
            PipelineType.METADATA,
            organization,
            project,
            pattern_id,
            int(pattern_index / len(patterns) * 100),
            PipelineStatus.ERROR,
            str(ex),
        )
        success = 1
    return object_to_response([{"exit": success}])


# *****adjacency_pipeline()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"organization" : "correounivalle", "project" : "BreastCancer", "pattern": "global"}' http://localhost:5004/adjacency-pipeline


@app.route("/adjacency-pipeline", methods=["POST"])
def adjacency_pipeline():
    if not request.json:
        abort(400)
    success = 0
    nodes = 0
    edges = 0
    b64_image = ""
    node_link_data = {}
    try:
        organization = request.json["organization"]
        project = request.json["project"]
        pattern = request.json["pattern"]
        patterns: list[dict[str, str]] = post_json_request(
            "http://db:5000/mongo-doc-list",
            {"db_name": organization, "coll_name": f"patterns#{project}"},
        )
        print(f"patterns: {patterns}, {type(patterns)}", flush=True)
        if pattern == "global" or (patterns and pattern in [item["_id"] for item in patterns]):
            pipeline_logger(
                PipelineType.ADJACENCY,
                organization,
                project,
                pattern,
                100,
                PipelineStatus.RUNNING,
                f"Processing pattern {pattern}",
            )
            authors = post_json_request(
                "http://db:5000/mongo-doc-list",
                {
                    "db_name": organization,
                    "coll_name": f"authors#{project}#{pattern}",
                },
            )
            authors_list = [
                f'{author["author"]} {" ".join(author["related"])}'
                for author in authors
            ]
            G = nx.parse_adjlist(authors_list, nodetype=str)
            plt.figure(figsize=(30, 30))
            nx.draw(
                G,
                with_labels=True,
                node_color="skyblue",
                node_size=100,
                font_size=10,
                style="solid",
            )
            nodes = G.number_of_nodes()
            edges = G.number_of_edges()
            image_bytes = io.BytesIO()
            plt.savefig(image_bytes, format="jpg")
            image_bytes.seek(0)
            b64_image = f"data:image/png;base64,{base64.b64encode(image_bytes.read()).decode()}"
            node_link_data = nx.node_link_data(G)
            if authors:
                pipeline_logger(
                    PipelineType.ADJACENCY,
                    organization,
                    project,
                    pattern,
                    100,
                    PipelineStatus.RUNNING,
                    f"Processed pattern {pattern}\nnodes: {nodes}\nedges:{edges}",
                )
            else:
                pipeline_logger(
                    PipelineType.ADJACENCY,
                    organization,
                    project,
                    pattern,
                    100,
                    PipelineStatus.ERROR,
                    f"Error in Processing pattern {pattern}",
                )

    except Exception as ex:
        pipeline_logger(
            PipelineType.ADJACENCY,
            organization,
            project,
            pattern,
            100,
            PipelineStatus.ERROR,
            str(ex),
        )
        success = 1
    return object_to_response([{"exit": success, "nodes": nodes, "edges": edges, "b64_image": b64_image, "node_link_data": node_link_data }])
