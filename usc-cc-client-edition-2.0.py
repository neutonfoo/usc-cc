#/usr/bin/env python3

from config import *

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from time import sleep, time
import datetime

import signal
import re
import getpass
import webbrowser
from pathlib import Path

username = ''
password = ''
driver = None
unschedule = False

def main():
	global username
	global password
	global classes
	global driver

	# Print app name
	print()
	print('''██╗   ██╗███████╗ ██████╗     ██████╗ ██████╗    ██╗   ██╗██████╗     ██████╗
██║   ██║██╔════╝██╔════╝    ██╔════╝██╔════╝    ██║   ██║╚════██╗   ██╔═████╗
██║   ██║███████╗██║         ██║     ██║         ██║   ██║ █████╔╝   ██║██╔██║
██║   ██║╚════██║██║         ██║     ██║         ╚██╗ ██╔╝██╔═══╝    ████╔╝██║
╚██████╔╝███████║╚██████╗    ╚██████╗╚██████╗     ╚████╔╝ ███████╗██╗╚██████╔╝
 ╚═════╝ ╚══════╝ ╚═════╝     ╚═════╝ ╚═════╝      ╚═══╝  ╚══════╝╚═╝ ╚═════╝''')
	print('USC Class Checker V2.0 (Client Edition)')
	print('Developed by Neuton Foo | https://github.com/neutonfoo/usc-cc')
	print()

	# Initialize Driver
	driverType = ''
	hasChromeDriver = False
	hasGeckoDriver = False

	chromeDriverFile = Path('./chromedriver')
	if chromeDriverFile.is_file():
		hasChromeDriver = True
		print('chromedriver placed in project directory')

	geckoDriverFile = Path('./geckodriver')
	if geckoDriverFile.is_file():
		hasGeckoDriver = True
		print('geckodriver placed in project directory')

	print()

	if hasChromeDriver:
		# Chrome
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--headless')
		driver = webdriver.Chrome(executable_path = './chromedriver', options = chrome_options)
		driverType = 'chromedriver'
	elif hasGeckoDriver:
		# Firefox
		firefox_options = webdriver.FirefoxOptions()
		firefox_options.add_argument('--headless')
		driver = webdriver.Firefox(executable_path = './geckodriver', options = firefox_options)
		driverType = 'geckodriver'
	else:
		# Default to Chrome, but don't specify executable_path
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--headless')
		driver = webdriver.Chrome(options = chrome_options)
		driverType = 'chromedriver'

	driver.set_page_load_timeout(timeout)
	print('Selenium initialized - \033[4m' + driverType + '\033[0m' + ' loaded')
	# Regex to match class - department + class code
	regex = re.compile('([A-Z]+)(\d+)')
	# Prepare classes
	for c in classes:
		c['initialized'] = False
		c['completed'] = False
		c['pages'] = [1 for section in range(len(c['sections']))]
		c['deptCode'] = regex.split(c['class'])[1]
		c['classCode'] = regex.split(c['class'])[2]

		c['urls'] = ['' for section in range(len(c['sections']))]

		c['sectionInitialized'] = [False for section in range(len(c['sections']))]
		c['sectionFullNames'] = ['' for section in range(len(c['sections']))]
		c['types'] = ['' for section in range(len(c['sections']))]
		c['units'] = ['' for section in range(len(c['sections']))]
		c['days'] = ['' for section in range(len(c['sections']))]
		c['times'] = ['' for section in range(len(c['sections']))]
		c['instructors'] = ['' for section in range(len(c['sections']))]
		c['locations'] = ['' for section in range(len(c['sections']))]
		c['availabilities'] = ['' for section in range(len(c['sections']))]
		c['availabilities'] = ['' for section in range(len(c['sections']))]

		c.pop('class', None)
	print('Prepared classes')
	print()

	# Get user authentication details
	getUSCID()

def getUSCID():
	global username
	global password

	print('\033[1m'  + 'Login with your USC ID' + '\033[0m')
	username = input('USC NetID: ')
	password = getpass.getpass('Password: ')
	print()
	attemptTry()

