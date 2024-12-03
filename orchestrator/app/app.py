import asyncio
import base64
from datetime import (
    datetime,
)
from enum import (
    Enum,
)
from flask import (
    abort,
    Flask,
    request,
    Response,
)
from flask_cors import (
    CORS,
)
import io


import json
import matplotlib.pyplot as plt
import networkx as nx
import requests
from wordcloud import (
    WordCloud,
)

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


async def async_post_json_request(url, obj):
    return await asyncio.to_thread(post_json_request, url, obj)


def get_json_orcid_request(name):
    url = "https://pub.sandbox.orcid.org/v3.0/expanded-search"
    headers = {
        "Accept": "application/json",
    }
    # params = (('q', f'{id_type}-self:{doc_id}'),)
    name = name.split()
    params = (("q", f"family-name:{name[0]}+AND+given-names:{name[1]}&start=0&ro=1"),)
    return requests.get(url, headers=headers, params=params).json()


def object_to_response(object):
    response = Response(response=json.dumps(object), mimetype="application/json")
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


# *****metadata_pipeline()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"organization" : "correounivalle", "project" : "BreastCancer"}' http://localhost:5004/metadata-pipeline


@app.route("/metadata-pipeline", methods=["POST"])
async def metadata_pipeline():
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
        executed_patterns: list[dict[str, str]] = post_json_request(
            "http://db:5000/mongo-coll-list",
            {"db_name": organization},
        )
    except Exception as ex:
        patterns = []
        pipeline_logger(
            PipelineType.METADATA,
            organization,
            project,
            pattern_id,
            0,
            PipelineStatus.ERROR,
            str(ex),
        )
        success = 1
    for index, pattern in enumerate(patterns):
        if (
            f"metadata#{project}#{pattern['_id']}"
            in executed_patterns[0]["collections"]
        ):
            print(
                f"Pattern {pattern['_id']}:{pattern['pattern']} already executed",
                flush=True,
            )
            continue
        try:
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
            urls = [db_url("PUBMED"), db_url("ARXIV"), db_url("CORE")]
            data = {
                "query": pattern["pattern"],
                "patternid": pattern["_id"],
                "maxdocs": int(project_info[0]["maxDocs"]) if project_info else 100,
                "organization": organization,
                "project": project,
            }
            tasks = [async_post_json_request(url, data) for url in urls]
            fill_metadata_results = await asyncio.gather(*tasks)
            print(f"fill_metadata: {fill_metadata_results}", flush=True)
            if fill_metadata_results and all(
                result[0].get("exit") == 0 for result in fill_metadata_results
            ):
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
# curl -X POST -H "Content-type: application/json" -d '{"organization" : "correounivalle", "project" : "BreastCancer", "pattern": "global", graph_type: "authors"}' http://localhost:5004/adjacency-pipeline


@app.route("/adjacency-pipeline", methods=["POST"])
def adjacency_pipeline():
    if not request.json:
        abort(400)
    success = 0
    nodes = 0
    edges = 0
    b64_image = "data:image/png;base64,"
    wordcloud_b64_image = "data:image/png;base64,"
    node_link_data = {}
    try:
        organization = request.json["organization"]
        project = request.json["project"]
        pattern = request.json["pattern"]
        graph_type = request.json["graph_type"]
        patterns: list[dict[str, str]] = post_json_request(
            "http://db:5000/mongo-doc-list",
            {"db_name": organization, "coll_name": f"patterns#{project}"},
        )
        singular = graph_type[:-1] if graph_type != "countries" else "country"
        if pattern == "global" or (
            patterns and pattern in [item["_id"] for item in patterns]
        ):
            pipeline_logger(
                PipelineType.ADJACENCY,
                organization,
                project,
                pattern,
                100,
                PipelineStatus.RUNNING,
                f"Processing pattern {pattern}",
            )
            items = post_json_request(
                "http://db:5000/mongo-doc-list",
                {
                    "db_name": organization,
                    "coll_name": f"{graph_type}#{project}#{pattern}",
                },
            )
            items_list = [
                f'{item[singular]} {" ".join(item["related"])}' for item in items
            ]
            G = nx.parse_adjlist(items_list, nodetype=str)
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
            b64_image = f"{b64_image}{base64.b64encode(image_bytes.read()).decode()}"
            node_link_data = nx.node_link_data(G)

            keyword_items = post_json_request(
                "http://db:5000/mongo-doc-list",
                {
                    "db_name": organization,
                    "coll_name": f"wordcloud#{project}#{pattern}",
                },
            )
            keyword_list = [item["keyword"] for item in keyword_items]
            text = " ".join(keyword_list)
            # mask = np.array(Image.open(path.join(d, "batman.jpg")))
            wc = WordCloud(
                background_color="black",
                max_words=3000,
                # mask=mask,
                max_font_size=30,
                min_font_size=0.1,
                random_state=42,
            )
            wc.generate(text)
            plt.figure(figsize=(30, 30))
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off")
            wordcloud_image_bytes = io.BytesIO()
            plt.savefig(
                wordcloud_image_bytes,
                bbox_inches="tight",
                format="jpg",
            )
            wordcloud_image_bytes.seek(0)
            wordcloud_b64_image = f"{wordcloud_b64_image}{base64.b64encode(wordcloud_image_bytes.read()).decode()}"
            if items:
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
    return object_to_response(
        [
            {
                "exit": success,
                "nodes": nodes,
                "edges": edges,
                "b64_image": b64_image,
                "node_link_data": node_link_data,
                "wordcloud_image": wordcloud_b64_image if wordcloud_b64_image else "",
            }
        ]
    )
