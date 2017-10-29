from flask import Flask, jsonify, request, render_template
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
import json
from math import sqrt

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'alerts'
app.config['MONGO_URI'] = 'mongodb://alerts_db:27017/alerts'

mongo = PyMongo(app)
CORS(app, resources={r"/*": {"origins": "*"}})

ACCESS_TOKEN = '837610735932932096-sVr1Lu5BQWbqmQgLs9Zxn6UlZC4andz'
ACCESS_SECRET = 'SX5ik6FgHe7QCsZ9ihqlmwF8ecCHPnNMFl9cz24W0tFvp'
CONSUMER_KEY = 'm0eXyOFZPtFPDr5HeuERvH4nb'
CONSUMER_SECRET = 'yKA3hGvqXiMyzvZMBGx9vVomz8AkEfwcdyWF8idTD1qEDOmgOV'

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
t = Twitter(auth=oauth)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/status', methods=['GET'])
def get_status():
	return jsonify({'status': 'OK'})

@app.route('/api/v1/alerts', methods=['GET'])
@cross_origin()
def get_alerts():
		
	# get request data
	latitude = request.args['latitude']
	longitude = request.args['longitude']
	max_range = 100
	text = request.args['text']

	if latitude == '' or longitude == '':
		return jsonify({"alerts": {}, "tweets": {}})

	# query twitter with text and geolocation
	last_id = None
	tweets = t.search.tweets(q=text, geocode = "%f,%f,%dkm" % (float(latitude), float(longitude), max_range), count=100, max_id=last_id)

	# get alerts from location
	alerts = mongo.db.alerts

	cursor = alerts.find({}, {'_id': 0})

	all_alerts = []

	for document in cursor:
		
		doc_latitude = document['latitude']
		doc_longitude = document['longitude']

		if doc_latitude != '' and doc_longitude != '':
			
			doc_latitude = float(doc_latitude)
			doc_longitude = float(doc_longitude)
			latitude = float(latitude)
			longitude = float(longitude)

			dist = sqrt(((latitude * 110.6 - doc_latitude * 110.6) ** 2) + ((longitude * 110.6 - doc_longitude * 110.6) ** 2))

			if dist <= max_range:
				all_alerts.append(document)

	return jsonify({'alerts': all_alerts, 'tweets': tweets['statuses']})

@app.route('/api/v1/alerts', methods=['POST'])
@cross_origin()
def post_alerts():

	# post alerts to database
	alerts = mongo.db.alerts
	latitude = request.args['latitude']
	longitude = request.args['longitude']
	text = request.args['text']

	if latitude == '' or longitude == '':
		return jsonify({"status": "FAIL"})

	alert_id = alerts.insert({'latitude': float(latitude), 'longitude': float(longitude), 'text': text})

	created_alert = alerts.find_one({'_id': alert_id}, {'_id': 0})

	return jsonify({"alert": created_alert})


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')