def login():
	global username
	global password
	global driver

	# Redirect to USC Shibboleth Login page
	print('Opening connection to USC Shibboleth')
	driver.get('https://my.usc.edu')
	sleep(3)

	# If session restored to myUSC, just return
	if driver.current_url == 'https://my.usc.edu/':
		print('Previous session restored')
		return

	# Login to USC Shibboleth
	print('Logging into USC Shibboleth as \033[4m' + username + '\033[0m')
	driver.find_element_by_name('j_username').send_keys(username)
	driver.find_element_by_name('j_password').send_keys(password)
	driver.find_element_by_name('_eventId_proceed').click()
	sleep(3)

	# Confirm URL
	if driver.current_url == 'https://my.usc.edu/':
		print('Login successful')
	else:
		print()
		print('Login failed')
		print('Please verify your login information')
		print()
		getUSCID()

def attemptTry():
	global unschedule
	global autocheckout

	try:
		login()
		redirectToTerm()

		if unschedule:
			unscheduleNonRegisteredCourses()
		elif autocheckout:
			print('\033[1m' + 'Autocheckout detected' + '\033[0m')
			print('For autocheckout to work, all your non-registered courses will need to be unscheduled from myCourseBin')
			print()
			print('\033[1m'  + ' * You will ' + '\033[4m' + 'not' + '\033[0m' + '\033[1m' + ' be unscheduled/dropped from courses you are currently registered in *' + '\033[0m')
			print()
			unscheduleOption = input('Unschedule all non-registered courses from myCourseBin? (Y/N): ')
			print()

			if unscheduleOption == 'Y':
				unschedule = True
				unscheduleNonRegisteredCourses()
			else:
				autocheckout = False
				print('Autocheckout disabled for this session')
				print('To disable autocheckout in future sessions, please edit the config file')
				print()
		checkWebReg()

	except TimeoutException as e:
		print()
		print('Exception thrown - TimeoutException')
		print('Disconnect detected')
		print('Attempting login again')
		print()
		attemptTry()
	except NoSuchElementException as e:
		print()
		print('Exception thrown - NoSuchElementException')
		print('Disconnect detected')
		print('Attempting login again')
		print()
		attemptTry()

def unscheduleNonRegisteredCourses():
	global driver
	print('Unsheduling all non-registered courses from myCourseBin')
	print('Redirecting to myCourseBin')
	driver.get('https://webreg.usc.edu/myCourseBin')
	sleep(2)

	print('Expanding all courses')
	expandAllButton = driver.find_element_by_id('expandAll')
	expandAllButton.click()
	sleep(1)

	unscheduleButtons = driver.find_elements_by_xpath('//a[text()="Unschedule"][following-sibling::a[text()="Register"]][ancestor-or-self::div[contains(@class, "schUnschRmv") and not(contains(@style, "display: none;"))]]')

	print('Unscheduling ' + str(len(unscheduleButtons)) + ' courses')
	# Unschedules all Unregistered courses
	for unscheduleButton in unscheduleButtons:
		unscheduleButton.click()
	print('Non-registered courses unscheduled')
	print()

def redirectToTerm():
	global driver
	global term
	# Redirect to USC Web Registration
	print('Redirecting to USC Web Registration')
	driver.get('https://my.usc.edu/portal/oasis/webregbridge.php')

	# Redirecting to Term
	print('Redirecting to Term ' + str(term))
	driver.get('https://webreg.usc.edu/Terms/termSelect?term=' + str(term))
	print()

