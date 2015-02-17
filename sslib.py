import json
import urllib2
import re
import sys
import time
import sk
import datetime 
import itertools
apiKey = open("skyscanner.py",'r').read()

# Global vars:
AUTOSUGGEST_URL = "http://partners.api.skyscanner.net/apiservices/autosuggest/v1.0//GB/GBP/en-GB"
# e. g. http://www.skyscanner.net/dataservices/geo/v1.0/autosuggest/uk/en/edinb
SKYSCANNER_URL = "http://partners.api.skyscanner.net/apiservices/browsedates/v1.0/GB/GBP/en-GB/"
# e. g. http://partners.api.skyscanner.net/apiservices/browsedates/v1.0/GB/GBP/en-GB/vno/edi/130419
ROUTEDATA_URL = "http://www.skyscanner.net/dataservices/routedate/v2.0/"
# e. g. http://www.skyscanner.net/dataservices/routedate/v2.0/a00765d2-7a39-404b-86c0-e8d79cc5f7e3
SUGGESTIONS_URL = "http://partners.api.skyscanner.net/apiservices/browsedates/v1.0/GB/GBP/en-GB/"
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


def fetch_prices(orig,dest,date,date2):
	input_from = orig+ "/"
   	input_to = dest+ "/"
   	date_from = date #+ "/"
   	date_to   =""# date2
   	url = SKYSCANNER_URL+ input_from + input_to + date_from+ date_to + "?apikey=" + apiKey
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






     