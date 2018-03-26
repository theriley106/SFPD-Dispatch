import csv
# This is for interactions with the datasets
from haversine import haversine
# This is the calculate long lat that's within a certain radius
from geopy.geocoders import GoogleV3
# This is for converting address to long lat
import glob
# This is used to returns lists of files ending in a certain extension
import json
# This is used to read datasets
import re
# Regex is used for extracting values from the dataset strings
from datetime import datetime
# This is used to calculate time differences
from operator import itemgetter
# This is for sorting the list of instances
import copy
# For copying dataset that is iterated over
import humanfriendly
# For converting seconds into a string

'''
Values from MAIN_DATASET_FILE:
call_number
unit_id
incident_number
call_type
call_date
watch_date
received_timestamp
entry_timestamp
dispatch_timestamp
response_timestamp
on_scene_timestamp
transport_timestamp
hospital_timestamp
call_final_disposition
available_timestamp
address
city
zipcode_of_incident
battalion
station_area
box
original_priority
priority
final_priority
als_unit
call_type_group
number_of_alarms
unit_type
unit_sequence_in_call_dispatch
fire_prevention_district
supervisor_district
neighborhood_district
location
row_id
latitude
longitude
'''

'''
Zip Codes:
['94130',
'94131',
'94132',
'94133',
'94134',
'94158',
'94118',
'94112',
'94110',
'94111',
'94116',
'94117',
'94114',
'94115',
'94127',
'94124',
'94123',
'94122',
'94121',
'94129',
'94109',
'94108',
'94103',
'94102',
'94105',
'94104',
'94107']
'''

DATASETS_DIRECTORY = "DATASETS"
# This is the folder than contains all of the Datasets
MAIN_DATASET_FILE = "{}/sfpd_dispatch_data_subset.csv".format(DATASETS_DIRECTORY)
# This is the location where the SFPD dataset is stored
UMICH_DATASET_FILE = "{}/umichDataset.csv".format(DATASETS_DIRECTORY)
# Data is from https://www.psc.isr.umich.edu/dis/census/Features/tract2zip/
# University of Michigan mean household income dataset
REDUCE_PROCESSING_POWER = True
# This enables various ways of reducing processing power
DATASET_FILENAME_STRUCTURE = DATASETS_DIRECTORY + "/PS_{0}_{1}_{2}.json"
# This is for the datasets that are created by the program
# intended as: DATASET_FILENAME_STRUCTURE.format(latitude, longitude, radius)
RESPONSE_BY_ZIP_DATASET = "{}/response_by_zip.json".format(DATASETS_DIRECTORY)
# JSON File containing police response time per zip
# Code for creating this file can be found in dataAnalysis.py
EMERGENCY_LOCATIONS_DATASET = "{}/emergency_locations.json".format(DATASETS_DIRECTORY)
# This contains the log lat coordinates for the nearest hospitals, police stations, and fire departments

listOfTypes = []

def readDataset(csvFile=MAIN_DATASET_FILE, householdIncome=True):
	# This will convert the dataset into a format the the front end will use
	dataset = []
	# Ideally this should be  a list of JSON/python dicts for the jinja template
	datasetList = csvToList(csvFile)
	# This is the dataset in list format
	datasetSchema = datasetList[0]
	# "call_number", "unit_id", etc.
	datasetList = datasetList[1:]
	# This removes the top row, which indicates the row values | ie: not actual data
	for val in datasetList:
		tempInfo = {}
		# This is overwritten on each loop
		for i in range(len(datasetSchema)):
			# Coverts each line in the CSV into JSON
			tempInfo[datasetSchema[i]] = val[i]
			# ie: dataset['call_number'] = 12312312321
		if tempInfo["priority"] == "E":
			# This messes up the frontend when priority is not an int
			tempInfo["priority"] = 3
			# Sets it to 3, which is basically "Emergency"
		#tempInfo["MeanHousehold"] = returnHousholdIncome(tempInfo["zipcode_of_incident"])
		# Ideally this would be a value IN THE dataset, but I don't want to modify the dataset from mindsumo
		tempInfo["mapColor"] = getPriorityColor(tempInfo["priority"])
		# This defines the pin color on the map
		tempInfo["responseTime"] = calculateResponseTime(tempInfo)
		# This is the total response time for the call
		dataset.append(tempInfo)
		# Adds the python dict to the dataset array
	return dataset
	# Returns an array of python dictionaries

