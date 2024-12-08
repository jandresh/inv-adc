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

# metapub tests
http_response_get http://localhost:5000 "/title, /abstract, /pmids, /metadata, /pmid2pdf, /query"
http_response_post '{ "id": "2020202" }' http://localhost:5000/title "The structure of the OARS physical health measures."
http_response_post '{ "id": "2020202" }' http://localhost:5000/abstract "This article proposes and evaluates two models for integrating self-reported health status"
http_response_post '{ "query": "breast cancer" }' http://localhost:5000/pmids '"39645589","39645560","39645548","39645491"'
http_response_post '{ "id": "2020202" }' http://localhost:5000/metadata "10.1097/00005650-199104000-00003"
http_response_post '{ "id": "32599772"}' http://localhost:5000/pmid2pdf "http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC7350007&blobtype=pdf"

exit 0
