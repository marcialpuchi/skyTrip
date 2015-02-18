import json
import urllib2
import urllib
import re
import sys
import time
import datetime 
import itertools
from flask import jsonify
apiKey = open("skyscanner.txt",'r').read()

# Global vars:
AUTOSUGGEST_URL = "http://partners.api.skyscanner.net/apiservices/autosuggest/v1.0//GB/GBP/en-GB"
# e. g. http://www.skyscanner.net/dataservices/geo/v1.0/autosuggest/uk/en/edinb
SKYSCANNER_URL = "http://partners.api.skyscanner.net/apiservices/browsedates/v1.0/GB/GBP/en-GB/"
# e. g. http://partners.api.skyscanner.net/apiservices/browsedates/v1.0/GB/GBP/en-GB/vno/edi/130419
ROUTEDATA_URL = "http://www.skyscanner.net/dataservices/routedate/v2.0/"
# e. g. http://www.skyscanner.net/dataservices/routedate/v2.0/a00765d2-7a39-404b-86c0-e8d79cc5f7e3
SUGGESTIONS_URL = "http://partners.api.skyscanner.net/apiservices/browsedates/v1.0/GB/GBP/en-GB/"

LIVE_PRICE_URL = "http://partners.api.skyscanner.net/apiservices/pricing/v1.0/"
# e. g. http://www.skyscanner.net/db.ashx?ucy=UK&lid=en&ccy=GBP&fp=KAUN&tp=EDIN&dd=20130410

def get_list_of_codes_from_cities(list_of_cities):
	list_of_codes = []
	for city in list_of_cities:
		CityId = str(autosuggest_place(city))
		list_of_codes.append(CityId)
	return list_of_codes


def permute(list_of_codes):
	return list(itertools.permutations(list_of_codes,2))

def autosuggest_place(str_city):
	url = AUTOSUGGEST_URL+ "?query="+str_city+ "&apikey=" + apiKey
   	data= json.load(urllib2.urlopen(url))
   	return data['Places'][0]['CityId'][:3]
'''
Cached data
'''


def fetch_prices(orig,dest,date,date2):
  print orig,dest,date
  input_from = orig+ "/"
  input_to = dest+ "/"
  date_from = date #+ "/"
  date_to   =""# date2
  url = SKYSCANNER_URL+ input_from + input_to + date_from+ date_to + "?apikey=" + apiKey
  print url
  data= json.load(urllib2.urlopen(url))
  return data


def json_to_manageable(json_file):
	carriers = json_file['Carriers']
	quotes = json_file['Quotes']
	dates = json_file['Dates']
	places = json_file['Places']
	outbound = dates['OutboundDates']

	'Carriers Dictionary'
	m_carriers = {}
	for carrier in carriers:
		m_carriers[carrier['CarrierId']] = carrier['Name']

	'Places Dictionary'
	m_places = {}
	for place in places:
		m_places[place['PlaceId']] = (place['IataCode'],place['Name'],place['CountryName'])


	'Quotes Dictionary'
	m_quotes = {}
	for quote in quotes:
		airlines = quote['OutboundLeg']['CarrierIds']
		m_airlines = []
		for v in airlines:
			m_airlines.append(m_carriers[v])
		m_quotes[quote['QuoteId']] = {'Price': quote['MinPrice'], 'Direct': quote['Direct'],'Airlines':m_airlines}
	
	'Dates Dictionary'
	m_dict = {}
	for date in outbound:
		for quote in [m_quotes[x] for x in date['QuoteIds']]:
			if quote['Price'] == date['Price']:
				m_dict[date['PartialDate']] = quote
				break

	return m_dict


 	

def fetch_for_month(city_codes,month):
	possible_flights = permute(city_codes)
	result = {}
	for city in city_codes:
		result[city] = {}

	for flight in possible_flights:
		orig = flight[0]
		dest = flight[1]
		json_responce = fetch_prices(orig,dest,month,month)
		flights_for_month = json_to_manageable(json_responce)
		result[orig][dest] = flights_for_month

	return result


'''
LIVE DATA
'''



