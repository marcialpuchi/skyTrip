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
	data = request.json
	date=data['date']
	city_list = []
	for city in data['destinations']:
		if (len(city['name'])>3):
			city_list.append((city['name'].split('(')[1].split(')')[0],int(city['days'])))
	year = int(date[:4])
	month = int(date[5:7])
	day = int(date[-2:])
	homecity = data['origin'].split('(')[1].split(')')[0]
	start_date = datetime.date(year,month,day)
	sorted_json = prob.go_fetch(city_list,start_date,homecity)
	sorted_json['Routes'] = sorted(sorted_json['Routes'],key=itemgetter('Cost'))
	return jsonify(sorted_json)
  
  
@app.route("/get_results_flex", methods=["GET","POST"])
def get_cached_flex():
  	data = request.json
	date=data['date']
	city_list = []
	for city in data['destinations']:
		if (len(city['name'])>3):
			city_list.append((city['name'].split('(')[1].split(')')[0],int(city['days'])))
	year = int(date[:4])
	month = int(date[5:7])
	day = int(date[-2:])
	homecity = data['origin'].split('(')[1].split(')')[0]
	start_date = datetime.date(year,month,day)
	sorted_json = prob.go_fetch_flex(city_list,start_date,homecity)
	sorted_json['Routes'] = sorted(sorted_json['Routes'],key=itemgetter('Cost'))
	return jsonify(sorted_json)

if __name__ == "__main__":
	app.debug = True
	app.run()

