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

def getAverageCustom(incidentList, param, forceSkip=True, skipZero=False):
	# Param has to be completely numerical
	# Incident list can be custom
	return averageValue(returnListOfParam(incidentList, param), forceSkip=forceSkip, skipZero=skipZero)

def getDictParamAvgByZip(param):
	zipResponse = {}
	for zipCode in getZipCodes():
		info = returnParamByZip(zipCode, param)
		info = filter(lambda a: a != 0, info)
		# This filters out all 0 values
		val = averageValue(info, forceSkip=True)
		zipResponse[zipCode] = val
	return zipResponse

def getDistance():
	zipResponse = []
	for zipCode in getZipCodes():
		info = returnParamByZip(zipCode, 'location')
		allList = []
		for var in info:
			lng, lat = var.replace("(", "").replace(")", "").split(", ")
			allList.append(findNearestFireDepartment((float(lng), float(lat)))["Distance"])
		val = averageValue(allList, forceSkip=True)
		print("{} - {}".format(zipCode, val))
		zipResponse.append({"Zip": zipCode, "Distance": val})
	return zipResponse

# Average Response Time: 484.6133
# getAverage("responseTime")

# Average Priority: 2.75377537754
# getAverage("priority")

# Average Response time for Priority 2: 811.173981811
'''
incidentList = returnIncidentsByParam("priority", "2")
print getAverageCustom(incidentList, "responseTime", forceSkip=True, skipZero=True)
'''


# Average Respone time for Priority 3: 508.584895359
'''
incidentList = returnIncidentsByParam("priority", "3")
print getAverageCustom(incidentList, "responseTime", forceSkip=True, skipZero=True)
'''

'''
Response time per zip
{'94130': 686.8235294117648, '94131': 596.4792899408284, '94132': 622.1849710982659, '94133': 573.1824104234528, '94134': 781.4897959183673, '94114': 514.25, '94118': 510.89237668161434, '94112': 598.8969359331477, '94110': 539.4389880952381, '94111': 686.0653594771242, '94116': 604.1695906432749, '94117': 501.32214765100673, '94158': 565.6447368421053, '94115': 516.1223958333334, '94127': 2719.506329113924, '94124': 637.8574821852732, '94123': 554.7692307692307, '94122': 555.4528301886793, '94121': 577.171270718232, '94129': 933.5172413793103, '94109': 513.8826151560178, '94108': 565.6842105263158, '94103': 562.1197263397947, '94102': 547.5945437441204, '94105': 1146.5746606334842, '94104': 559.5172413793103, '94107': 599.639344262295}
'''


print getDistance()
