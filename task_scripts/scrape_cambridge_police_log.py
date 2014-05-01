# coding: utf-8
#!/usr/bin/python
import requests
import re
import sqlite3
import MySQLdb
from bs4 import BeautifulSoup

mysql_host = 'localhost'
mysql_user = 'root'
mysql_pass = ''
mysql_db = 'ipvtech'


def has_same_record(source="cambridge", incident_no='', report_time='', report_date=''):
	conn = MySQLdb.connect(host=mysql_host, # your host, usually localhost 
	                     user=mysql_user, # your username
	                      passwd=mysql_pass, # your password
	                      db=mysql_db) 
	curr = conn.cursor()
	curr.execute("SELECT COUNT(*) FROM policelog WHERE incident_no='%s' AND report_date='%s' AND report_time='%s' AND source='%s'" % (incident_no, report_date, report_time, source))
	result=curr.fetchone()
	conn.close()
	if result[0] > 0:
		return True
	else:
		return False

def save(report_date='', report_time='', occur_date='', occur_time='', location='', comments='', type='', incident_no='', source='cambridge'):
	conn = MySQLdb.connect(host=mysql_host, # your host, usually localhost
		                     user=mysql_user, # your username
		                      passwd=mysql_pass, # your password
		                      db=mysql_db) 
	curr = conn.cursor()
	try:
		curr.execute("INSERT INTO policelog (report_date, report_time, occur_date, occur_time, location, comments, type, source, incident_no) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (report_date, report_time, occur_date, occur_time, conn.escape_string(location), conn.escape_string(comments), conn.escape_string(type), source, incident_no))
	except sqlite3.ProgrammingError:
		print "losing data! %s, %s, %s" % (report_date,report_time,incident_no)
	conn.commit()
	conn.close()

def scrape_cambridge():
	cursor_url = "http://www.cambridgema.gov/cpd/newsandalerts/Archives.aspx"
	domain_name = "http://www.cambridgema.gov"
	soup = BeautifulSoup(requests.get(cursor_url).content)
	for list_link in soup.select('#nav-secondary a'):
		list_url = domain_name + list_link.get('href')
		while True:
			print "processing list ... %s" % list_url
			soup2 = BeautifulSoup(requests.get(list_url).content)
			for a_link in soup2.select('.news a'):
				if re.search('Daily Log', a_link.string, re.I):
					page_url = domain_name + a_link.get('href')
					print "scraping page ... %s" % page_url
					success = scrape_cambridge_single_page(page_url)
					if not success:
						return False
			# find the next link
			next_link = soup2.find('a', text="Next")
			if next_link:
				list_url = domain_name+next_link.get('href')
			else:
				break
		

def scrape_cambridge_single_page(url):
	html = requests.get(url)
	all_lines = re.findall('<tr>(.*?)</tr>', html.content, re.M | re.S)
	if len(all_lines)>2:
		for ln in range(2, len(all_lines)):
			line = all_lines[ln]
			line_content = []
			for elem in re.split('<.*?>', line, 0, re.M | re.S):
				elem = elem.replace('&nbsp;', '')
				real_elem = re.findall('[^\r^\n^\s]+', elem, re.M | re.S)
				if len(real_elem)>0:
					line_content.append(' '.join(real_elem))
			print line_content
			if len(line_content) > 6:
				if re.search('[0-9]+', line_content[0]):
					save(report_date=line_content[0], report_time=line_content[1], incident_no=line_content[3], type=line_content[4], location=line_content[5], comments=line_content[6])
				else:
					save(report_date=line_content[2], report_time=line_content[3], incident_no=line_content[1], type=line_content[4], location=line_content[5], comments=line_content[6])
			elif len(line_content) > 5:
				if re.search('[0-9]+', line_content[0]):
					save(report_date=line_content[0], report_time=line_content[1], incident_no=line_content[3], location=line_content[4], comments=line_content[5])
				else:
					rdatetime = line_content[2].split(' ')
					if len(rdatetime)>1:
						save(report_date=rdatetime[0], report_time=rdatetime[1], type=line_content[3], incident_no=line_content[1], location=line_content[4], comments=line_content[5])
					else:
						save(report_date=line_content[2], report_time=line_content[3], incident_no=line_content[1], location=line_content[4], comments=line_content[5])
			elif len(line_content) > 4:
				rdatetime = line_content[2].split(' ')
				if len(rdatetime)>1:
					save(report_date=rdatetime[0], report_time=rdatetime[1], incident_no=line_content[1], location=line_content[3], comments=line_content[4])
	return True
		
	
#scrape_cambridge_single_page("http://www.cambridgema.gov/cpd/newsandalerts/Archives/detail.aspx?path=%2fsitecore%2fcontent%2fhome%2fcpd%2fnewsandalerts%2fArchives%2f2014%2f03%2f03272014")
scrape_cambridge()