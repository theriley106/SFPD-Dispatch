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