def getPriorityColor(priority):
	# Red: #f2391d
	# Yellow: #f9fc49
	# Gray: #b7b2b2
	# Blue: #6e8dea
	# Green: #5ee5ad
	try:
		return ["#5ee5ad", "#6e8dea", "#f2391d"][int(priority)-1]
	except Exception as exp:
		return "#b7b2b2"

def getZipCodes():
	# Returns all zip codes in the dataset
	return ['94130', '94131', '94132', '94133', '94134', '94158', '94118', '94112', '94110', '94111', '94116', '94117', '94114', '94115', '94127', '94124', '94123', '94122', '94121', '94129', '94109', '94108', '94103', '94102', '94105', '94104', '94107']

def returnParamByZip(zipCode, param):
	# This will return a list of params filtered by zip code
	incidentList = returnIncidentsByParam("zipcode_of_incident", zipCode)
	# Creates an incident list containing incidents that took place in that zip code
	return returnListOfParam(incidentList, param)
	# Returns a list of all values taking place in that zip code

def getTypeColor(incident):
	colorInfo = {}
	# Red: #f2391d
	# Yellow: #f9fc49
	# Gray: #b7b2b2
	# Blue: #6e8dea
	# Green: #5ee5ad
	colorInfo["Medical Incident"] = "#5ee5ad"
	# Requires Ambulance
	colorInfo["Structure Fire"] = "#f2391d"
	colorInfo["Outside Fire"] = "#f2391d"
	colorInfo["Electrical Hazard"] = "#f2391d"
	colorInfo["Vehicle Fire"] = "#f2391d"
	colorInfo["Fuel Spill"] = "#f2391d"
	colorInfo["Water Rescue"] = "#f2391d"
	colorInfo["Smoke Investigation (Outside)"] = "#f2391d"
	colorInfo["Train / Rail Incident"] = "#f2391d"
	colorInfo["Gas Leak (Natural and LP Gases)"] = "#f2391d"
	colorInfo["Odor (Strange / Unknown)"] = "#f2391d"
	colorInfo["HazMat"] = "#f2391d"
	colorInfo["Elevator / Escalator Rescue"] = "#f2391d"
	# Requires Fire Service
	colorInfo["Citizen Assist / Service Call"] = "#6e8dea"
	colorInfo["Alarms"] = "#6e8dea"
	colorInfo["Other"] = "#6e8dea"
	colorInfo["Traffic Collision"] = "#6e8dea"
	# These instances require police vehicles
	return colorInfo[incident]

def csvToList(csvFile):
	# This will return a list of rows in the csv file
	with open(csvFile, 'rb') as f:
		reader = csv.reader(f)
		return list(reader)
		# Returns as list, which == rows in the csv

def readJsonDataset(jsonFile):
	# Reads a json dataset
	return json.load(open(jsonFile))
	# Reads the json file and returns it as a python object

def checkInRadius(point1, point2, radius):
	# This will return if a point is within a certain radius
	return (haversine(point1, point2, miles=True) < radius)

def returnHousholdIncome():
	# Returns mean household income and population for a zip code
	householdInfo = {}
	for row in csvToList(UMICH_DATASET_FILE)[1:]:
		# Goes through all lines in the umich dataset, except for line #1
		zipCode = row[0]
		# ie: 54666
		meanIncome = row[1]
		# ie: 104969
		populationSize = row[2]
		# ie: 14225
		householdInfo[zipCode] = {"Population": populationSize, "Income": meanIncome}
		# Python dictionary with all values being integers
	return householdInfo
	# Returns as dictionary

