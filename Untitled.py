from flask import Flask, jsonify,request
import re
app = Flask(__name__, static_url_path='')
import sslib
import json
import prob
import datetime
from operator import itemgetter
sample_route={
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
    }

@app.route('/')
def index():
	return app.send_static_file("index.html")

@app.route("/get_route_live", methods=["GET","POST"])
def asdad():
	results = sslib.get_live_prices_for_route(sample_route)
	return str(results)

@app.route("/get_results", methods=["GET","POST"])
def get_cached():
	print "JSON"
	print request.get_json()
	data = request.json
	date=data['date']
	origin=data['origin'].split('(')[1].split(')')[0]

	sample_json = {'Cities':[],
	'Home_city':origin,	
	'Start_date':date
	}
	for d in data['destinations']:
		dest = d['name'].split('(')[1].split(')')[0]
		days_for_dest = int(d['days'])
		sample_json['Cities'].append({'CityId': dest, 'Days': days_for_dest})
	'''
	for k,v in data.iteritems():
		if len(k)>6:
			if k[-6:] == "[name]":
				dest = v.split('(')[1].split(')')[0]
				days_key = k[:-6] + "[days]"
				days_for_dest = int(data[days_key])
				sample_json['Cities'].append({'CityId': dest, 'Days': days_for_dest})
	'''
	
	city_list = []
	for city in sample_json['Cities']:
		city_list.append((city['CityId'],city['Days']))
	print sample_json
	year = int(sample_json['Start_date'][:4])
	month = int(sample_json['Start_date'][5:7])
	day = int(sample_json['Start_date'][-2:])
	homecity = sample_json['Home_city']
	start_date = datetime.date(year,month,day)
	sorted_json = prob.go_fetch(city_list,start_date,homecity)
	sorted_json['Routes'] = sorted(sorted_json['Routes'],key=itemgetter('Cost'))
	return jsonify(sorted_json)
  
  
@app.route("/get_results_flex", methods=["GET","POST"])
def get_cached_flex():
  
	date=request.form['date']
	origin=request.form['origin'].split('(')[1].split(')')[0]
	sample_json = {'Cities':[],
	'Home_city':origin,	
	'Start_date':date
	}

	for k,v in request.form.iteritems():
		if k[0] == "D":
			days_for_dest = int(request.form['days_D'+ str(k[1])])
			sample_json['Cities'].append({'CityId':v.split('(')[1].split(')')[0], 'Days': days_for_dest})

	city_list = []
	for city in sample_json['Cities']:
		city_list.append((city['CityId'],city['Days']))

	year = int(sample_json['Start_date'][:4])
	month = int(sample_json['Start_date'][5:7])
	day = int(sample_json['Start_date'][-2:])
	homecity = sample_json['Home_city']
	start_date = datetime.date(year,month,day)
	sorted_json = prob.go_fetch_flex(city_list,start_date,homecity)
	sorted_json['Routes'] = sorted(sorted_json['Routes'],key=itemgetter('Cost'))
	return jsonify(sorted_json)

if __name__ == "__main__":
	app.debug = True
	app.run()

