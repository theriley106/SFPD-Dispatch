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
			tempInfo["priority"] = 4
			# Sets it to 4, which is basically "Unknown"
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

def returnHousholdIncome(zipCode):
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

def incidentsNearLatLng(point, radius):
	# Returns a list of instances within radius of a long lat point
	dataset = readDataset()
	# Reads the dataset
	for var in dataset:
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

def returnIncidentsByParam(parameter, equalsValue):
	# Parameter is equal to dict key, equalsValue is the value
	# Returns all instances where one dict value matches another dict value
	# Ie: parameter = "zipcode_of_incident"
	# equalsValue = "94108"
	# Would return all incidents where incident["zipcode_of_incident"] == "94108"
	returnValues = []
	# This will be the list of incidents that are returned to the user
	for incident in readDataset():
		# Loops through all incidents
		try:
			# Try -> Except to catch invalid parameter
			if str(incident[parameter]) == str(equalsValue):
				# Converting both to strings, ignoring data type
				returnValues.append(incident)
				# Appends incident value to the list of data that is returned
		except:
			# This means the parameter is not in the incident dict
			raise Exception("Parameter in returnIncidentsByParam() is not valid")
			# More detailed exception
	return returnValues
	# Return type is a List of dict values

def returnListOfParam(incidentList, param):
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
		except:
			# This means the parameter is not in the incident dict
			raise Exception("Parameter in returnListOfParam() is not valid")
			# More detailed exception
	return returnValues
	# Return type is a List

def averageValue(listOfValues):
	# Returns an average for all values in a list
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
		print exp
		raise Exception("Error in sortIncidentList() - parameter does not exist in incident list")
		# More detailed exception



# returnListOfParam((returnIncidentsByParam("zipcode_of_incident", 94108)), "available_timestamp")
if __name__ == '__main__':
	incidentList = readDataset()
	# Returns all incidents taking place in 94108
	#returnListOfParam(incidentList, ""
	for var in sortIncidentList(incidentList, "responseTime")[:10]:
		print var["responseTime"]