def addressToCoord(address):
	# Returns lat long for an address
	geolocator = GoogleV3(api_key='AIzaSyDBZre20-q9hSY0BFXTqmiZr5-orJSuwr0')
	# ^ Yes, I know this isn't a good idea :P
	coords = geolocator.geocode(address)
	# Coords is a class that contains a ton of info about the address
	return (coords.latitude, coords.longitude)
	# Returns lat long as a float

def coordToAddress(point):
	# Returns address for long lat
	geolocator = GoogleV3(api_key='AIzaSyDBZre20-q9hSY0BFXTqmiZr5-orJSuwr0')
	# ^ Yes, I know this isn't a good idea :P
	coords = geolocator.reverse(list(point), exactly_one=True)
	# Coords is a class that contains a ton of info about the address
	return coords.address
	# Returns address as a string

def incidentsNearLatLng(point, radius):
	# Returns a list of instances within radius of a long lat point
	dataset = readDataset()
	# Reads the dataset
	values = copy.copy(dataset)
	# This copies that dataset list so nothing is does to this array
	for var in values:
		# Goes through all values in the dataset
		if not checkInRadius((float(var["latitude"]), float(var["longitude"])), point, radius):
			# Checks to see if the value is within the radius
			dataset.remove(var)
			# Removes the value
	return dataset
	# Returns a list of python dictionaries

def incidentsNearAddress(address, radius):
	# Returns all instances that take place within radius of an address
	lat, lng = addressToCoord(address)
	# Returns latitude and longitude for an address
	point = (lat, lng)
	# Point is just a tuple sent to functions using lat lng
	print(point)
	if REDUCE_PROCESSING_POWER == True:
		# This means the constant is set to True
		previousSearch = checkPreviousSearch(point, radius)
		# This checks to see if this search query has already been run
		if previousSearch != None:
			# This means the dataset has already been created
			return readJsonDataset(previousSearch)
			# Returns dataset without doing a ton of processing
	incidentList = incidentsNearLatLng(point, radius)
	# Returns incidents near that lat long
	if REDUCE_PROCESSING_POWER == True:
		# This will save the dataset locally for future searches
		saveIncidentList(incidentList, point, radius)
		# Saves incidentList as {latitude}-{longitude}-{radius}.json
	return incidentList

def saveIncidentList(incidentList, point, radius):
	# Saves the list of json files containing incidents within a certain radius
	latitude = point[0]
	# This sets the latitude as first elem in the point tuple
	longitude = point[1]
	# This sets the longitude as second elem in the point tuple
	fileName = DATASET_FILENAME_STRUCTURE.format(latitude, longitude, radius)
	# Sets filename it's going to save the incident list as
	with open(fileName, 'w') as csvObject:
		# Will overwrite if the file already exists
		json.dump(incidentList, csvObject)
		# Writes incident list to fileName, a json file

def extractLocationFromFile(fileName):
	# This extract long, lat, and radius from a file name
	fileInfo = fileName.partition("{}/".format(DATASETS_DIRECTORY))[2]
	# This only grabs the actual filename - removing directory info
	fileInfo = fileName.replace(".json", "")
	# This will remove .json only if it's present
	if fileInfo.count("_") != 3:
		# This checks to see if the format indicates it contains lat lng radius
		return None
		# It will return None if it doesn't
	else:
		# This means it does follow the {lat}-{lng}-{radius}.json format
		lat, lng, radius = fileInfo.partition("PS_")[2].split("_")
		# Creates 3 files
		return {"Latitude": lat, "Longitude": lng, "Radius": radius, "Filename": fileName}
		# Returns Python dictionary

