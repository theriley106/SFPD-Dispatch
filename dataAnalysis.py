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

def findMostFrequentLocation():
	incidentList = readDataset()
