import csv
from datetime import (
    datetime,
)
from flask import (
    Flask,
    jsonify,
    request,
    Response,
)
from flask_cors import (
    CORS,
)
import json
from langdetect import (
    detect,
)
import requests
import sys
import time

app = Flask(__name__)
CORS(app)

apikey = "JAnjvcE7LDiB0aHeh8ruR3gUGFVW6qSI"


def post_json_request(url, obj):
    try:
        response = requests.post(url, json=obj).json()
    except:
        print(f"Error: Can't process the request to {url}", flush=True)
        response = {}
    return response

def object_to_response(object):
    response = Response(
        response=json.dumps(object), mimetype="application/json"
    )
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response


def query_api(search_url, query, scrollId=None):
    result_flag = 0
    while result_flag < 5:
        print(f"result_flag: {result_flag}", flush=True)
        try:
            headers = {"Authorization": "Bearer " + apikey}
            if not scrollId:
                response = requests.get(
                    f"{search_url}?q={query}&limit=100&scroll=true",
                    headers=headers,
                )
            else:
                response = requests.get(
                    f"{search_url}?q={query}&limit=100&scrollId={scrollId}",
                    headers=headers,
                )
            print(
                f"response: {str(response)}, query: {query}, scrollId: {scrollId}",
                flush=True
            )
        except:
            print("Control Point 1", flush=True)
            print("Post request fail, trying again ...", flush=True)
            time.sleep(3)
            response = None
        if response is not None:
            success = False
            if str(response) == "<Response [200]>":
                print("Control Point 2", flush=True)
                success = True
                try:
                    result = response.json()
                    elapsed = response.elapsed.total_seconds()
                except:
                    print("Control Point 3", flush=True)
                    success = False
            elif str(response) == "<Response [429]>":
                time.sleep(300)
            if success:
                print("Control Point 4", flush=True)
                return result, elapsed
        print("Control Point 6", flush=True)
        result_flag += 1
    print("Control Point 7", flush=True)
    return None, None


def scroll(search_url, query, extract_info_callback):
    allresults = []
    count = 0
    scrollId = None
    while True:
        result, elapsed = query_api(search_url, query, scrollId)
        scrollId = result["scrollId"]
        totalhits = result["totalHits"]
        result_size = len(result["results"])
        if result_size == 0:
            break
        for hit in result["results"]:
            if extract_info_callback:
                allresults.append(extract_info_callback(hit))
            else:
                allresults.append(extract_info(hit))
        count += result_size
        print(f"{count}/{totalhits} {elapsed}s", flush=True)
    return allresults