def returnLatLngTuple(pythonDict):
	# Converts the python dict created by extractLocationFromFile() to tuple
	try:
		# Try-Except to catch any issues
		latitude = pythonDict["Latitude"]
		# Latitude is a string
		longitude = pythonDict["Longitude"]
		# Longitude is a string
		return (float(latitude), float(longitude))
		# Returns them as a tuple of floats
	except:
		# Means there was an issue with the dict
		raise Exception("returnLatLngTuple() failed - python dictionary is not in the correct format")
		# More detailed error than before

def checkPreviousSearch(point, radius):
	'''
	Since incidentsNearLatLng() is extremely time consuming, the searches are saved
	as CSV, and this list of CSVs is checked upon each call to incidentsNearLatLng()
	to reduce the speed of incidents being returned
	'''
	for file in glob.glob("{}/PS_*.json".format(DATASETS_DIRECTORY)):
		# Goes through all files in DATASETS_DIRECTORY ending in .json
		fileInfo = extractLocationFromFile(file)
		# Tries to extract lat, lng, radius from file
		if fileInfo != None:
			# Means the filename is in the correct {lat}-{lng}-{radius}.json format
			if returnLatLngTuple(fileInfo) == point and float(radius) == float(fileInfo["Radius"]):
				# This means the params match a previous dataset
				return file
				# String containing file

def returnIncidentsByParam(parameter, equalsValue, incidentList=None):
	# Parameter is equal to dict key, equalsValue is the value
	# Returns all instances where one dict value matches another dict value
	# Ie: parameter = "zipcode_of_incident"
	# equalsValue = "94108"
	# Would return all incidents where incident["zipcode_of_incident"] == "94108"
	returnValues = []
	# This will be the list of incidents that are returned to the user
	if incidentList == None:
		# Means that the function wasn't called with a predefined list
		incidentList = readDataset()
		# Reads full incident list
	for incident in incidentList:
		# Loops through all incidents
		try:
			# Try -> Except to catch invalid parameter
			if str(incident[parameter]) == str(equalsValue):
				# Converting both to strings, ignoring data type
				returnValues.append(incident)
				# Appends incident value to the list of data that is returned
		except Exception as exp:
			# This means the parameter is not in the incident dict
			print exp
			# More detailed just in case exp is different
			raise Exception("Parameter in returnIncidentsByParam() is not valid")
			# More detailed exception
	return returnValues
	# Return type is a List of dict values

def returnListOfParam(incidentList, param, duplicates=True):
	# Input: List of python dicts, string containing a dictionary key
	# Output: list of values
	# Ie: param = "zipcode_of_incident"
	# would return a list of values matching incident["zipcode_of_incident"]
	returnValues = []
	# This will be the list of incidents that are returned to the user
	for incident in incidentList:
		try:
			# Try -> Except to catch invalid parameter
			returnValues.append(incident[param])
			# Appends value to the list of data that is returned
		except Exception as exp:
			# This means the parameter is not in the incident dict
			print exp
			# More detailed just in case exp is different
			raise Exception("Parameter in returnListOfParam() is not valid")
			# More detailed exception
	if duplicates == True:
		return returnValues
		# Return type is a List
	else:
		# This means that you only want unique param values
		return list(set(returnValues))
		# Set only contains unique, converting back to list removed all non-unique vals

def averageValue(listOfValues, forceSkip=False, skipZero=False):
	# Returns an average for all values in a list
	if forceSkip == True:
		# This means the default value has been changed to == True
		valList = []
		# Val list will hold float values from listOfValues
		for val in listOfValues:
			# Iterates through all values
			try:
				# Tries to convert the list into floats
				if skipZero == True:
					# Default param is equal to true | skip values == 0
					if float(val) != 0:
						# Primarily for the response time, where invalid times == 0
						valList.append(float(val))
						# Appends the float val to valList
				else:
					# skipZero == False
					valList.append(float(val))
					# Appends the float val to valList
			except:
				# This means it wasn't able to be converted to a float
				pass
				# Ignore the error
		listOfValues = valList
		# Assigns the valList to the new listOfValues
	else:
		# This means forceSkip was set to False, the default val
		try:
			# Tries to convert the list into floats
			listOfValues = [float(value) for value in listOfValues]
			# Converts the entire list into a list of float values
		except:
			# This means it's probably a list of strings or dicts
			raise Exception("Error in averageValue() - elements not numerical values")
			# More detailed exception
	return (sum(listOfValues) / float(len(listOfValues)))
	# Sum / length is the average
	# Returns value as a float

