# Patrick McCorkell
# November 2021
# US Naval Academy
# Robotics and Control TSD
#
# References:
# https://help.ifttt.com/hc/en-us/articles/115010230347-Webhooks-service-FAQ#article-container
# https://medium.com/mai-piu-senza/connect-a-python-script-to-ifttt-8ee0240bb3aa
# https://anthscomputercave.com/tutorials/ifttt/using_ifttt_web_request_email.html


from bs4 import BeautifulSoup
import requests
from time import sleep

from config import *		# includes "event_name" from IFTTT applet name, and product webpage from Digikey.
try:
	from secrets import *
	run_main = 1
except:
	print('ERROR: API key not found.')
	print('Create \"secrets.py\" file with API key set as string variable \"maker_key\".')
	run_main = 0


iftt_website = 'https://maker.ifttt.com/trigger/'+event_name+'/with/key/'+ maker_key

def connect_website(website):
	failed=1
	while(failed):
		html = requests.get(website)
		html_parser = BeautifulSoup(html.text,'html.parser')

		check_rejected = html_parser.head.title.getText('title')

		print('')
		if (check_rejected == 'Request Rejected'):
			print('check_rejected')
			print('The internet is not playing nice. Try again ?')
			sleep(10)
			# return 0
		else:
			failed=0
	return html_parser



def scrape_website(target_website):
	connection = connect_website(target_website)
	products = {}

	if (connection):

		# The table's id is derived from F12 inspection
		table = connection.find("table", {"id":"data-table-0"})

		# 'tr' is html code for rows in a table.
		rows = table.find_all('tr')

		# First 2 rows are header stuff, get rid of them.
		# Use visual inspection of website + F12 inspection to figure that out.
		rows.pop(0)
		rows.pop(0)

		for row in rows:
			# 'td' is html code for columns in a table.
			cells = row.find_all('td')

			# Using F12 Inspection, derive that 0th column is title, 1st column is product code, and 2nd column is quantity
			# Verify w/ visual inspection.
			product_code = cells[0].getText('title')
			product_name = cells[1].getText('data-atag')
			product_quantity = int(cells[2].getText('data-atag'))

			# Arrange the 3 pieces of data we're interested in as a dictionary
			products[product_code]={
				'quantity':product_quantity,
				'name':product_name
			}

		# Do things with the dictionary of product information.
		for product in products:
			print(products[product]['name'] + ': ' + str(products[product]['quantity']))
		return products


def send_ifttt(stock_data):
	report = {}
	for i,k in enumerate(stock_data):
		report["value"+str(i+1)] = stock_data[k]
		print(k)
	print(report)
	if report:
		requests.post(iftt_website,data=report)
		print("sent: " + str(report))
	else:
		print("No report to send.")


def check_stock(data):
	in_stock = 0
	stock = {}

	if (data):
		for k in data:
			if (data[k]['quantity']):
				stock[k] = data[k]
		print(stock)
		if stock:
			for k in stock:
				send_ifttt(stock[k])

def main():
	global digikey_website	# from config.py
	check_stock(scrape_website(digikey_website))

# Ensure API secrets.py exists, then run main().
if (run_main):
	main()