def scroll2(search_url, query, ptid):
    count = 0
    spanish_count = 0
    scrollId = None
    while True:
        with open("program_out.csv", mode="a") as file:
            writer = csv.writer(
                file, delimiter=";", quotechar="'", quoting=csv.QUOTE_ALL
            )
            result = True
            try:
                result, elapsed = query_api(search_url, query, scrollId)
                time.sleep(2)
                print(f'scrollId : {result["scrollId"]}', flush=True)
                if result is None:
                    print("Control Point 8", flush=True)
                    break
            except:
                print("Control Point 9", flush=True)
                result = None
            if result is not None:
                scrollId = result["scrollId"]
                totalhits = result["totalHits"]
                result_size = len(result["results"])
                if result_size == 0:
                    print("Control Point 10", flush=True)
                    break
                file_name = f"{int((ptid + 1) / 2)}.csv"
                with open(file_name, mode="a") as file2:
                    writer2 = csv.writer(
                        file2,
                        delimiter=";",
                        quotechar="'",
                        quoting=csv.QUOTE_ALL,
                    )
                    for item in result["results"]:
                        if item["title"] == None:
                            item["title"] = ""
                        try:
                            esp_detect_title = (
                                detect(item["title"].lower()) == "es"
                            )
                        except:
                            esp_detect_title = False
                        if item["abstract"] == None:
                            item["abstract"] = ""
                        try:
                            esp_detect_abstract = (
                                detect(item["abstract"].lower()) == "es"
                            )
                        except:
                            esp_detect_abstract = False
                        if item["fullText"] == None:
                            item["fullText"] = ""
                        try:
                            esp_detect_fullText = (
                                detect(item["fullText"].lower()) == "es"
                            )
                        except:
                            esp_detect_fullText = False
                        if (
                            esp_detect_title
                            or esp_detect_abstract
                            or esp_detect_fullText
                        ):
                            print("Control Point 11", flush=True)
                            writer2.writerow(
                                [
                                    int((ptid + 1) / 2),
                                    item["id"],
                                    item["downloadUrl"],
                                    item["title"].replace("'", ""),
                                    item["abstract"].replace("'", ""),
                                    item["fullText"].replace("'", ""),
                                ]
                            )
                            spanish_count += 1
                        print(
                            "PatternId:",
                            int((ptid + 1) / 2),
                            "SpanishCount:",
                            spanish_count,
                            flush=True
                        )
                    count += result_size
                    print(f"{count}/{totalhits} {elapsed}s", flush=True)
                    writer.writerow(
                        [
                            datetime.now(),
                            "PatternId: {}, spanishCount: {}, {}/{}".format(
                                int((ptid + 1) / 2),
                                spanish_count,
                                count,
                                totalhits,
                            ),
                        ]
                    )
                    file2.close()
                    print("Control Point 12")
                    if spanish_count > 12000 or count == totalhits:
                        print("Control Point 13")
                        break
            else:
                print("Control Point 14")
                file.close()
                break
            print("Control Point 15", flush=True)
            file.close()
    print("Control Point 16", flush=True)
    return spanish_count


def format_pubmed_author(author: str):
    formatted_author = author.split(",")
    if len(formatted_author) > 2:
        authors = []
        for nested_author in formatted_author:
            author_name = nested_author.split(" ")
            if len(author_name) > 1:
                authors.append(
                    author_name[-1]
                    + f"""{''.join(list(map(
                        lambda name: name[0] if len(name) > 0 else '',
                        author_name[0:-2])))}"""
                )
        return authors
    if len(formatted_author) == 2:
        return (
            f"{formatted_author[0]} "
            + f"""{''.join(list(map(
                lambda name: name[0] if len(name) > 0 else '',
                formatted_author[1].split(' '))))}"""
        )
    if len(formatted_author) == 1:
        spaced_author = list(
            filter(lambda item: len(item) > 0, formatted_author[0].split(" "))
        )
        if len(spaced_author) > 1:
            return (
                spaced_author[-1]
                + f""" {''.join(list(map(
                lambda name: name[0] if len(name) > 0 else '',
                spaced_author[0:-2])))}"""
            )

    return ""


def standardize_authors(authors):
    standardized_authors = list(
        filter(
            lambda item: item != "",
            map(
                lambda author: format_pubmed_author(author.get("name", "")),
                authors,
            ),
        )
    )
    if (
        len(standardized_authors) == 1
        and type(standardized_authors[0]) == "list"
    ):
        return list(
            filter(
                lambda item: item != "",
                map(
                    lambda author: format_pubmed_author(
                        author.get("name", "")
                    ),
                    standardized_authors[0],
                ),
            )
        )

    return standardized_authors


