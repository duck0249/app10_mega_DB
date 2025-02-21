import requests
from selectorlib import Extractor
import smtplib, ssl
import os
import time
import sqlite3


URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

connection = sqlite3.connect("data.db")


def scrape(url):
	"""Scrape the page source from the URL"""
	response = requests.get(url, headers=HEADERS)
	source = response.text
	return source


def extract(source):
	extractor = Extractor.from_yaml_file("extract.yaml")
	value = extractor.extract(source)["tours"]
	return value


def send_email(message):
	host = "smtp.gmail.com"
	port = 465

	username = "duck0249@gmail.com"
	password = "lqjavdgzrjdqkuft"

	receiver = "duck0249@gmail.com"
	context = ssl.create_default_context()

	with smtplib.SMTP_SSL(host, port, context=context) as server:
		server.login(username, password)
		server.sendmail(username, receiver, message)
	print("Email was sent!")


def store(extracted):
	row = extracted.split(",")
	row = [item.strip() for item in row]
	cursor = connection.cursor()
	cursor.execute("INSERT INTO events VALUES(?, ?, ?)", row)
	connection.commit()


def read(extracted):
	row = extracted.split(",")
	row = [item.strip() for item in row]
	group, city, event_date = row
	cursor = connection.cursor()
	cursor.execute('SELECT * FROM events WHERE "group"=? AND city=? AND "date"=?', (group, city, event_date))
	rows = cursor.fetchall()
	print(rows)
	return rows


if __name__=="__main__":
	scraped = scrape(URL)
	extracted = extract(scraped)
	print(extracted)
	
	if extracted != "No upcoming tours":
		row = read(extracted)
		if not row:
			store(extracted)
			send_email(message="Hey new event was sent.")
