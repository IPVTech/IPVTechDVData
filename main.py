from flask import Flask, render_template, request
from flask_pagination import Pagination 
from db import *
from consts import *

# system consts
records_per_page = 10

app = Flask(__name__)

@app.route("/")
def index():
	return render_template('index.html') 

@app.route("/search", methods=["GET"])
def search():
    page = request.args['page']
    keyword = request.args['keyword']
    if not page:
        page = 1
    sql_key = "%"+keyword+"%"
    query_object = PoliceLog.select().where((PoliceLog.location ** sql_key) | (PoliceLog.comments ** sql_key) | (PoliceLog.type ** sql_key))
    records_num = query_object.count()
    result = query_object.paginate(1, records_per_page)
    pagination = Pagination(total=records_num, page=int(page), bs_version=3)
    return render_template('result.html', records=result, pagination=pagination ) 

@app.route("/case/<case_id>")
def view_case(case_id):
    result = PoliceLog.get(PoliceLog.id==case_id)
    return render_template('case.html', case=result, incident_types=incident_types) 
    

@app.route("/report")
def new_incident():
	return render_template('report.html') 

@app.route("/insert")
def insert_incident():
	police_log = PoliceLog()
	police_log.location = request.form['location']
	police_log.comments = request.form['comments']
	police_log.source = "reported"


if __name__ == "__main__":
    app.run(debug=True)