from flask import Flask, jsonify,request
import re
app = Flask(__name__, static_url_path='')
import sslib
import json
import prob
import datetime
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
def asdab():
  
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



  

  print 'Hello there!'
  

  city_list = []
  for city in sample_json['Cities']:
   city_list.append((city['CityId'],city['Days']))

  year = int(sample_json['Start_date'][:4])
  month = int(sample_json['Start_date'][5:7])
  day = int(sample_json['Start_date'][-2:])
  homecity = sample_json['Home_city']
  #print year,month,day
  start_date = datetime.date(year,month,day)
  
  print city_list
  return jsonify(prob.test(city_list,start_date,homecity))
  
  


if __name__ == "__main__":
	app.debug = True
	app.run()

