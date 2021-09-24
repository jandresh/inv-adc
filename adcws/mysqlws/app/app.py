from flask import Flask, jsonify, request
import mysql.connector
import requests
import time

app = Flask(__name__)

config = {
        'user': 'adccali',
        'password': 'adccali',
        'host': 'db',
        'port': '3306',
        'database': 'adccali'
    }

#Initial database creation
# def database_init():
#     try:
#         connection = mysql.connector.connect(
#             host='db',
#             user='root',
#             password='root',
#             port='3306'
#         )
#         cursor = connection.cursor()
#         cursor.execute('create database adccali CHARACTER SET utf8 COLLATE utf8_general_ci')
#         connection.commit()
#         cursor.close()
#         connection.close()
#         print('adc database created')
#         return True
#     except:
#         print('adc database exist')
#         return False

def post_json_request(url, obj):
    return requests.post(url, json = obj).json()

def execute_mysql_query(query, connection):
    # connection = mysql.connector.connect(**config)
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
    # connection.close()
    return results

def execute_mysql_query2(query, connection):
    try:
        # connection = mysql.connector.connect(**config)
        # connection.set_charset_collation('utf8')
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        columns = cursor.description 
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        #results=cursor.fetchall()
        cursor.close()
        # connection.close()
    except:
        results = None
    return results
   
@app.route('/init',methods=['GET'])
def init():
    connection = mysql.connector.connect(**config)
    # Init tables
    # database_init()
    try:
        execute_mysql_query2(
                """CREATE TABLE patterns (
                    id INT(10) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    pattern TEXT NOT NULL,
                    description TEXT
                )""", connection)
        execute_mysql_query2(
                """CREATE TABLE searches (
                    id_pattern INT(10) NOT NULL,
                    pmid INT(10) NOT NULL,
                    title TEXT,
                    abstract TEXT,
                    PRIMARY KEY (id_pattern,pmid)
                )""", connection)
        execute_mysql_query2(
            """INSERT INTO 
                    patterns (pattern, description)
                VALUES 
                    ('Cancer de mama','Principales'),
                    ('Breast cancer','Main'),
                    ('Cancer de cervix','Principales'),
                    ('Cervical Cancer','Main'),
                    ('Cancer de prostata','Principales'),
                    ('Prostate cancer','Main'),
                    ('Cancer de pulmon','Principales'),
                    ('Lung cancer','Main');
            """, connection)
    except:
        print('Error on tables creation')
    results=execute_mysql_query('SELECT * FROM patterns', connection)
    connection.close()
    return jsonify(results)

@app.route('/patterns',methods=['GET'])
def patterns():
    connection = mysql.connector.connect(**config)
    results=execute_mysql_query('SELECT * FROM patterns', connection)
    connection.close()
    return jsonify(results)
    
@app.route('/searches',methods=['GET'])
def searches():
    connection = mysql.connector.connect(**config)
    results=execute_mysql_query('SELECT * FROM searches', connection)
    connection.close()
    return jsonify(results)
    
@app.route('/execute',methods=['GET'])
def execute():
    connection = mysql.connector.connect(**config)
    # Para cada patron sacar 1000 pmid
    # para cada pmid recuperar metadatos
    # llenar la base de datos
    results=execute_mysql_query('SELECT * FROM patterns', connection)
    for pattern in results:
        # {'id': 1, 'pattern': 'Cancer de mama', 'description': 'Principales'}
        get_metadata=True
        try:
            pmids_json=post_json_request('http://metapubws:5000/pmids',{"query": pattern['pattern']})            
        except:
            get_metadata=False
        if get_metadata:
            pmids=pmids_json['pmids']
            pmid_counter=0
            insert_counter=0
            for pmid in pmids:
                print("id_pattern:%s"%pattern['id'])
                print("pattern:%s"%pattern['pattern'])
                print("pmid:%s"%pmid)
                pmid_counter+=1
                print("pmid_counter:%s"%pmid_counter)
                success=0
                if pmid is not None:
                    insert_mysql=True
                    try:
                        metadata_json=post_json_request('http://metapubws:5000/metadata',{"id": pmid})
                    except:
                        insert_mysql=False
                    print("title:%s"%metadata_json['title'])
                    print("abstract:%s"%metadata_json['abstract'])
                    # time.sleep(0.3)
                    if(metadata_json['abstract']==None):
                        insert_abstract=""
                    else:
                        insert_abstract=metadata_json['abstract']
                    if(metadata_json['abstract']==None):
                        insert_title=""
                    else:
                        insert_title=metadata_json['abstract']    
                    if insert_mysql: 
                        try:
                            query='INSERT INTO searches (id_pattern, pmid, title, abstract) VALUES (%s,%s,"%s","%s") ON DUPLICATE KEY UPDATE title="%s", abstract="%s";'%(pattern['id'],pmid,insert_title.replace('"','').replace('\n',''),insert_abstract.replace('"','').replace('\n',''),insert_title.replace('"','').replace('\n',''),insert_abstract.replace('"','').replace('\n',''))
                            results=execute_mysql_query2(query, connection)
                            success=1
                        except:
                            query="Mysql not executed"
                            success=0
                insert_counter+=success            
                print("insert_counter:%s"%insert_counter)
                                        
    results=execute_mysql_query('SELECT id_pattern, title, abstract FROM searches',connection)
    connection.close()
    return jsonify(results)
    
