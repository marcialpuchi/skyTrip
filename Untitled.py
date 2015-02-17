from flask import Flask, jsonify,request
app = Flask(__name__)
import sslib
import json
import prob
import datetime


@app.route("/")
def hello():
	#x = sslib.autosuggest_place("edinburgh")
	x = sslib.fetch_prices('jfk','lhr','2015-03-01','2015-03-04')

	return json.dumps(x)

'''
Sample JSON

{'Cities':[
			{'CityId': 'lon'},
			{'CityId': 'lca'},
			{'CityId': 'jfk'}
			]	
	'Start_date':'2015-03-02' 
	}
'''
@app.route("/get_results/", methods=["POST"])
def asdad():
	

	sample_json = {'Cities':[
			{'CityId': 'lon', 'Days': 3},
			{'CityId': 'lca','Days': 4},
			{'CityId': 'jfk','Days': 3}
			],	
	'Start_date':'2015-03-02' 
	}


	sample_json =(request.get_json())
	


	print sample_json
	city_list = []
	for city in sample_json['Cities']:
		city_list.append((city['CityId'],city['Days']))

	year = int(sample_json['Start_date'][:4])
	month = int(sample_json['Start_date'][5:7])
	day = int(sample_json['Start_date'][-2:])
	print year,month,day
	start_date = datetime.date(year,month,day)
	return str(prob.test(city_list,start_date))



if __name__ == "__main__":
	app.debug = True
	app.run()