def iterator(search_url, query, patternid, database, project, maxdocs):
    count = 0
    spanish_count = 0
    scrollId = None
    while True:
        try:
            results, elapsed = query_api(search_url, query, scrollId)
            time.sleep(2)
            print(f'scrollId : {result["scrollId"]}', flush=True)
            if results is None:
                print("Control Point 8")
                break
        except:
            print("Control Point 9", flush=True)
            result = None
        if results is not None:
            scrollId = results["scrollId"]
            totalhits = results["totalHits"]
            result_size = len(results["results"])
            if result_size == 0:
                print("Control Point 10", flush=True)
                break
            for result in results["results"]:
                abstract = result.get("abstract", "")
                title = result.get("title", "")
                dbid = result.get("id", "")
                doi = result.get("doi", "")
                authors = standardize_authors(result.get("authors", ""))
                url = result.get("downloadUrl", "")
                year = result.get("publishedDate", "")
                full_text = post_json_request(
                        "http://preprocessing:5000/url2text", {"url": url}
                    ).get("url2text", "")
                emails = list(set(post_json_request(
                        "http://preprocessing:5000/text2emails", {"text": full_text}
                    ).get("emails", [])))
                if title is not None:
                    document = {
                        "pat_id": patternid,
                        "dbid": dbid,
                        "doi": doi,
                        "title": title,
                        "abstract": abstract,
                        "authors": authors,
                        "emails": emails,
                        "org": "",
                        "url": url,
                        "year": year,
                        "lang": post_json_request(
                                "http://preprocessing:5000/text2lang", {"text": full_text}
                            ).get("lang", ""),
                    }
                    post_json_request(
                        "http://db:5000/mongo-doc-update",
                        {
                            "db_name": database,
                            "coll_name": f"{project}_metadata_{patternid}",
                            "filter": {"title": title},
                            "document": document,
                        },
                    )
                    post_json_request(
                        "http://db:5000/mongo-doc-update",
                        {
                            "db_name": database,
                            "coll_name": f"{project}_metadata_global",
                            "filter": {"title": title},
                            "document": document,
                        },
                    )
                    for email in emails:
                        post_json_request(
                            "http://db:5000/mongo-doc-update",
                            {
                                "db_name": database,
                                "coll_name": f"{project}_author_vs_doc_id_{patternid}",
                                "filter": {"author": email},
                                "document": {
                                    "doc_id": dbid,
                                    "doi": doi,
                                },
                            },
                        )
                        post_json_request(
                            "http://db:5000/mongo-doc-update",
                            {
                                "db_name": database,
                                "coll_name": f"{project}_author_vs_doc_id_global",
                                "filter": {"author": email},
                                "document": {
                                    "doc_id": dbid,
                                    "doi": doi,
                                },
                            },
                        )
            count += result_size
            print(f"{count}/{totalhits} {elapsed}s", flush=True)
            print("Control Point 12", flush=True)
            if count > maxdocs or count == totalhits:
                print("Control Point 13", flush=True)
                break
        else:
            break
    return spanish_count


#
# Este metodo retorna informacion de microservicios disponibles
#


@app.route("/")
def root():
    return "core endpoints: /core, /core2, /query"


#
# *****query_core******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "carcinoma lobulillar de mama" }' http://localhost:5003/core | jq '.' | less
#


@app.route("/core", methods=["POST"])
def query_core():
    if not request.json:
        abort(400)
    result = None
    query = request.json["query"]
    search, seconds = query_api(
        f"https://api.core.ac.uk/v3/search/works", query
    )
    for key, value in search.items():
        if key == "results":
            result = value

    return jsonify(result)


#
# *****query_core******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "carcinoma lobulillar de mama", "idpattern": 1 }' http://localhost:5003/core | jq '.' | less
#


@app.route("/core2", methods=["POST"])
def query_core_scroll():
    if not request.json:
        abort(400)
    result = None
    query = request.json["query"]
    ptid = request.json["idpattern"]
    result = scroll2(f"https://api.core.ac.uk/v3/search/works", query, ptid)
    return jsonify(result=result)


#
# *****query******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "abstract:(breast AND carcinoma)", "patternid": 1, "maxdocs": 200, "database": "test4", "project": "adc-cali" }' http://localhost:5003/query
#


@app.route("/query", methods=["POST"])
def query():
    if not request.json:
        abort(400)
    result = None
    query = request.json["query"]
    ptid = request.json["patternid"]
    database = request.json["database"]
    project = request.json["project"]
    maxdocs = request.json["maxdocs"]
    result = iterator(
        f"https://api.core.ac.uk/v3/search/works",
        query,
        ptid,
        database,
        project,
        maxdocs,
    )
    return object_to_response({"exit": 0})
