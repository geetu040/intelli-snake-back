from flask import Flask, render_template, request, send_from_directory
from map import Map
import json, os

rows = 31
cols = 28
map = Map(rows, cols, fixed_map_url="static/binary_map.json")

app = Flask(__name__, template_folder='static/web')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def index():
	params = {
		'rows': rows,
		'cols': cols,
	}
	return render_template("index.html", params=params)

@app.route("/remap", methods=["GET", "POST"])
def remap():
	info = json.loads(request.args.get("data"))
	returned_info = map.handle_info(info)
	return json.dumps(returned_info)

if __name__ == '__main__':
	app.run(debug=True)