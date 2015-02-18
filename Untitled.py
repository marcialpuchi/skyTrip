from flask import Flask, jsonify,request
app = Flask(__name__, static_url_path='')
import sslib
import json
import prob
import datetime


@app.route('/')
def index():
	return app.send_static_file("index.html")
	
@app.route("/get_results/", methods=["POST"])
def asdad():
	

	sample_json = {'Cities':[
			{'CityId': 'lon', 'Days': 3},
			{'CityId': 'lca','Days': 4},
			{'CityId': 'jfk','Days': 3}
			],
	'Home_city':'edi',	
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
	homecity = sample_json['Home_city']
	print year,month,day
	start_date = datetime.date(year,month,day)
	return str(prob.test(city_list,start_date,homecity))



if __name__ == "__main__":
	app.debug = True
	app.run()