def extractTimeVal(timeStamp):
	# Returns the datetime value from a timestamp string
	timeVal = re.findall('(.+)\.', timeStamp)[0]
	# timeVal is the raw timestamp as a string
	timeFormat = "%Y-%m-%d %H:%M:%S"
	# This is the format of the timestamps in the dataset
	return datetime.strptime(timeVal, timeFormat)
	# Datetime values can be added to, subtracted from, etc

def calculateResponseTime(incident):
	# Input: incident dictionary
	# Output: float containing seconds
	try:
		# Try -> Except because some calls don't have timestamps
		callReceived = extractTimeVal(incident["received_timestamp"])
		# Extracts the datetime value from the "received_timestamp" string
		onScene = extractTimeVal(incident["on_scene_timestamp"])
		# Extracts the datetime value from the "on_scene_timestamp" string
		return (onScene - callReceived).total_seconds()
		# onScence - callReceived is the total time it took to respond
	except:
		# This means the call likely is missing a timestamp
		return (callReceived - callReceived).total_seconds()
		# This means the response time is 0, which is impossible so the value will be skipped

def sortIncidentList(incidentList, param, reverse=True):
	try:
		# Try -> Except to catch nonexistant parameters
		return sorted(incidentList, key=itemgetter(param), reverse=reverse)
	except Exception as exp:
		# This means the parameter doesn't exist
		raise Exception("Error in sortIncidentList() - parameter does not exist in incident list")
		# More detailed exception

def returnResponseByZip(zipCode):
	# Returns that response time average for the zipcode
	responseData = json.load(open(RESPONSE_BY_ZIP_DATASET))
	# Converts the json file into a python dictionary
	return responseData[str(zipCode)]
	# This returns the float value containing the average response time

def ResponseByZipAsLod():
	# This returns the response time by zip code as a list of python dictionaries
	listOfTimes = []
	# This is the list of python dictionaries containing zip code and response time
	responseData = json.load(open(RESPONSE_BY_ZIP_DATASET))
	# Converts the json file into a python dictionary
	for key, val in responseData.iteritems():
		# Iterates through the values in the dictionary as a tuple containing key and value
		listOfTimes.append({"Zip": key, "Response": val})
		# Converts those tuples to a python dictionary and appends it to the list
	return sorted(listOfTimes, key=itemgetter("Response"))
	# Returns the list of sorted python dictionaries

def getAverageByLatLong(point, param, radius=.3, skipZero=False):
	# This returns the average of a certain param by lat long
	# Radius is equal to .3, which is equal to nearby locations
	incidentList = incidentsNearLatLng(point, radius)
	# This gets all instances within a certain radius of long lat
	valueList = returnListOfParam(incidentList, param)
	# This is a raw list of values taken from that incident list
	return averageValue(valueList, forceSkip=True, skipZero=skipZero)
	# This returns a float value indicating the average of all values

