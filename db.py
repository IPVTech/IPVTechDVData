from peewee import *

# remind me to change my password after this project is finished ^_^
mysql_db = MySQLDatabase('ipvtech', user='root',passwd='', host="localhost")

class MySQLModel(Model):
	"""base model to mysql database"""
	class Meta:
		database = mysql_db

class PoliceLog(MySQLModel):
	id = IntegerField()
	report_date = DateTimeField()
	report_time = DateTimeField()
	location = CharField()
	comments = CharField()
	type = CharField()
	source = CharField()
	incident_no = CharField()

	
		
mysql_db.connect()
# print PoliceLog.select().count()
