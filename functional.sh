#! /bin/bash

http_response_get(){
    response=$(curl --silent --write-out "HTTPSTATUS:%{http_code}" $1)
    body=$(echo "$response" | sed -e 's/HTTPSTATUS\:.*//g')
    status_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

    echo "Site $1 status response is $status_code"
    echo "Response body: $body"

    if [ "$status_code" -eq 403 ] || [ "$status_code" -eq 404 ] || [ "$status_code" -eq 500 ] || [ "$status_code" -eq 503 ] || [ "$status_code" -eq 504 ] ; then
        exit 1
    fi

    if ! echo "$body" | grep -q "$2" ; then
        echo "Error: Expected text '$2' not found in response from $1"
        exit 1
    fi
}

http_response_post(){
    response=$(curl -X POST -H "Content-type: application/json" -d "$1" $2 --silent --write-out "HTTPSTATUS:%{http_code}")
    body=$(echo "$response" | sed -e 's/HTTPSTATUS\:.*//g')
    status_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

    echo "Site $2 status response is $status_code"
    echo "Response body: $body"

    if [ "$status_code" -eq 403 ] || [ "$status_code" -eq 404 ] || [ "$status_code" -eq 500 ] || [ "$status_code" -eq 503 ] || [ "$status_code" -eq 504 ] ; then
        exit 1
    fi

    if ! echo "$body" | grep -q "$3" ; then
        echo "Error: Expected text '$3' not found in response from $2"
        exit 1
    fi
}

# arxiv tests
http_response_get http://localhost:5005 "/arxiv, /query"
http_response_post '{ "query": "breast cancer" }' http://localhost:5005/arxiv "breast cancer"

# core tests
http_response_get http://localhost:5003 "/core, /core2, /query"
http_response_post '{ "query": "breast cancer" }' http://localhost:5003/core "breast cancer"
http_response_post '{ "query": "breast cancer" }' http://localhost:5003/core2 "breast cancer"

# metapub tests
http_response_get http://localhost:5000 "/title, /abstract, /pmids, /metadata, /pmid2pdf, /query"
http_response_post '{ "id": "2020202" }' http://localhost:5000/title "The structure of the OARS physical health measures."
http_response_post '{ "id": "2020202" }' http://localhost:5000/abstract "This article proposes and evaluates two models for integrating self-reported health status"
http_response_post '{ "query": "breast cancer" }' http://localhost:5000/pmids '"39'
http_response_post '{ "id": "2020202" }' http://localhost:5000/metadata "10.1097/00005650-199104000-00003"
http_response_post '{ "id": "32599772"}' http://localhost:5000/pmid2pdf "http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC7350007&blobtype=pdf"

# preprocessing test
http_response_get http://localhost:5002 "/, /url2text, /url2htext, /text2locations, /text2places, /text2ner, /text2emails, /text2lang, /text2keywords"
http_response_post '{ "url": "http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC7350007&blobtype=pdf"}' http://localhost:5002/url2text "fibrosis"
http_response_post '{ "url": "http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC7350007&blobtype=pdf"}' http://localhost:5002/url2htext "Journal"
http_response_post '{ "text": "Universidad del Valle. Cali - Colombia"}' http://localhost:5002/text2locations "Colombia"
http_response_post '{ "text": "Universidad del Valle. Cali - Colombia" }' http://localhost:5002/text2places "Colombia"
http_response_post '{ "text": "Universidad del Valle. Cali - Colombia" }' http://localhost:5002/text2ner "NNP"
http_response_post '{ "text": "Universidad del Valle. Cali - Colombia. email.test@univalle.edu.co" }' http://localhost:5002/text2emails "email.test@univalle.edu.co"
http_response_post '{ "text": "Esta es una prueba del idioma español" }' http://localhost:5002/text2lang "es"
http_response_post '{ "text": "Breast cancer. A comparative study of two histological prognostic features in operable breast Carcinoma" }' http://localhost:5002/text2keywords "breast"

# mongo test
http_response_get http://localhost:5001 "/mongo-db-create    POST"
http_response_post '{"db_name" : "tests"}' http://localhost:5001/mongo-db-create "0"
http_response_post '{"db_name" : "tests", "coll_name" : "projects"}' http://localhost:5001/mongo-coll-create "0"
http_response_post '{
  "db_name": "tests",
  "coll_name": "projects",
  "document": {
    "name": "BreastCancer",
    "description": "Collection test",
    "maxDocs": 1,
    "status": "Created"
  }
}' http://localhost:5001/mongo-doc-insert "0"
http_response_post '{
  "db_name": "tests",
  "coll_name": "patterns#BreastCancer",
  "document": {
    "pattern": "Breast Cancer"
  }
}' http://localhost:5001/mongo-doc-insert "0"
http_response_get http://localhost:5001/mongo-db-list "tests"
http_response_post '{"db_name" : "tests"}' http://localhost:5001/mongo-coll-list 'patterns#BreastCancer'
http_response_post '{"db_name" : "tests", "coll_name": "projects"}' http://localhost:5001/mongo-doc-list '"name": "BreastCancer", "description": "Collection test", "maxDocs": 1, "status": "Created"'

# E2E orchestrator
http_response_get http://localhost:5004 "/, /metadata-pipeline, /adjacency-pipeline"
http_response_post '{"organization" : "tests", "project": "BreastCancer"}' http://localhost:5004/metadata-pipeline '0'
http_response_post '{"organization" : "tests", "project" : "BreastCancer", "pattern": "global", "graph_type": "authors"}' http://localhost:5004/adjacency-pipeline 'node_link_data'

# Cleanup
http_response_post '{"db_name" : "tests"}' http://localhost:5001/mongo-db-delete "0"

# gui
http_response_get http://localhost:3000 "You need to enable JavaScript to run this app"

exit 0