def checkWebReg():
	global driver
	global classes
	global availabilityAlertLink

	while True:
		st = datetime.datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')
		print(st)

		for c in classes:
			if not c['completed']:
				for sectionIndex, section in enumerate(c['sections']):
					inPage = False

					while not inPage:
						if not c['sectionInitialized'][sectionIndex]:
							c['urls'][sectionIndex] = 'https://webreg.usc.edu/Courses?DeptId=' + c['deptCode'] + '&page=' + str(c['pages'][sectionIndex])

						driver.get(c['urls'][sectionIndex])
						sleep(3)
						html = driver.page_source

						# Checks if the section number is on the page
						if c['sectionInitialized'][sectionIndex] or ('<b>' + section in html):
							inPage = True

							if not c['sectionInitialized'][sectionIndex]:
								# Matches the section and the letter after
								c['sectionFullNames'][sectionIndex] = section + find_between(html, '<b>' + section, '</b>')

								if not c['initialized']:
									# Parses full class name
									classSectionsDiv = driver.find_element_by_xpath('//b[text() = "' + c['sectionFullNames'][sectionIndex] + '"]/../../../..')
									classIndex = classSectionsDiv.get_attribute('id')
									classDiv = driver.find_element_by_css_selector('a.course-title-indent[href="#' + classIndex + '"]')
									c['classFullName'] = classDiv.get_attribute('innerText').strip()

									# Initialize
									c['initialized'] = True

							# Matches the <div> of the session
							sectionDiv = driver.find_element_by_xpath('//b[text() = "' + c['sectionFullNames'][sectionIndex] + '"]/../..')
							sectionDivHtml = sectionDiv.get_attribute('innerText')

							# Get the HTML of the sectionDiv
							if not c['sectionInitialized'][sectionIndex]:
								# Parses section type
								c['types'][sectionIndex] = find_between(sectionDivHtml, 'Type: ', '\n').strip()
								# Parses section units
								c['units'][sectionIndex] = find_between(sectionDivHtml, 'Units: ', '\n').strip()
								# Parses section days
								c['days'][sectionIndex] = find_between(sectionDivHtml, 'Days: ', '\n').strip()
								# Parses section time
								c['times'][sectionIndex] = find_between(sectionDivHtml, 'Time: ', '\n').strip()
								# Parses section instructor
								c['instructors'][sectionIndex] = find_between(sectionDivHtml, 'Instructor: ', '\n').strip()
								# Parses section location
								c['locations'][sectionIndex] = find_between(sectionDivHtml, 'Location: ', '\n').strip()
								# Set sectionInitialized
								c['sectionInitialized'][sectionIndex] = True
							# Parses class availbility
							c['availabilities'][sectionIndex] = find_between(sectionDivHtml, 'Registered: ', '\n').strip()
						else:
							c['pages'][sectionIndex] += 1
					processSection(c, sectionIndex)
				processClass(c)
		sleep(interval)
		print()

def find_between(s, first, last):
	try:
		start = s.index( first ) + len( first )
		end = s.index( last, start )
		return s[start:end]
	except ValueError:
		return ''

def processSection(c, sectionIndex):
		classMetaFormatted = c['classFullName'] + ' ' + c['sectionFullNames'][sectionIndex] + ' ' + c['types'][sectionIndex] + ' (' + c['instructors'][sectionIndex] + ') [' + c['days'][sectionIndex] + ' / ' + c['times'][sectionIndex] + '] - ' + c['availabilities'][sectionIndex]
		if c['availabilities'][sectionIndex] != 'Closed' and c['availabilities'][sectionIndex] != 'Canceled':
			print('\033[92m' + '\033[1m' + classMetaFormatted + '\033[0m' + '\033[0m')
		else:
			print(classMetaFormatted)

def processClass(c):
	canRegister = True

	for sectionIndex, section in enumerate(c['sections']):
		if c['availabilities'][sectionIndex] == 'Closed' or c['availabilities'][sectionIndex] == 'Canceled':
			canRegister = False

	if canRegister:
		c['completed'] = True
		webbrowser.open(availabilityAlertLink)
		if autocheckout and c['checkout']:
			checkout(c)

def checkout(c):
	global driver
	print('Redirecting to myCourseBin')
	driver.get('https://webreg.usc.edu/myCourseBin')
	for section in c['sections']:
		sectionRegisterButton = driver.find_element_by_xpath('//a[@href = "/myCoursebin/SchdUnschRmv?act=Sched&section=' + section + '"]')
		sectionRegisterButton.click()
	driver.get('https://webreg.usc.edu/Register')
	driver.find_element_by_id('SubmitButton').click()

def handleSIGINT(sig, frame):
	print()
	print('SIGNIT detected')
	handleQuit()

def handleQuit():
	global driver
	if driver != None:
		print('Closing Selenium driver')
		driver.quit()
	quit()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt as e:
		print()
		print()
		print('Ctrl + C detected')
		handleQuit()