def create_session_and_get_url(place_id_from, place_id_to, date):
   
	data = {}
	data['originplace'] = place_id_from + "-sky"
	data['destinationplace'] = place_id_to + "-sky"
	data['outbounddate'] = date
	data['country'] = "GB"
	data['currency'] = "GBP"
	data['locale'] = "en-GB"
	data['apikey'] = apiKey
	data['adults'] = 1
	url_encoded = urllib.urlencode(data)
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'

	headers = { 'Accept' : "application/json",
				'user_agent' : user_agent,
				'Content-Type': "application/x-www-form-urlencoded"
				}


	req = urllib2.Request(url =LIVE_PRICE_URL, data = url_encoded, headers = headers)
	
	
	response = urllib2.urlopen(req)
	
	response_headers = response.info().headers
	for string in response_headers:
		if string[:8] == "Location":
			session_key = string[10:-2]
			 
	if not session_key:
		print "No data found for this date"
		sys.exit(4)

	return session_key


	
def fetch_live_prices(orig,dest,date):
	followUrl = create_session_and_get_url(orig,dest,date)
	new_url = followUrl+ "?apiKey=" + apiKey
	#headers
	print new_url
	headers = {'Accept': 'application/json'}
	response = urllib2.urlopen(new_url+'&stops=0')
	data = response.read()
	
	return json.loads(data)



def live_to_json(json_file):
	print json_file
	carriers = json_file['Carriers']
	itineraries = json_file['Itineraries']
	agents = json_file['Agents']
	places = json_file['Places']
	legs = json_file['Legs']
	segments = json_file['Segments']

	'Carriers Dictionary'
	m_carriers = {}
	for carrier in carriers:
		m_carriers[carrier['Id']] = (carrier['Name'],carrier['ImageUrl'])

	'Places Dictionary'
	m_places = {}
	for place in places:
		m_places[place['Id']] = place['Name']

	m_agents = {}
	for agent in agents:
		m_places[agent['Id']] = agent['Name']

	
	live_price = itineraries[0]['PricingOptions'][0]['Price']
	DeeplinkUrl = itineraries[0]['PricingOptions'][0]['DeeplinkUrl']
	OutboundLegId = itineraries[0]['OutboundLegId']
	leg = legs[0]
	origin = m_places[leg['OriginStation']]
	dest = m_places[leg['DestinationStation']]
	duration = leg['Duration']
	arrival_time = leg['Arrival']
	departure_time = leg['Departure']
	carrier_name = m_carriers[leg['Carriers'][0]][0]
	carrier_logo_url = m_carriers[leg['Carriers'][0]][1]
	flight_details = {
	'price' : live_price,
	'deeplink' :DeeplinkUrl,
	'origin' : origin,
	'destination' : dest,
	'duration' : duration,
	'arrival_time' : arrival_time,
	'departure_time' : departure_time,
	'carrier_name': carrier_name,
	'carrier_logo_url' : carrier_logo_url
	}
	return flight_details



def get_live_prices_for_route(route):
	key = route['Routes'][0].keys()[0]
	list_of_legs = route['Routes'][0][key]
	
	
	to_get_live = []
	for leg in list_of_legs:
		to_get_live.append(leg['Leg']['leg_data'])

	live_data = {'data':[],'TotalCost': 0}
	for flight in to_get_live:
		print flight
		orig = flight['Orig']
		dest = flight['Dest']
		date = flight['Date']
		live_d_json = live_to_json(fetch_live_prices(orig,dest,date))
		live_data['TotalCost'] += live_d_json['price']
		live_data['data'].append(live_d_json)

	return live_data



















