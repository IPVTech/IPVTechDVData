from peewee import *

# remind me to change my password after this project is finished ^_^
mysql_db = MySQLDatabase('ipvtech', user='root',passwd='', host="localhost")

class MySQLModel(Model):
	"""base model to mysql database"""
	class Meta:
		database = mysql_db

class PoliceLog(MySQLModel):
	id = IntegerField()
	report_time = DateTimeField()
	location = CharField()
	content = CharField()
	type = CharField()
	source = CharField()
	incident_no = CharField()

class Tag(MySQLModel):
    name = CharField()
    type = CharField()
    
class PoliceLogTag(MySQLModel):
    policeLog = ForeignKeyField(PoliceLog)
    tag = ForeignKeyField(Tag)
    
class User(MySQLModel):
    name = CharField()
    username = CharField()
    password = CharField()
    email = CharField(default='')
    is_masteruser = IntegerField(default=0)
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    
		
mysql_db.connect()
# print PoliceLog.select().count()
