from interactions import *



'''
This is a not production ready code, but I wanted to include it anyway.
This is the code used to generate the data visualizations and analytics
in the readme
'''

def findAmountOfUniqueLocations():
	a = returnListOfParam(incidentList, param, duplicates=True)
	b = returnListOfParam(incidentList, param, duplicates=False)
	return (float(b) / float(a)) * 100

def findMostFrequentLocation(count=10):
	incidentList = readDataset()
	fullDataSet = returnListOfParam(incidentList, "location", duplicates=True)
	info = []
	for var in returnListOfParam(incidentList, "location", duplicates=False):
		info.append({"Location": var, "Count": len(re.findall(var, str(fullDataSet)))})
	return sorted(info, key=itemgetter("Count"), reverse=True)[:count]

def findAverageResponseTimeByZipCode():
	incidentList = readDataset()
	zipCodes = returnListOfParam(incidentList, "zipcode_of_incident", duplicates=False)
	print zipCodes
	for zipC in zipCodes:
		incidentList = returnIncidentsByParam("zipcode_of_incident", zipC)
		a = returnListOfParam(incidentList, "responseTime")
		print("{} - {}".format(zipC, averageValue(a, forceSkip=True)))
findAverageResponseTimeByZipCode()
