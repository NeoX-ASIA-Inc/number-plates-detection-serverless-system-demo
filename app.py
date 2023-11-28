from flask import Flask, jsonify, make_response, render_template

app = Flask(__name__)


@app.route("/")
def root():
    return render_template('index.html')


@app.route("/hello")
def hello():
    return jsonify(message='Hello from path!')


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
