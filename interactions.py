import csv
from haversine import haversine

MAIN_DATASET_FILE = "datasets/sfpd_dispatch_data_subset.csv"
# This is the location where the SFPD dataset is stored
UMICH_DATASET_FILE = "datasets/umichDataset.csv"
listOfTypes = []

def returnBetween(point, radius):
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

def readDataset():
	# This will convert the dataset into a format the the front end will use
	dataset = []
	# Ideally this should be  a list of JSON/python dicts for the jinja template
	datasetList = csvToList(MAIN_DATASET_FILE)
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
			tempInfo["priority"] = 4
		tempInfo["mapColor"] = getPriorityColor(tempInfo["priority"])
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
	# Data is from https://www.psc.isr.umich.edu/dis/census/Features/tract2zip/
	# University of Michigan mean household income dataset

def Status(zip):
	with open('Economics.csv', 'rb') as f:
		reader = csv.reader(f)
		lis = list(reader)
	for e in lis:
		if str(zip) in str(e):
			return int(float(str(e[1]).replace(",", '')))
