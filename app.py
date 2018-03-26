from flask import Flask, request, render_template, request, url_for, redirect, Markup, Response, send_file, send_from_directory, make_response, jsonify
# Flask for backend
import interactions
# This is the PRIMARY file that contains almost all functions used in the app
import json
# For interacting with the datasets
import ast
# This is for converting a string into a python dict
from operator import itemgetter
# This is for sorting the list of instances

'''
interactions.py contains almost all of the functions
used in the webapp, and it has a lot more comments
explaning what's going on in the backend
'''

app = Flask(__name__, static_url_path="", static_folder="static")


@app.route('/', methods=['GET'])
def index():
	# This returns the main "index" page
	return render_template("index.html")
	# 127.0.0.1/

@app.route('/heatMap', methods=['GET'])
def getHeatMap():
	# This returns the Heatmap indicating call frequency at certain coordinates
	return render_template("heatMap.html", dataset=interactions.readDataset())
	# 127.0.0.1/heatMap

@app.route("/getInstanceByLongLat/<lng>/<lat>")
def getInstanceLngLat(lng, lat):
	# Returns instances near a specific lat long
	instances = interactions.incidentsNearLatLng((float(lng), float(lat)), radius=.1)
	# This returns th einstances near a specific lat long
	noDup = interactions.removeDuplicateLocations(instances)
	# This grabs the location to tell if more than 1 call has taken place at this location
	locationLists = interactions.returnListOfParam(instances, 'location')
	# This is simply a list of location coords
	for e in noDup:
		# Iterates through all unique locaitons
		instanceCount = str(instances).count(e['location'])
		# Counts how many times the location has showed up
		if instanceCount < 2:
			# This means it's unique
			e["HTML"] = "<h1><center><b>{} Instance reported at this location</b></center></h1>".format(instanceCount)
		else:
			# This means it's not unique
			e["HTML"] = "<h1><center><b>{} Instances reported at this location</b></center></h1>".format(instanceCount)
		for val in interactions.grabIncidentByLocation(instances, e["location"]):
			# Iterates through all incidents that have taken place at that location
			e["HTML"] += interactions.genHTMLDescription(val)
			# Adds them to the pop up html
	return jsonify(noDup)
	# Returns it as structured JSON

@app.route("/genPopUp/<lng>/<lat>")
def getInstanceInfo(lng, lat):
	try:
		# Try -> except to see if there are nearby long lat coords
		data = interactions.genInfoFromLatLng(lat, lng, radius=.5)
		# Pulls all instances within a .5 mile radius
	except:
		# This means there are no coords nearby
		return "<center><h1><b>Not enough incidents found near this location</b></h1></center><center><p>Please input another address</p></center>"
		# Returns an error message
	return render_template("popUp.html", DATA=data)
	# Returns a template for the popup

@app.route("/genFullReport/<lng>/<lat>")
def getFullReport(lng, lat):
	# Generates a report for a lat long coord
	return render_template("resultsPage.html", DATA=interactions.genInfoFromLatLng(lng, lat, radius=.5))

@app.route("/timeEstimates/<lng>/<lat>/<timeVal>")
def genEstimateFromTime(lng, lat, timeVal):
	# This generates predictions from the time inputted
	hour = timeVal[:2]
	# Javascript sends it as something like 0815, so this splits out 08
	minute = timeVal[2:]
	# Javascript sends it as something like 0815, so this splits out 15
	estimatedPriority = interactions.ReturnIncidentByLocationAndTime("{}:{}".format(hour, minute), (float(lng), float(lat)), "priority", minRange=180)
	# All instances near that location during a certain time
	estimatedResponseTime = interactions.ReturnIncidentByLocationAndTime("{}:{}".format(hour, minute), (float(lng), float(lat)), "responseTime", minRange=180)
	# All instances of response time for that location during a certain time
	estimatedResponseTime = interactions.convertSecondsToMinString(int(estimatedResponseTime))
	# Gets prediction from average
	if float(estimatedPriority) > 2.5:
		# Means it rounds up to 3
		callType = "Emergency"
	else:
		# Rounds down
		callType = "Non-Emergency"
	return jsonify({"CallType": callType, "EstimatedPriority": estimatedPriority, "ResponseTime": estimatedResponseTime})

@app.route("/all")
def genAnalysis():
	# Generates the overall analysis from /all
	MHH = []
	# Mean household income
	dataset = interactions.ResponseByZipAsLod()
	# Returns the response time from each zip as a list of dictionaries
	zipVal = interactions.returnHousholdIncome()
	# Returns the household incomes for each zip as a python dict
	for zipC in interactions.getZipCodes():
		# Iterates through all zip codes in the dataset
		MHH.append({"Zip": zipC, "MHH": int(zipVal[zipC]["Income"].replace(",", ""))})
		# Appends the values to the mean household income dataset
	MHH = sorted(MHH, key=itemgetter('MHH'), reverse=False)
	# Sorts the values
	distanceFrom = json.load(open("DATASETS/distance_from.json"))
	# Loads the distance dataset
	distanceFrom = sorted(distanceFrom, key=itemgetter('Distance'), reverse=False)
	# Sorts the values
	return render_template("all.html", responseTimeData=dataset, MeanIncome=MHH, DistanceFrom=distanceFrom)
	# Generates the template

if __name__ == "__main__":
	app.run(host='0.0.0.0')
