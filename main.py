from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_pagination import Pagination 
from db import *
from flask_login import LoginManager, login_user
import consts
import md5

# system consts
records_per_page = 10
md5_salt = 'coersive control'

app = Flask(__name__)
app.secret_key = 'the manipulative man'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User.get(User.id==userid)


@app.route("/")
def index():
	return render_template('index.html') 

@app.route("/search", methods=["GET"])
def search():
    if 'page' in request.args:
        page = request.args['page']
    else:
        page = 1
    
    query_object = PoliceLog.select()
    if 'keyword' in request.args:
        keyword = request.args['keyword']
        sql_key = "%"+keyword+"%"
        query_object = query_object.where((PoliceLog.location ** sql_key) | (PoliceLog.content ** sql_key) | (PoliceLog.type ** sql_key))
    else:
        keyword = ''
    records_num = query_object.count()
    #get count broken by source
    source_count_map = {}
    source_count_result = query_object.select(fn.Count(PoliceLog.id).alias('cnt'), PoliceLog.source).group_by(PoliceLog.source)
    for line in source_count_result:
        source_count_map[line.source] = line.cnt
    print source_count_map
    result = query_object.paginate(int(page), records_per_page)
    pagination = Pagination(total=records_num, page=int(page), bs_version=3)
    return render_template('result.html', records=result, pagination=pagination, keyword=keyword, page=page, source_count_map=source_count_map ) 

@app.route("/search_data", methods=["GET"])
def search_data():
    # percentage = count_result / count_base
    aggregate_base = PoliceLog.select()
    count_base = PoliceLog.select(fn.Date_format(PoliceLog.report_time, '%Y-%m').alias('x'), fn.Count(fn.Date_format(PoliceLog.report_time, '%Y-%m')).alias('date_count')).where(~(PoliceLog.report_time >> None)).group_by(fn.Date_format(PoliceLog.report_time, '%Y-%m'))
    count_result = count_base
    if 'keyword' in request.args:
        keyword = request.args['keyword']
        sql_key = "%"+keyword+"%"
        count_result = count_result.where((PoliceLog.location ** sql_key) | (PoliceLog.content ** sql_key) | (PoliceLog.type ** sql_key))
    start_year = aggregate_base.aggregate(fn.Min(fn.Year(PoliceLog.report_time)))
    start_month = aggregate_base.aggregate(fn.Min(fn.Month(PoliceLog.report_time)))
    end_year = aggregate_base.aggregate(fn.Max(fn.Year(PoliceLog.report_time)))
    end_month = aggregate_base.aggregate(fn.Max(fn.Month(PoliceLog.report_time)))
    
    result_map = {}
    base_map = {}
    count_list = []
    percentage_list = []
    for item in count_result:
        result_map[str(item.x)] = item.date_count
    for item in count_base:
        base_map[str(item.x)] = item.date_count

    while start_year*100+start_month <= end_year*100+end_month:
        date_string = str(start_year)+'-'+str(start_month).zfill(2)
        if date_string in base_map and date_string in result_map:
            count = int(result_map[date_string])
            percentage = float(count) / float(base_map[date_string])
        else:
            count = 0
            percentage = 0.0
        count_list.append([date_string, count])
        percentage_list.append([date_string, percentage])
        start_month = start_month + 1
        if start_month > 12:
            start_year = start_year + 1
            start_month = 1

#    for item in count_base:
#        if str(item.x) in result_map:
#            count = int(result_map[str(item.x)])
#        else:
#            count = 0
#        percentage = float(count) / float(item.date_count)
#        count_list.append([str(item.x), count])
#        percentage_list.append([str(item.x), percentage])
    return jsonify(data = [{'key':'count', 'bar':True, 'values':count_list}, {'key':'percentage', 'bar':False, 'values':percentage_list}])

@app.route("/case/<case_id>")
def view_case(case_id):
    result = PoliceLog.get(PoliceLog.id==case_id)
    tags = Tag.select().join(PoliceLogTag).join(PoliceLog).where(PoliceLog.id==case_id)
    case_tags = []
    device_tags = []
    for tag in tags:
        if tag.type == 'case':
            case_tags.append(tag.name)
        elif tag.type == 'device':
            device_tags.append(tag.name)
    return render_template('case.html', case=result, suggested_types=consts.incident_types, suggested_devices=consts.incident_devices, case_tags=','.join(case_tags), device_tag=','.join(device_tags)) 

@app.route("/report")
def new_incident():
	return render_template('report.html', suggested_types=consts.incident_types, suggested_devices=consts.incident_devices) 

@app.route("/insert", methods=["POST"])
def insert_incident():
    log = PoliceLog()
    log.type = request.form['type']
    log.location = request.form['location']
    log.content = request.form['content']
    log.source = "reported"
    log.save()
    print request.form
    return "something"

@app.route("/login_form")
def login_form():
    return render_template('login.html')

@app.route("/login", methods=["POST"])
def login():
    return "hello"

@app.route("/register", methods=["POST"])
def register():
    user_count = User.select().where(User.username==request.form['username']).count()
    if user_count > 0:
        flash("the username is already exist", "danger")
        return redirect(url_for("login_form"))
    user = User()
    user.name = request.form['name']
    user.username = request.form['username']
    user.password = md5.new(md5_salt+request.form['password']).hexdigest()
    user.email = ''
    user.is_masteruser = False
    user.save()
    login_user(user)
    return redirect(url_for("index"))

if __name__ == "__main__":
    
    app.run(debug=True)