def returnIncidentsByTime(timestamp, parameter="received_timestamp", minRange=15, incidentList=None, timeFormat="%H:%M"):
	# Parameter is equal to dict key, equalsValue is the value
	# Returns all instances where one dict value matches another dict value
	# Ie: parameter = "received_timestamp"
	# equalsValue = 2018-01-24 17:36:16.000000 UTC +- minRange
	# Timestamp in the format 8:15, etc.
	timeStamp = datetime.strptime(timestamp, timeFormat)
	# Converts the timestamp string into a datetime object
	returnValues = []
	# This will be the list of incidents that are returned to the user
	if incidentList == None:
		# Means that the function wasn't called with a predefined list
		incidentList = readDataset()
		# Reads full incident list
	for incident in incidentList:
		# Loops through all incidents
		try:
			timeVal = extractTimeVal(str(incident[parameter]))
			# timeVal is equal to a column containing time
			dateTimeParam = (timeVal - timeStamp)
			# Converts this difference into a datetime object
			if dateTimeParam.seconds < (60*minRange):
				# Seeing if the time difference is less than minRange
				returnValues.append(incident)
				# Appends incident value to the list of data that is returned
		except Exception as exp:
			# This means the parameter is not in the incident dict
			print exp
			# More detailed just in case exp is different
			raise Exception("Parameter in returnIncidentsByParam() is not valid")
			# More detailed exception
	return returnValues
	# Return type is a List of dict values

def ReturnIncidentByLocationAndTime(timestamp, point, param, minRange=30, radius=.5):
	# Returns incidents during a time period within a certain radius
	incidentList = incidentsNearLatLng(point, radius)
	# Gets all instances near a certain long lat
	incidentList = returnIncidentsByTime(timestamp, minRange=minRange, incidentList=incidentList)
	# Filters down previosu incident list by time
	listOfParam = returnListOfParam(incidentList, param)
	# Returns the list of paramters
	return averageValue(listOfParam, forceSkip=True, skipZero=False)
	# Returns the average of those parameters

def genHTMLDescription(incident):
	# This generates an html description for the instance
	if incident["priority"] == "2":
		htmlVal = "<center><h1><i>Non-Emergency Incident</i></h1></center>"
	else:
		htmlVal = "<center><h1><i>Emergency Incident</i></h1></center>"
	# This is the top val in the popup
	if incident["responseTime"] != 0:
		# Checks to see if the response time is valid or not
		htmlVal += "<b>Response Time</b>: {}<br>".format(incident["responseTime"])
	else:
		# This means the response time is invalid
		htmlVal += "<b>Response Time</b>: {}<br>".format("Unknown")
	# Adds response time to the popup
	htmlVal += "<b>Priority</b>: {}<br>".format(incident["priority"])
	# Adds priority to the popup
	return htmlVal
	# Returns html val as a string

def genInfoFromLatLng(lat, lng, radius=.1):
	# Generates a brief amount of into from longitude and latitude
	data = {"lng": lng, "lat": lat}
	# Data is the python dict that will hold all the data
	data["address"] = coordToAddress((lng, lat))
	# This generates a string containing the address for these long lat points
	nearbyInstances = incidentsNearLatLng((float(lng), float(lat)), radius=radius)
	# Instances that have taken place nearby
	data['nearby'] = len(nearbyInstances)
	# This is the amount of instances nearby
	data["frequency"] = (float(data["nearby"]) / 11.0)
	# This is the amount of calls per day
	responseTime = returnListOfParam(nearbyInstances, 'responseTime')
	# This is a list of response times near that long lat
	data["averageResponseTime"] = averageValue(responseTime, forceSkip=True, skipZero=True)
	# This calculates the average response time
	data["nearestFireDepartment"] = findNearestFireDepartment((float(lng), float(lat)))
	# This is the nearest fire department
	data["nearestHospital"] = findNearestHospital((float(lng), float(lat)))
	# This is the nearest hospital
	return data

def grabIncidentByLocation(incidentList, point):
	listOfVals = []
	# This will hold the list of vals that contain that point
	for value in incidentList:
		# Iterates through all the items in incidentList
		if str(point) in str(value):
			# This means the point is in the incident value
			listOfVals.append(value)
			# Adds the python dict to the new list
	return listOfVals
	# This returns a smaller python list

