import json
import interactions

hospitalList = [u'2425 Geary Blvd', u'2425 Geary Blvd', u'1600 Divisadero St', u'1600 Divisadero St', u'3700 California St', u'3700 California St', u'2333 Buchanan St', u'2333 Buchanan St', u'450 Stanyan St', u'450 Stanyan St', u'Castro and Duboce Streets', u'Castro and Duboce Streets', u'505 Parnassus Avenue', u'505 Parnassus Avenue', u'900 Hyde St', u'900 Hyde St', u'1001 Potrero Ave', u'1001 Potrero Ave', u'3555 Cesar Chavez', u'3555 Cesar Chavez', u'845 Jackson St', u'845 Jackson St', u'1200 El Camino Real', u'1200 El Camino Real']
hospitalNames = [u'Kaiser Permanente San Francisco Medical Center', u'UCSF Medical Center at Mount Zion', u'California Pacific Medical Center - California Campus', u'California Pacific Medical Center - Pacific Campus', u"St. Mary's Medical Center", u'California Pacific Medical Center - Davies Campus', u'UCSF Medical Center at Parnassus', u'Saint Francis Memorial Hospital', u'San Francisco General Hospital', u"California Pacific Medical Center - Saint Luke's", u'Chinese Hospital', u'Kaiser Permanente South San Francisco Medical Center', u'Alta Bates Summit Medical Center - Summit', u'Seton Medical Center', u'Kaiser Permanente Richmond Medical Center', u'Kaiser Permanente Oakland Medical Center', u'Mills-Peninsula Medical Center', u'Alta Bates Summit Medical Center - Alta Bates Camp', u'Marin General Hospital', u'Mills Health Center', u'Alameda Hospital', u'Kaiser Foundation Hospital - San Leandro', u'Kaiser Permanente San Rafael Medical Center']

fdList = [u'935 Folsom at 5th Street', u'1340 Powell Street at Broadway', u'1067 Post Street at Polk Street ', u'449 Mission Rock at 3rd Street ', u'1301 Turk Street at Webster Street', u'135 Sanchez Street at Henry Street', u'2300 Folsom Street at 19th Street', u'36 Bluxome Street at 4th Street', u'2245 Jerrold Avenue at Upton Street', u'655 Presidio Avenue at Bush Street', u'3880 26th Street at Church Street', u'1145 Stanyan Street at Grattan Street', u'530 Sansome Street at Washington Street', u'551 26th Avenue at Geary Boulevard', u'1000 Ocean Avenue at Phelan Avenue', u'2251 Greenwich Street at Fillmore Street', u'1295 Shafter Avenue at Ingalls Street', u'1935 32nd Avenue at Ortega Street', u'390 Buckingham Way at Winston Street', u'285 Olympia Way at Clarendon Avenue', u'1443 Grove Street at Broderick Street', u'1290 16th Avenue at Irving Street', u'1348 45th Avenue at Judah Street', u'100 Hoffman Avenue at Alvarado Street', u'3305 3rd Street at Cargo Way', u'80 Digby Street at Addison Street', u'1814 Stockton Street at Greenwich Street', u'299 Vermont Street at 16th Street', u'441 12th Avenue at Geary Boulevard', u'194 Park Street at Holly Park Circle', u'8 Capital Street at Broad Street', u'499 41st Avenue at Geary Boulevard', u'Pier 22\xbd, The Embarcadero at Harrison Street', u'109 Oak Street at Franklin Street', u'798 Wisconsin Street at 22nd Street', u'2150 California Street at Laguna Street', u'1091 Portola Drive at Miraloma Drive', u'2155 18th Avenue at Rivera Street', u'1325 Leavenworth Street at Jackson Street', u'2430 San Bruno Avenue at Silver Avenue', u'720 Moscow Street at France Avenue', u'1298 Girard Street at Wilde Avenue', u'800 Avenue I at 10th Street, Treasure Island', u'1415 Evans Avenue at Mendell Street', u'218 Lincoln Blvd at Keyes Avenue']
pdList =[u'766 Vallejo Street', u'1251 3rd Street', u'201 Williams Avenue', u'630 Valencia Street', u'1125 Fillmore Street', u'1899 Waller Street', u'461 6th Avenue', u'1 Sgt. John V. Young Lane', u'2345 24th Avenue', u'301 Eddy Street']
data = {"Hospitals": [], "FireDeparments": [], "PoliceDepartments": []}

for i, address in enumerate(hospitalList):
	try:
		coords = interactions.addressToCoord(address)
		typeVal = "Hospital"
		name = hospitalNames[i]
		data["Hospitals"].append({"Type": typeVal, "Address": address, "Location": coords, "Name": name})
	except:
		print("Error")
for address in fdList:
	try:
		coords = interactions.addressToCoord(address)
		typeVal = "FireDepartment"
		data["FireDeparments"].append({"Type": typeVal, "Address": address, "Location": coords})
	except:
		print("Error")
for address in pdList:
	try:
		coords = interactions.addressToCoord(address)
		typeVal = "PoliceDepartment"
		data["PoliceDeparments"].append({"Type": typeVal, "Address": address, "Location": coords})
	except:
		print("Error")
with open('data.json', 'w') as outfile:
	json.dump(data, outfile)
