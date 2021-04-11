import sys
import logging
import pymysql
import json
import os

#rds settings
rds_endpoint = os.environ['rds_endpoint']
username=os.environ['username']
password=os.environ['password']
db_name=os.environ['db_name']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Connection
try:
    connection = pymysql.connect(host=rds_endpoint, user=username,
        passwd=password, db=db_name)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()
logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

def handler(event, context):
    cur = connection.cursor()  
## Retrieve Data
    # Get your queue no and other details
    query = "SELECT q.status, q.queueNumber, q.branchId,b.name as branchName,b.addr as branchAddr,b.postal as branchPostal, c.id as clinicId, c.name as clinicName, q.customerId \
        FROM Queue q,Branch b,Clinic c \
            WHERE customerId= 1 and q.branchId=b.id and b.clinicId=c.id and q.status='Q'".format(event['customerId'])  
    cur.execute(query)
    connection.commit()
## Construct body of the response object
    transactionResponse = {}
    rows = cur.fetchall()
    branchId = 0
    for row in rows:
        print("TEST {0} {1} {2} {3} {4} {5} {6} {7} {8}".format(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
        transactionResponse['status'] = row[0]
        transactionResponse['yourQueueNumber'] = row[1]
        transactionResponse['branchId'] = row[2]
        transactionResponse['branchName'] = row[3]
        transactionResponse['branchAddr'] = row[4]
        transactionResponse['branchPostal'] = row[5]
        transactionResponse['clinicId'] = row[6]
        transactionResponse['clinicName'] = row[7]
        transactionResponse['customerId'] = row[8]
        branchId = row[2]
    # Get current queue no
    query="SELECT min(queueNumber) FROM Queue WHERE branchId={} and status='D' or status='P' or status='C'".format(branchId)
    cur.execute(query)
    connection.commit()
    rows = cur.fetchall()
    for row in rows:
        print("current queue no: {0}".format(row[0]))
        transactionResponse['currentQueueNumber']=row[0]

# Construct http response object
    responseObject = {}
    responseObject['statusCode'] = 200
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type']='application/json'
    responseObject['headers']['Access-Control-Allow-Origin']='*'
    responseObject['body'] = json.dumps(transactionResponse, sort_keys=True,default=str)
    
    #k = json.loads(responseObject['body'])
    #print(k['uin'])

    return responseObject