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
	if REDUCE_PROCESSING_POWER == True:
		# This means the constant is set to True
		previousSearch = checkPreviousSearch((lat, lng), radius)
		# This checks to see if this search query has already been run
		if previousSearch != None:
			# This means the dataset has already been created
			return readDataset(previousSearch)
			# Returns dataset without doing a ton of processing
	incidentList = incidentsNearLatLng((lat, lng), radius)
	# Returns incidents near that lat long
	if REDUCE_PROCESSING_POWER == True:
		# This will save the dataset locally for future searches




def saveIncidentList(incidentList, point, radius):


def extractLocationFromFile(fileName):
	# This extract long, lat, and radius from a file name
	fileName = fileName.partition("{}/".format(DATASETS_DIRECTORY))[2]
	# This only grabs the actual filename - removing directory info
	fileName = fileName.replace(".json", "")
	# This will remove .csv only if it's present
	if fileName.count("-") != 3:
		# This checks to see if the format indicates it contains lat lng radius
		return None
		# It will return None if it doesn't
	else:
		# This means it does follow the {lat}-{lng}-{radius}.csv format
		lat, lng, radius = fileName.split("-")
		# Creates 3 files
		return {"Latitude": lat, "Longitude": lng, "Radius": radius, "Filename": fileName}
		# Returns Python dictionary

def returnLatLngTuple(pythonDict):
	try:
		latitude = pythonDict["Latitude"]
		longitude = pythonDict["Longitude"]
		return (latitude, longitude)
	except:
		raise Exception("returnLatLngTuple() failed - python dictionary is not in the correct format")

def checkPreviousSearch(point, radius):
	'''
	Since incidentsNearLatLng() is extremely time consuming, the searches are saved
	as CSV, and this list of CSVs is checked upon each call to incidentsNearLatLng()
	to reduce the speed of incidents being returned
	'''
	for file in glob.glob("{}/*.json".format(DATASETS_DIRECTORY)):
		fileInfo = extractLocationFromFile(file)
		if fileInfo != None:
			if returnLatLngTuple(fileInfo) == point and radius == fileInfo["Radius"]:
				print("This has already been completed")

#print len(incidentsNearAddress("101 Post Street San Francisco, CA 94108", 2))
checkPreviousSearch(1, 1)
