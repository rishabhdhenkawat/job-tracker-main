import flask
from flask import request, jsonify
from scraper import *
from bson.json_util import dumps
import json
import threading

app = flask.Flask(__name__)
app.config["DEBUG"] = True

jl = MongoDb(collection="jobs")
#jl.collection.drop_index("Location_text_Industry_text_Title_text_Company_text_Description_text")
#jl.collection.drop_index("Title_text_Company_text_Description_text")
#jl.collection.create_index([("Location", pymongo.TEXT), ("Industry", pymongo.TEXT), ("Title", pymongo.TEXT), ("Company", pymongo.TEXT), ("Description", pymongo.TEXT)])
jl.collection.create_index([('Posted_On', 1)])

@app.route('/start', methods=['GET'])
def home():
    auto_scraping2(jl)
    print("Done", flush=True)
    return "OK"



@app.route('/db/main', methods=['GET'])
def main_db():
    date = request.args.get('date')
    hours = request.args.get('hours')
    lsearch = request.args.get('lsearch')
    csearch = request.args.get('csearch')
    tsearch = request.args.get('tsearch')
    limit = request.args.get('limit')
    page = request.args.get('page')
    portal = request.args.get('portal')

    response = app.response_class(
        response=dumps(jl.fetch_main(date = date, hours = hours, lsearch = lsearch, csearch = csearch, tsearch = tsearch, limit = limit, page = page, portal = portal), indent=2),
        status=200,
        mimetype='application/json')
    return response



@app.route('/db/fetchall', methods=['GET'])
def fetchall():
    response = app.response_class(
        response=dumps(jl.fetch_some(all=True), indent=2),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/db/fetch/<int:num>', methods=['GET'])
def fetch(num):
    response = app.response_class(
        response=dumps(jl.fetch_some(num), indent=2),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/db/fetch/date/<string:date>', methods=['GET'])
def fetch_date(date):
    response = app.response_class(
        response=dumps(jl.fetch_by_date(date), indent=2),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/db/fetch/date/<string:date>/<int:limit>/<int:page>', methods=['GET'])
def fetch_date_with_lp(date, limit, page):
    result = str(dumps(jl.fetch_by_date(date), indent=2))
    py_object = json.loads(result)[(page-1)*limit:((page-1)*limit)+limit]
    response = app.response_class(
        response=dumps(py_object, indent=2),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/db/fetch/date/hours/<int:hours>', methods=['GET'])
def fetch_hours(hours):
    response = app.response_class(
        response=dumps(jl.fetch_by_hours(hours), indent=2),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/db/fetch/date/hours/<int:hours>/<int:limit>/<int:page>', methods=['GET'])
def fetch_hours_with_lp(hours, limit, page):
    result = str(dumps(jl.fetch_by_hours(hours), indent=2))
    py_object = json.loads(result)[(page-1)*limit:((page-1)*limit)+limit]
    response = app.response_class(
        response=dumps(py_object, indent=2),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/db/search/title/<string:search>', methods=['GET'])
def search_in_title(search):
    response = app.response_class(
        response=dumps(jl.search_string(search), indent=2),
        status=200,
        mimetype='application/json'
    )
    return response

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
