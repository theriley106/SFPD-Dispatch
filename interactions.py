import csv
DATASET_FILE = "datasets/sfpd_dispatch_data_subset.csv"
# This is the location where the SFPD dataset is stored

def readDataset():
	# This will convert the dataset into a format the the front end will use
	csvToList(DATASET_FILE)

def csvToList(csvFile):
	# This will return a list of rows in the csv file
	with open(csvFile, 'rb') as f:
	    reader = csv.reader(f)
	    your_list = list(reader)
