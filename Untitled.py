from flask import Flask
app = Flask(__name__)
import sslib
import json

@app.route("/")
def hello():
	#x = sslib.autosuggest_place("edinburgh")
	x = sslib.fetch_prices('jfk','lhr','2015-03-01','2015-03-04')

	return json.dumps(x)

@app.route("/ra/")
def asdad():
	return "asdaafs"

if __name__ == "__main__":
	app.debug = True
	app.run()

