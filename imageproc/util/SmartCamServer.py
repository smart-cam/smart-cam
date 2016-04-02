from flask import Flask
from flask import jsonify
from db import DynamoDBUtils
import pprint

app = Flask(__name__)

cols = ['CREATE_TIME','LEN','PROCESSED','S3_BUCKET','S3_KEY','VERSION']

@app.route('/')
def hello_world():
    return 'Welcome to SmartCam!'

@app.route('/cam/<id>')
def fetch_cam_records_byID(id):
    print 'ID: {0}'.format(id)
    db = DynamoDBUtils()
    try:
        rows = db.get_items_by_id(id)
        res = {}
        values = []
        for row in rows:
            vDict = {}
            for col in cols:
                vDict[col] = row[col]
            values.append(vDict)
        res[id] = values
        return jsonify(res)
    except Exception as e:
        return e

if __name__ == '__main__':
    app.run()