from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def index():
    return 'Nothing yet, but working on it'

@app.route('/api/v1/status', methods=['GET'])
def get_status():
	return jsonify({'status': 'Live in full effect!'})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')