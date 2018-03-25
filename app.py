from flask import Flask, request, render_template, request, url_for, redirect, Markup, Response, send_file, send_from_directory, make_response, jsonify
import interactions
import json
import ast

app = Flask(__name__, static_url_path="", static_folder="static")


@app.route('/', methods=['GET'])
def index():
	return render_template("index.html", dataset=interactions.readDataset()[:5])

@app.route('/residential', methods=['GET'])
def residential():
	return render_template("residential.html", dataset=interactions.readDataset())

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

@app.route('/otherViz', methods=['GET'])
def getVizz():
	return render_template("heatMapExample.html", dataset=interactions.readDataset())

@app.route('/getGeoJson', methods=['GET'])
def getGeoJson():
	return jsonify(json.load(open("DATASETS/geo.geojson")))

@app.route("/getInstanceByLongLat/<lng>/<lat>")
def getInstanceLngLat(lng, lat):
	instances = interactions.incidentsNearLatLng((float(lng), float(lat)), radius=.1)
	noDup = interactions.removeDuplicateLocations(instances)
	# This grabs the location to tell if more than 1 call has taken place at this location
	print len(noDup)

	locationLists = interactions.returnListOfParam(instances, 'location')
	for e in noDup:
		e["HTML"] = ""
		for val in interactions.grabIncidentByLocation(instances, e["location"]):
			e["HTML"] += interactions.genHTMLDescription(val)
	return jsonify(noDup)

@app.route("/genPopUp/<lng>/<lat>")
def getInstanceInfo(lng, lat):
	data = {"lng": lng, "lat": lat}
	return jsonify(interactions.genInfoFromLatLng(lat, lng))

@app.route("/genFullReport/<lng>/<lat>")
def getFullReport(lng, lat):
	data = {"lng": lng, "lat": lat}
	return render_template("fullReport.html", DATA=data)

if __name__ == "__main__":
	app.run(host='0.0.0.0')