def removeDuplicateLocations(incidentList):
	# This creates a new list of incidents that does not contain more than one incident per long lat
	newIncidentList = []
	# Removes non-unique locations
	locationLists = returnListOfParam(incidentList, 'location', duplicates=False)
	# This is a list of unique locations
	for incident in incidentList:
		# Iterates through all items in the incident list
		for location in locationLists:
			# Iterates through all locations present in the incident list
			if str(location) in str(incident):
				# This means the incident happened at one of the locations
				newIncidentList.append(incident)
				# Appends that incident to the new list
				locationLists.remove(location)
				# No longer searches for this location.
	return newIncidentList
	# This returns the new incident list without duplicates for each location

def findNearestFireDepartment(point):
	# Returns the nearest fire department given a long lat point
	locations = json.load(open(EMERGENCY_LOCATIONS_DATASET))
	# Reads the dataset containing the building locations
	distance = haversine(point, tuple(locations["FireDepartments"][0]["Location"]), miles=True)
	# Distance from fire department at index 0
	address = locations["FireDepartments"][0]["Address"]
	# Address of fire departmetn at index 0
	nearestDepartment = {"Distance": float(distance), "Address": address}
	# This sets the nearest department as the first one in the list
	for department in locations["FireDepartments"][1:]:
		# Iterates from second element to last
		distance = haversine(point, tuple(department["Location"]), miles=True)
		# This returns the distance in miles from the defined point
		if distance < nearestDepartment["Distance"]:
			# This means the distance is lower
			address = department["Address"]
			# Sets the address to the new nearest department
			nearestDepartment = {"Distance": float(distance), "Address": address}
			# Sets nearest department as new nearest department
	return nearestDepartment
	# Returns a dictionary containing the distance and address of the nearest department

def findNearestHospital(point):
	# Returns the nearest hospital given a long lat point
	locations = json.load(open(EMERGENCY_LOCATIONS_DATASET))
	# Reads the dataset containing the building locations
	distance = haversine(point, tuple(locations["Hospitals"][0]["Location"]), miles=True)
	# Distance from hospital at index 0
	address = locations["Hospitals"][0]["Address"]
	# Address of hospital at index 0
	nearestDepartment = {"Distance": float(distance), "Address": address}
	# This sets the nearest hospital as the first one in the list
	for department in locations["Hospitals"][1:]:
		# Iterates from second element to last
		distance = haversine(point, tuple(department["Location"]), miles=True)
		# This returns the distance in miles from the defined point
		if distance < nearestDepartment["Distance"]:
			# This means the distance is lower
			address = department["Address"]
			# Sets the address to the new nearest hospital
			nearestDepartment = {"Distance": float(distance), "Address": address}
			# Sets nearest hospital as new nearest hospital
	return nearestDepartment
	# Returns a dictionary containing the distance and address of the nearest hospital

def convertSecondsToMinString(seconds):
	# This converts a float containing seconds into a string containing minutes
	return humanfriendly.format_timespan(seconds)
	# Converts it to the format of x minutes and x seconds



# returnListOfParam((returnIncidentsByParam("zipcode_of_incident", 94108)), "available_timestamp")
if __name__ == '__main__':
	'''incidentList = readDataset()
	# Returns all incidents taking place in 94108
	#returnListOfParam(incidentList, ""
	#for var in sortIncidentList(incidentList, "responseTime")[:10]:
	#	print var["responseTime"]
	param = "location"
	a = returnListOfParam(incidentList, param, duplicates=True)
	b = returnListOfParam(incidentList, param, duplicates=False)
	print len(a)
	print len(b)
	info = []
	for var in b:
		info.append({"Location": var, "Count": len(re.findall(var, str(a)))})
	print sorted(info, key=itemgetter("Count"), reverse=True)[:10]'''
	#print getAverageByLatLong((37.77444199483868, -122.5046792231959), "priority")
	#print len(returnIncidentsByTime("9:15"))
	#print guessIncidentType("12:15", (37.77444199483868, -122.5046792231959), "responseTime")
	#print ReturnIncidentByLocationAndTime("12:15", (37.78868610000001, -122.40385309999999), "priority", minRange=120)
	pass
