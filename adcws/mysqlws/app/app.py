from flask import Flask, jsonify, request
import mysql.connector
import requests
import time

app = Flask(__name__)

config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'adccali'
    }

def post_json_request(url, obj):
    return requests.post(url, json = obj).json()

def execute_mysql_query(query):
    connection = mysql.connector.connect(**config)
    # connection.set_charset_collation('utf8')
    cursor = connection.cursor()
    cursor.execute(query)
    try:
        columns = cursor.description 
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    except:
        results = None
    #results=cursor.fetchall()
    cursor.close()
    connection.close()
    return results
def execute_mysql_query2(query):
    connection = mysql.connector.connect(**config)
    # connection.set_charset_collation('utf8')
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    try:
        columns = cursor.description 
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    except:
        results = None
    #results=cursor.fetchall()
    cursor.close()
    connection.close()
    return results
   
@app.route('/patterns',methods=['GET'])
def patterns():
    results=execute_mysql_query('SELECT * FROM patterns')
    return jsonify(results)
    
@app.route('/searches',methods=['GET'])
def searches():
    results=execute_mysql_query('SELECT * FROM searches')
    return jsonify(results)
    
@app.route('/execute',methods=['GET'])
def execute():
    # Para cada patron sacar 1000 pmid
    # para cada pmid recuperar metadatos
    # llenar la base de datos
    results=execute_mysql_query('SELECT * FROM patterns')
    for pattern in results:
        # {'id': 1, 'pattern': 'Cancer de mama', 'description': 'Principales'}
        pmids_json=post_json_request('http://metapubws:5000/pmids',{"query": pattern['pattern']})
        pmids=pmids_json['pmids']
        for pmid in pmids:
            print(pattern['id'])
            print(pattern['pattern'])
            print(pmid)
            if pmid is not None:
                metadata_json=post_json_request('http://metapubws:5000/metadata',{"id": pmid})
                #print(metadata_json['title'])
                #print(metadata_json['abstract'])
                #time.sleep(0.3)
                #query='INSERT INTO searches (id_pattern, pmid, title, abstract) VALUES (%s,%s,"%s","%s") ON DUPLICATE KEY UPDATE title="%s", abstract="%s";'%(pattern['id'],pmid,metadata_json['title'],metadata_json['abstract'],metadata_json['title'],metadata_json['abstract'])
                try:
                    query='INSERT INTO searches (id_pattern, pmid, title, abstract) VALUES (%s,%s,"%s","%s");'%(pattern['id'],pmid,metadata_json['title'].replace('"',''),metadata_json['abstract'].replace('"',''))
                    results=execute_mysql_query2(query)
                except:
                    query="Mysql not executed"                
    results=execute_mysql_query('SELECT id_pattern, title, abstract FROM searches')
    return jsonify(results)
    
