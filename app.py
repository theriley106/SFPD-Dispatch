from flask import Flask, request, render_template, request, url_for, redirect, Markup, Response, send_file, send_from_directory, make_response, jsonify
import interactions

app = Flask(__name__, static_url_path="", static_folder="static")


@app.route('/', methods=['GET'])
def index():
	return "<h1>This Works</h1>"

if __name__ == "__main__":
	app.run()