sample_route = {
  "Routes": [
    {
      "Route3": [
        {
          "LegPrice": 179,
          "Carrier": [
            "British Airways"
          ],
          "Leg": {
            "leg_data": {
              "leg": 1,
              "Date": "2015-03-02",
              "Dest": "lhr",
              "Orig": "edi"
            }
          }
        },
        {
          "LegPrice": 89,
          "Carrier": [
            "Ukraine International"
          ],
          "Leg": {
            "leg_data": {
              "Date": "2015-03-05",
              "Dest": "lhr",
              "Orig": "cdg"
            },
            "leg": 2
          }
        },
        {
          "LegPrice": 368,
          "Carrier": [
            "Norwegian"
          ],
          "Leg": {
            "leg_data": {
              "Date": "2015-03-08",
              "Dest": "edi",
              "Orig": "stn"
            },
            "leg": 3
          }
        }
      ],
      "Cost": 636
    },
    {
      "Cost": 715,
      "Route5": [
        {
          "LegPrice": 452,
          "Carrier": [
            "Aer Lingus"
          ],
          "Leg": {
            "leg_data": {
              "Date": "2015-03-02",
              "Dest": "jfk",
              "Orig": "edi"
            },
            "leg": 1
          }
        },
        {
          "LegPrice": 190,
          "Carrier": [
            "Norwegian"
          ],
          "Leg": {
            "leg_data": {
              "Date": "2015-03-05",
              "Dest": "lon",
              "Orig": "jfk"
            },
            "leg": 2
          }
        },
        {
          "LegPrice": 73,
          "Carrier": [
            "easyJet"
          ],
          "Leg": {
            "leg_data": {
              "Date": "2015-03-09",
              "Dest": "lca",
              "Orig": "lon"
            },
            "leg": 3
          }
        }
      ]
    },
    {
      "Cost": 710,
      "Route6": [
        {
          "LegPrice": 452,
          "Carrier": [
            "Aer Lingus"
          ],
          "Leg": {
            "leg_data": {
              "Date": "2015-03-02",
              "Dest": "jfk",
              "Orig": "edi"
            },
            "leg": 1
          }
        },
        {
          "LegPrice": 217,
          "Carrier": [
            "Norwegian"
          ],
          "Leg": {
            "leg_data": {
              "Date": "2015-03-06",
              "Dest": "lca",
              "Orig": "jfk"
            },
            "leg": 2
          }
        },
        {
          "LegPrice": 41,
          "Carrier": [
            "easyJet"
          ],
          "Leg": {
            "leg_data": {
              "Date": "2015-03-09",
              "Dest": "lon",
              "Orig": "lca"
            },
            "leg": 3
          }
        }
      ]
    }
  ]
}

     
sample_json_live ={
  "SessionKey": "02d01c65fea6417290b2c022050467ec_ecilpojl_B73C7A982F3FE4B0422B4F8188A52B5C",
  "Query": {
    "Country": "GB",
    "Currency": "GBP",
    "Locale": "en-GB",
    "Adults": 1,
    "Children": 0,
    "Infants": 0,
    "OriginPlace": "13554",
    "DestinationPlace": "13445",
    "OutboundDate": "2015-02-25",
    "LocationSchema": "Default",
    "CabinClass": "Economy",
    "GroupPricing": False
  },
  "Status": "UpdatesPending",
  "Itineraries": [
    {
      "OutboundLegId": "13554-1502251145-BA-0-13445-1502251820",
      "PricingOptions": [
        {
          "Agents": [
            2365707
          ],
          "QuoteAgeInMinutes": 1,
          "Price": 147.8,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2febuk%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d147.80%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26deeplink_ids%3d4518e2a494fd0fdebc3bd0d20c33eec3%26q_datetime_utc%3d2015-02-18T18%3a12%3a08"
        },
        {
          "Agents": [
            4499211
          ],
          "QuoteAgeInMinutes": 1,
          "Price": 147.81,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2fxpuk%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d147.81%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26deeplink_ids%3dc4e1a569a006218d071edf6cc3eee480%26q_datetime_utc%3d2015-02-18T18%3a12%3a15"
        },
        {
          "Agents": [
            3874827
          ],
          "QuoteAgeInMinutes": 1,
          "Price": 148.47,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2fs1uk%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dtrue%26ticket_price%3d148.47%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26deeplink_ids%3d2f4530c36e9bc671bb4e64eca5e593b1%26q_datetime_utc%3d2015-02-18T18%3a12%3a10"
        },
        {
          "Agents": [
            3165195
          ],
          "QuoteAgeInMinutes": 1,
          "Price": 148.81,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2flmuk%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d148.81%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26deeplink_ids%3d409e428d263a13b5cabfb5b6055cbdff%26q_datetime_utc%3d2015-02-18T18%3a12%3a08"
        },
        {
          "Agents": [
            3503883
          ],
          "QuoteAgeInMinutes": 1,
          "Price": 151.81,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2fopuk%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d151.81%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26deeplink_ids%3d082507a0d4f9b9e785fdc0eb2088eb0e%26q_datetime_utc%3d2015-02-18T18%3a12%3a19"
        },
        {
          "Agents": [
            3496199
          ],
          "QuoteAgeInMinutes": 186,
          "Price": 163.63,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2fomeg%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d163.63%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26q_datetime_utc%3d2015-02-18T15%3a07%3a41"
        },
        {
          "Agents": [
            4056843
          ],
          "QuoteAgeInMinutes": 1,
          "Price": 164.8,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2ftpuk%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d164.80%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26deeplink_ids%3dcd7960b4a8e50dbc35feaf8cad8211f6%26q_datetime_utc%3d2015-02-18T18%3a12%3a08"
        },
        {
          "Agents": [
            4061456
          ],
          "QuoteAgeInMinutes": 1,
          "Price": 164.81,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2ftrup%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d164.81%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26deeplink_ids%3dd23c20b93ad7a3d9a6a741682ac92e41%26q_datetime_utc%3d2015-02-18T18%3a12%3a05"
        },
        {
          "Agents": [
            3367894
          ],
          "QuoteAgeInMinutes": 1,
          "Price": 164.81,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2fnetf%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d164.81%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26deeplink_ids%3d506d397df99ccc87c2051359188be87c%26q_datetime_utc%3d2015-02-18T18%3a12%3a05"
        },
        {
          "Agents": [
            2370315
          ],
          "QuoteAgeInMinutes": 1,
          "Price": 168.02,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2feduk%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d168.02%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26deeplink_ids%3dc9ce9be62e9ba27bde9eac06947f406f%26q_datetime_utc%3d2015-02-18T18%3a12%3a19"
        },
        {
          "Agents": [
            2043147
          ],
          "QuoteAgeInMinutes": 1,
          "Price": 168.2,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2fbfuk%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d168.20%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26deeplink_ids%3dfe60a555300bb01ea2e06fdec55053fb%26q_datetime_utc%3d2015-02-18T18%3a12%3a06"
        },
        {
          "Agents": [
            2032127
          ],
          "QuoteAgeInMinutes": 1332,
          "Price": 175.81,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2fba__%2f1%2f13554.13445.2015-02-25%2fair%2fairli%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d175.81%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26q_datetime_utc%3d2015-02-17T20%3a01%3a19"
        },
        {
          "Agents": [
            2628363
          ],
          "QuoteAgeInMinutes": 1,
          "Price": 177.67,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2fgtuk%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d177.67%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26deeplink_ids%3d7f98e7f77eb657a26bda7fc0c7aa0dac%26q_datetime_utc%3d2015-02-18T18%3a12%3a06"
        },
        {
          "Agents": [
            3579051
          ],
          "QuoteAgeInMinutes": 1,
          "Price": 184.31,
          "DeeplinkUrl": "http://partners.api.skyscanner.net/apiservices/deeplink/v2?_cje=r0vhsHNDJGcQeeMmTIid1DTAfmjFdJeUQAvBk%2feZ%2f9A9kOIRXJqv9pSkR4pgdt9Z&url=http%3a%2f%2fwww.apideeplink.com%2ftransport_deeplink%2f4.0%2fUK%2fen-gb%2fGBP%2fpack%2f1%2f13554.13445.2015-02-25%2fair%2ftrava%2fflights%3fitinerary%3dflight%7c-32480%7c662%7c13554%7c2015-02-25T11%3a45%7c13445%7c2015-02-25T18%3a20%26carriers%3d-32480%26passengers%3d1%2c0%2c0%26channel%3ddataapi%26cabin_class%3deconomy%26facilitated%3dfalse%26ticket_price%3d184.31%26is_npt%3dfalse%26client_id%3dskyscanner_website%26request_id%3dd3594949-a1fb-4709-96a3-8fbac7d6820a%26deeplink_ids%3d6e27f26f1ac9b96f82d3177ad948366d%26q_datetime_utc%3d2015-02-18T18%3a12%3a07"
        }
      ],
      "BookingDetailsLink": {
        "Uri": "/apiservices/pricing/v1.0/02d01c65fea6417290b2c022050467ec_ecilpojl_B73C7A982F3FE4B0422B4F8188A52B5C/booking",
        "Body": "OutboundLegId=13554-1502251145-BA-0-13445-1502251820&InboundLegId=",
        "Method": "PUT"
      }
    }
  ],
  "Legs": [
    {
      "Id": "13554-1502251145-BA-0-13445-1502251820",
      "SegmentIds": [
        1
      ],
      "OriginStation": 13554,
      "DestinationStation": 13445,
      "Departure": "2015-02-25T11:45:00",
      "Arrival": "2015-02-25T18:20:00",
      "Duration": 275,
      "JourneyMode": "Flight",
      "Stops": [],
      "Carriers": [
        881
      ],
      "OperatingCarriers": [
        881
      ],
      "Directionality": "Outbound",
      "FlightNumbers": [
        {
          "FlightNumber": "662",
          "CarrierId": 881
        }
      ]
    }
  ],
  "Segments": [
    {
      "Id": 1,
      "OriginStation": 13554,
      "DestinationStation": 13445,
      "DepartureDateTime": "2015-02-25T11:45:00",
      "ArrivalDateTime": "2015-02-25T18:20:00",
      "Carrier": 881,
      "OperatingCarrier": 881,
      "Duration": 275,
      "FlightNumber": "662",
      "JourneyMode": "Flight",
      "Directionality": "Outbound"
    }
  ],
  "Carriers": [
    {
      "Id": 881,
      "Code": "BA",
      "Name": "British Airways",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/BA.png",
      "DisplayCode": "BA"
    },
    {
      "Id": 1427,
      "Code": "MS",
      "Name": "EgyptAir",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/MS.png",
      "DisplayCode": "MS"
    },
    {
      "Id": 1523,
      "Code": "OS",
      "Name": "Austrian Airlines",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/OS.png",
      "DisplayCode": "OS"
    },
    {
      "Id": 1710,
      "Code": "SN",
      "Name": "Brussels Airlines",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/SN.png",
      "DisplayCode": "SN"
    },
    {
      "Id": 819,
      "Code": "A3",
      "Name": "Aegean Airlines",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/A3.png",
      "DisplayCode": "A3"
    },
    {
      "Id": 858,
      "Code": "AZ",
      "Name": "Alitalia",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/AZ.png",
      "DisplayCode": "AZ"
    },
    {
      "Id": 1384,
      "Code": "LX",
      "Name": "Swiss",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/LX.png",
      "DisplayCode": "LX"
    },
    {
      "Id": 1413,
      "Code": "ME",
      "Name": "MEA",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/ME.png",
      "DisplayCode": "ME"
    },
    {
      "Id": 1325,
      "Code": "KM",
      "Name": "Air Malta",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/KM.png",
      "DisplayCode": "KM"
    },
    {
      "Id": 1806,
      "Code": "UN",
      "Name": "Transaero Airlines",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/UN.png",
      "DisplayCode": "UN"
    },
    {
      "Id": 1126,
      "Code": "GF",
      "Name": "Gulf Air",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/GF.png",
      "DisplayCode": "GF"
    },
    {
      "Id": 1324,
      "Code": "KL",
      "Name": "KLM",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/KL.png",
      "DisplayCode": "KL"
    },
    {
      "Id": 1618,
      "Code": "QR",
      "Name": "Qatar Airways",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/QR.png",
      "DisplayCode": "QR"
    },
    {
      "Id": 1717,
      "Code": "SU",
      "Name": "Aeroflot",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/SU.png",
      "DisplayCode": "SU"
    },
    {
      "Id": 1385,
      "Code": "LY",
      "Name": "EL AL Israel Airlines",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/LY.png",
      "DisplayCode": "LY"
    },
    {
      "Id": 1035,
      "Code": "EK",
      "Name": "Emirates",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/EK.png",
      "DisplayCode": "EK"
    },
    {
      "Id": 834,
      "Code": "AB",
      "Name": "Air Berlin",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/AB.png",
      "DisplayCode": "AB"
    },
    {
      "Id": 1658,
      "Code": "RJ",
      "Name": "Royal Jordanian",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/RJ.png",
      "DisplayCode": "RJ"
    },
    {
      "Id": 1242,
      "Code": "IZ",
      "Name": "arkia",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/IZ.png",
      "DisplayCode": "IZ"
    },
    {
      "Id": 1218,
      "Code": "IB",
      "Name": "Iberia",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/IB.png",
      "DisplayCode": "IB"
    },
    {
      "Id": 1707,
      "Code": "SK",
      "Name": "SAS",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/SK.png",
      "DisplayCode": "SK"
    },
    {
      "Id": 1044,
      "Code": "ET",
      "Name": "Ethiopian Airlines",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/ET.png",
      "DisplayCode": "ET"
    },
    {
      "Id": 1755,
      "Code": "TK",
      "Name": "Turkish Airlines",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/TK.png",
      "DisplayCode": "TK"
    },
    {
      "Id": 1505,
      "Code": "OA",
      "Name": "Olympic Air",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/OA.png",
      "DisplayCode": "OA"
    },
    {
      "Id": 838,
      "Code": "AF",
      "Name": "Air France",
      "ImageUrl": "http://s1.apideeplink.com/images/airlines/AF.png",
      "DisplayCode": "AF"
    }
  ],
  "Agents": [
    {
      "Id": 2045393,
      "Name": "BudgetAir",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/bgta.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "BookingNumber": "02033184060",
      "Type": "TravelAgent"
    },
    {
      "Id": 3503883,
      "Name": "Opodo",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/opuk.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "Type": "TravelAgent"
    },
    {
      "Id": 2370315,
      "Name": "eDreams",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/eduk.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "Type": "TravelAgent"
    },
    {
      "Id": 3874827,
      "Name": "via Skyscanner",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/s1uk.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "Type": "TravelAgent"
    },
    {
      "Id": 4061456,
      "Name": "travelup",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/trup.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "BookingNumber": "02071184747",
      "Type": "TravelAgent"
    },
    {
      "Id": 3496199,
      "Name": "omegaflightstore.com",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/omeg.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": False,
      "Type": "TravelAgent"
    },
    {
      "Id": 2628363,
      "Name": "GotoGate",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/gtuk.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "Type": "TravelAgent"
    },
    {
      "Id": 4056843,
      "Name": "Tripsta",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/tpuk.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "Type": "TravelAgent"
    },
    {
      "Id": 2365707,
      "Name": "ebookers",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/ebuk.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "Type": "TravelAgent"
    },
    {
      "Id": 4499211,
      "Name": "Expedia",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/xpuk.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "Type": "TravelAgent"
    },
    {
      "Id": 3367894,
      "Name": "netflights.com",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/netf.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "Type": "TravelAgent"
    },
    {
      "Id": 2043147,
      "Name": "Bravofly",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/bfuk.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "BookingNumber": "0203 499 5179",
      "Type": "TravelAgent"
    },
    {
      "Id": 3579051,
      "Name": "Travelpack",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/pack.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "BookingNumber": "02085854043",
      "Type": "TravelAgent"
    },
    {
      "Id": 3165195,
      "Name": "lastminute.com",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/lmuk.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "Type": "TravelAgent"
    },
    {
      "Id": 3961811,
      "Name": "Swiss",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/swis.png",
      "Status": "UpdatesPending",
      "OptimisedForMobile": True,
      "BookingNumber": "+448456010956",
      "Type": "Airline"
    },
    {
      "Id": 2032127,
      "Name": "British Airways",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/ba__.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": True,
      "BookingNumber": "08444930787",
      "Type": "Airline"
    },
    {
      "Id": 1929573,
      "Name": "Aegean Airlines",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/aege.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": False,
      "BookingNumber": "8011120000",
      "Type": "Airline"
    },
    {
      "Id": 3247716,
      "Name": "Air Malta",
      "ImageUrl": "http://s1.apideeplink.com/images/websites/malt.png",
      "Status": "UpdatesComplete",
      "OptimisedForMobile": False,
      "BookingNumber": "09061030012",
      "Type": "Airline"
    }
  ],
  "Places": [
    {
      "Id": 13554,
      "ParentId": 4698,
      "Code": "LHR",
      "Type": "Airport",
      "Name": "London Heathrow"
    },
    {
      "Id": 13445,
      "ParentId": 4455,
      "Code": "LCA",
      "Type": "Airport",
      "Name": "Larnaca"
    },
    {
      "Id": 4698,
      "ParentId": 247,
      "Code": "LON",
      "Type": "City",
      "Name": "London"
    },
    {
      "Id": 4455,
      "ParentId": 109,
      "Code": "LCA",
      "Type": "City",
      "Name": "Larnaca"
    },
    {
      "Id": 247,
      "Code": "GB",
      "Type": "Country",
      "Name": "United Kingdom"
    },
    {
      "Id": 109,
      "Code": "CY",
      "Type": "Country",
      "Name": "Cyprus"
    }
  ],
  "Currencies": [
    {
      "Code": "GBP",
      "Symbol": "s",
      "ThousandsSeparator": ",",
      "DecimalSeparator": ".",
      "SymbolOnLeft": True,
      "SpaceBetweenAmountAndSymbol": False,
      "RoundingCoefficient": 0,
      "DecimalDigits": 2
    },
    {
      "Code": "EUR",
      "Symbol": ".",
      "ThousandsSeparator": ".",
      "DecimalSeparator": ",",
      "SymbolOnLeft": False,
      "SpaceBetweenAmountAndSymbol": True,
      "RoundingCoefficient": 0,
      "DecimalDigits": 2
    }
  ]
}