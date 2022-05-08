from flask import Flask, render_template, request, send_from_directory
import json, os
import utility

app = Flask(__name__, template_folder='static/web')

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def index():
	with open("static/params.json", "r") as f:
		params = json.loads(f.read())
	return render_template("index.html", params=params)

@app.route("/map")
def map():
	info = json.loads(request.args.get("data"))
	returned_info = utility.load_map(info)
	return json.dumps(returned_info)

@app.route("/automate")
def automate():
	info = json.loads(request.args.get("data"))
	predicted_dirs = utility.automate(info)
	return predicted_dirs

@app.route("/automate_faster")
def automate_faster():
	info = json.loads(request.args.get("data"))
	returned_infos = utility.automate_faster(info)
	return json.dumps(returned_infos)

@app.route("/write")
def write():
	content = request.args.get("content")
	with open("latest_dataset.txt", "a") as f:
		f.write(content)
	return "nothing"

if __name__ == '__main__':
	app.run(debug=True)