from flask import Flask, jsonify,request
import re
app = Flask(__name__, static_url_path='')
import sslib
import json
import prob
import datetime


@app.route('/')
def index():
	return app.send_static_file("index.html")

@app.route("/get_result", methods=["POST"])
def asdad():
	print request.form[0]
	return 'sdfsdd'

@app.route("/get_results", methods=["GET","POST"])
def asdab():
	d1 = request.form['D1'].split('(')[1][:-1]
	d2 = request.form['D2'].split('(')[1][:-1]
	d3 = request.form['D3'].split('(')[1][:-1]
	daysD1=int(request.form['days_D1'])
	daysD2=int(request.form['days_D2'])
	daysD3=int(request.form['days_D3'])
	date=request.form['date']
	origin=request.form['origin'].split('(')[1][:-1]
	sample_json = {'Cities':[
			{'CityId': d1, 'Days':daysD1},
			{'CityId': d2,'Days':daysD2},
			{'CityId': d3,'Days':daysD2}
			],
	'Home_city':origin,	
	'Start_date':'2015-03-010' 
	}
	#sample_json =(request.get_json())
	
	city_list = []
	for city in sample_json['Cities']:
		city_list.append((city['CityId'],city['Days']))

	year = int(sample_json['Start_date'][:4])
	month = int(sample_json['Start_date'][5:7])
	day = int(sample_json['Start_date'][-2:])
	homecity = sample_json['Home_city']
	#print year,month,day
	start_date = datetime.date(year,month,day)
	return str(prob.test(city_list,start_date,homecity))
	


if __name__ == "__main__":
	app.debug = True
	app.run()

