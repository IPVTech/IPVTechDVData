from peewee import *
import json, re

mysql_db = MySQLDatabase('ipvtech', user='root',passwd='', host="localhost")

class MySQLModel(Model):
	"""base model to mysql database"""
	class Meta:
		database = mysql_db

#court_db = SqliteDatabase('court_decisions.db')
#
#class SQLiteModel(Model):
#	"""base model to mysql database"""
#	class Meta:
#		database = court_db
        
class Decision(MySQLModel):
    year = CharField(default='')
    month = CharField(default='')
    content = CharField()
    place = CharField(default='')
    title = CharField()
    source = CharField()

file_content = open('result_detail.json', 'r').read()

mysql_db.connect()
Decision.create_table(True)

#records = json.loads('['+file_content+'{}]')
#valid_count = 0
#for record in records:
#    if 'c' in record and record['c'] != None:
#        match =  re.search('\(([0-9]{4})\)',record['t'])
#        decision = Decision()
#        decision.content = record['c']
#        decision.title = record['t']
#        if match:
#            decision.year = match.group(1)
#        decision.save()
#        valid_count = valid_count+1
#
#print valid_count

records = Decision.select()
month_names_pattern = "(January|February|March|April|May|June|July|August|September|October|November|December)"
month_names_dict = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
for record in records:
    match = re.search(month_names_pattern, record.content, re.M)
    if match:
        record.month = month_names_dict[match.group(0)]
        record.save()
        