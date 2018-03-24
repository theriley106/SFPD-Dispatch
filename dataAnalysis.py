from interactions import *



'''
This is a not production ready code, but I wanted to include it anyway.
This is the code used to generate the data visualizations and analytics
in the readme
'''

#class analysis(object):


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
	listOfResponseTimes = []
	incidentList = readDataset()
	zipCodes = returnListOfParam(incidentList, "zipcode_of_incident", duplicates=False)
	for zipC in zipCodes:
		incidentList = returnIncidentsByParam("zipcode_of_incident", zipC)
		a = returnListOfParam(incidentList, "responseTime")
		info = {"ZipCode": zipC, "ResponseTime": averageValue(a, forceSkip=True), "Calls": len(a)}
		listOfResponseTimes.append(info)
	return listOfResponseTimes

def getAverage(param):
	# Param has to be completely numerical
	listVal = []
	incidentList = readDataset()
	return averageValue(returnListOfParam(incidentList, param), forceSkip=True)


# Average Response Time: 484.6133
# getAverage("responseTime")

# Average Priority: 2.75377537754
# getAverage("priority")


