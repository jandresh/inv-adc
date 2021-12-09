from flask import Flask, jsonify, request
import requests
import time
from langdetect import detect

app = Flask(__name__)
apikey = "JAnjvcE7LDiB0aHeh8ruR3gUGFVW6qSI"

def post_json_request(url, obj):
    return requests.post(url, json=obj).json()

def query_api(search_url, query, scrollId=None):
    headers = {"Authorization": "Bearer "+apikey}
    if not scrollId:
        response = requests.get(
            f"{search_url}?q={query}&limit=100&scroll=true", headers=headers)
    else:
        response = requests.get(
            f"{search_url}?q={query}&limit=100&scrollId={scrollId}", headers=headers)
    return response.json(), response.elapsed.total_seconds()

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
        print(f"{count}/{totalhits} {elapsed}s")
    return allresults

def scroll2(search_url, query, ptid):
    count = 0
    spanish_count = 0
    scrollId = None
    while True:
        result, elapsed = query_api(search_url, query, scrollId)
        scrollId = result["scrollId"]
        totalhits = result["totalHits"]
        result_size = len(result["results"])
        if result_size == 0:
            break
        for item in result["results"]:
            if item['title']==None:
                break
            if detect(item['title'].lower())=='es' :
                try:
                    insert=post_json_request(
                        'http://mysqlws:5000/search2mysql', 
                        {
                        "patternid" : ptid, 
                        "docid": item['id'], 
                        "title" : item['title'], 
                        "abstract" : item['abstract'], 
                        "fulltext" : item['fullText']
                        })
                    # if insert['result']=='0':
                    spanish_count+=1    
                except:
                    print('No inserted docid: ', item['id'])
            print('PatternId:', ptid, 'SpanishCout:', spanish_count) 
        count += result_size                       
        print(f"{count}/{totalhits} {elapsed}s")
    return spanish_count

#
# *****query_core******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "carcinoma lobulillar de mama" }' http://localhost:5003/core | jq '.' | less
#

@app.route("/core", methods=['POST'])
def query_core():
    if not request.json:
        abort(400)
    result = None
    query = request.json['query']
    search, seconds = query_api(
        f"https://api.core.ac.uk/v3/search/works", query)
    for key, value in search.items():
        if(key == 'results'):
            result = value
            # # print(key, ":", value)
            # for item in list(value):
            #     print('title : ', item['title'])
            #     print('Abstract :', item['abstract'])
    return jsonify(result)

#
# *****query_core******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "carcinoma lobulillar de mama", "idpattern": 1 }' http://localhost:5003/core | jq '.' | less
#


@app.route("/core2", methods=['POST'])
def query_core_scroll():
    if not request.json:
        abort(400)
    result = None
    query = request.json['query']
    ptid = request.json['idpattern']
    result = scroll2(
        f"https://api.core.ac.uk/v3/search/works", 
        query,
        ptid)
    return jsonify(result=result)
# Eliminar volumenes en docker
# sudo docker volume rm mysqlws_my-db
# sudo docker volume ls
