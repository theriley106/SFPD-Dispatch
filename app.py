from flask import Flask, request, render_template, request, url_for, redirect, Markup, Response, send_file, send_from_directory, make_response, jsonify
import interactions
import json
import ast
from operator import itemgetter
# This is for sorting the list of instances

app = Flask(__name__, static_url_path="", static_folder="static")


@app.route('/', methods=['GET'])
def index():
	return render_template("index.html")

@app.route('/heatMap', methods=['GET'])
def getHeatMap():
	# This returns the Heatmap indicating call frequency at certain coordinates
	return render_template("heatMap.html", dataset=interactions.readDataset())

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
		instanceCount = str(instances).count(e['location'])
		if instanceCount < 2:
			e["HTML"] = "<h1><center><b>{} Instance reported at this location</b></center></h1>".format(instanceCount)
		else:
			e["HTML"] = "<h1><center><b>{} Instances reported at this location</b></center></h1>".format(instanceCount)
		for val in interactions.grabIncidentByLocation(instances, e["location"]):
			e["HTML"] += interactions.genHTMLDescription(val)
	return jsonify(noDup)

@app.route("/genPopUp/<lng>/<lat>")
def getInstanceInfo(lng, lat):
	try:
		data = interactions.genInfoFromLatLng(lat, lng, radius=.5)
	except:
		return "<center><h1><b>Not enough incidents found near this location</b></h1></center><center><p>Please input another address</p></center>"
	return render_template("popUp.html", DATA=data)

@app.route("/genFullReport/<lng>/<lat>")
def getFullReport(lng, lat):
	data = {"lng": lng, "lat": lat}
	return render_template("resultsPage.html", DATA=interactions.genInfoFromLatLng(lng, lat, radius=.5))

@app.route("/test")
def genTime():
	return render_template("inputTime.html")

@app.route("/timeEstimates/<lng>/<lat>/<timeVal>")
def genEstimateFromTime(lng, lat, timeVal):
	hour = timeVal[:2]
	minute = timeVal[2:]
	#return interactions.ReturnIncidentByLocationAndTime("12:15", (float(lng), float(lat)), "priority", minRange=120)
	estimatedPriority = interactions.ReturnIncidentByLocationAndTime("{}:{}".format(hour, minute), (float(lng), float(lat)), "priority", minRange=180)
	estimatedResponseTime = interactions.ReturnIncidentByLocationAndTime("{}:{}".format(hour, minute), (float(lng), float(lat)), "responseTime", minRange=180)
	estimatedResponseTime = interactions.convertSecondsToMinString(int(estimatedResponseTime))
	if float(estimatedPriority) > 2.5:
		callType = "Emergency"
	else:
		callType = "Non-Emergency"
	return jsonify({"CallType": callType, "EstimatedPriority": estimatedPriority, "ResponseTime": estimatedResponseTime})

@app.route("/all")
def genAnalysis():
	MHH = []
	dataset = interactions.ResponseByZipAsLod()
	zipVal = interactions.returnHousholdIncome()
	for zipC in interactions.getZipCodes():
		MHH.append({"Zip": zipC, "MHH": int(zipVal[zipC]["Income"].replace(",", ""))})
	MHH = sorted(MHH, key=itemgetter('MHH'), reverse=False)
	distanceFrom = json.load(open("DATASETS/distance_from.json"))
	distanceFrom = sorted(distanceFrom, key=itemgetter('Distance'), reverse=False)
	return render_template("all.html", responseTimeData=dataset, MeanIncome=MHH, DistanceFrom=distanceFrom)


if __name__ == "__main__":
	app.run(host='0.0.0.0')
