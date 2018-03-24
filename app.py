from flask import Flask, request, render_template, request, url_for, redirect, Markup, Response, send_file, send_from_directory, make_response, jsonify
import interactions

app = Flask(__name__, static_url_path="", static_folder="static")


@app.route('/', methods=['GET'])
def index():
	return render_template("index.html", dataset=interactions.readDataset()[:500])

@app.route('/dataset', methods=['GET'])
def dataset():
	return jsonify(interactions.readDataset())

@app.route('/Resident', methods=['GET'])
def resident():
	return jsonify(interactions.readDataset())

@app.route('/LawEnforcement', methods=['GET'])
def lawEnforcement():
	return jsonify(interactions.readDataset())

@app.route('/Government', methods=['GET'])
def government():
	return jsonify(interactions.readDataset())

@app.route('/searchAddress', methods=['POST'])
def searchAddress():
	address = request.form.get("address")
	return ""

@app.route('/responseTimeViz', methods=['GET'])
def getViz():
	dataset = interactions.ResponseByZipAsLod()
	return render_template("zipResponseViz.html", responseTimeData=dataset)


if __name__ == "__main__":
	app.run(host='0.0.0.0')
