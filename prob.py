import sslib
import datetime
import itertools
'takes list in form below'



def possible_configs(cities_and_days,start_date,home_city):
	'''
	city_codes_with_days format
	[("edi",4),("lon",3),("jfk",3)]

	start_date format
	datetime.datetime(year=2015,month=3,day=2)

	start_date
	'''
	total_days = [x[1] for x in cities_and_days]
	total_days = sum(total_days)
	print total_days
	configs = list(itertools.permutations(cities_and_days))
	date = start_date
	end_date = start_date + datetime.timedelta(days = total_days)
	flight_plans = {}
	PermutationId = 1
	for perm in configs:
		date = start_date
		flight_plans[PermutationId] = []
		flight_plans[PermutationId].append({
											'leg': 1, 
											'Orig': home_city,
											'Date':start_date,
											'Dest':perm[0][0]
											}
											)
		i = 1
		while i < len(perm):
			timedelta = datetime.timedelta(days = perm[i][1])
			date = date+timedelta
			legName = 'leg' + str(i+1)
			flight_plans[PermutationId].append({'leg': i+1, 
												'Orig': perm[i-1][0],
												'Date':date,
												'Dest':perm[i][0]})
			i +=1
		flight_plans[PermutationId].append({'leg': i, 
							'Orig': perm[i-1][0],
							'Date':end_date,
							'Dest':home_city})
		
		PermutationId +=1
	print flight_plans	 
	return flight_plans
		
def date_to_string(date_object,include_day=False):
	year = str(date_object.year)
	month = str(date_object.month)
	day = str(date_object.day)

	if len(month) == 1:
		month = "0" + month
	if len(day) == 1:
		day = "0" + day
	if include_day:
		date_string =   year + "-" + month + "-" + day
	else:
		date_string =  year + "-" + month
	return date_string


def get_flights_from_to_home(start_date):
	pass 


def get_price_for_each_plan(flight_data,flight_plans,start_date):
	flight_plans_update = {'Routes':[]}
	data = flight_data
	for k in flight_plans:
		plan = flight_plans[k]
		price_for_plan = 0
		routeName = "Route" + str(k)
		current_plan = {'Route':[]}
		success = True
		leg_num = 1
		for leg in plan:
			orig = leg['Orig']
			date = date_to_string(leg['Date'],True)
			dest = leg['Dest']
			leg['Date'] = date
			try:
				price_for_leg = data[orig][dest][date]["Price"]
				carrier_for_leg = data[orig][dest][date]['Airlines']
				price_for_plan += price_for_leg
				legName = 'Leg' + str(leg_num)
				#Numbered route names are available with routeName var
				current_plan['Route'].append({'Leg':leg,'LegPrice':price_for_leg,'Carrier':carrier_for_leg})
				
			except KeyError:
				print "Error in leg"
				current_plan[routeName].append({'EEEERRRORRRRRRRR':'RRERE'})
				success = False
			leg_num += 1
			current_plan['Cost'] = price_for_plan
		'''

		for each plan add the cost of 
		'''
		if success:	
			flight_plans_update['Routes'].append(current_plan)

	return flight_plans_update


def merge_flight_data(list_of_data):
	data = list_of_data[0]
	rest_of = list_of_data[1:]
	for trip in rest_of:
		for orig in trip:
				for dest in trip[orig]:
					for x in trip[orig][dest]:
						data[orig][dest][x] = trip[orig][dest]
	return data
		

def get_required_flight_data(start_date,end_date,city_codes):
	months_to_fetch = [date_to_string(start_date)]
	if start_date.month != end_date.month:
		how_many = end_date.month - start_date.month
		months = range(start_date.month+1,start_date.month+how_many+1)
		for x in months:
			months_to_fetch.append(date_to_string(datetime.date(start_date.year,x,start_date.day)))

	list_of_data = [sslib.fetch_for_month(city_codes,m) for m in months_to_fetch]
	merged_data = merge_flight_data(list_of_data)
	return merged_data

x = [("edi",4),("lon",3),("jfk",3)]
y = datetime.datetime(year=2015,month=3,day=2)
def test(city_codes_with_days,start_date,home_city):
	'''
	city_codes_with_days format
	[("edi",4),("lon",3),("jfk",3)]

	start_date format
	datetime.datetime(year=2015,month=3,day=2)

	start_date
	'''
	start = start_date
	end = datetime.datetime(year=2015,month=3,day=12)
	city_codes = [y[0] for y in city_codes_with_days]
	city_codes.append(home_city)
	flight_data = get_required_flight_data(start,end,city_codes)
	flight_plans = possible_configs(city_codes_with_days,start,home_city)
	x = get_price_for_each_plan(flight_data,flight_plans,start)
	return x



