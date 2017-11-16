#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""USC Class Checker 1.0 - Public

This script checks for availability of USC Classes and opens a website if availability is detected.
"""

__author__ = "Neuton Foo"
__version__ = "1.0-public"
__email__ = "nfoo@usc.edu"
__status__ = "Production"

import sys
sys.dont_write_bytecode = True

from config import *
from time import sleep
from selenium import webdriver
import getpass
import webbrowser
import time
import datetime

def main():
    source = ""

    print("""
.  .  ,-.   ,-.    ,-. .                ,-. .           ,
|  | (   ` /      /    |               /    |           |
|  |  `-.  |      |    | ,-: ,-. ,-.   |    |-. ,-. ,-. | , ,-. ;-.
|  | .   ) \      \    | | | `-. `-.   \    | | |-' |   |<  |-' |
`--`  `-'   `-'    `-' ' `-` `-' `-'    `-' ' ' `-' `-' ' ` `-' '""");
    print("Version " + __version__)
    print("For documentation, please refer to the README")
    print("")

    for c in classes:
        c['completed'] = False
        c['page'] = 0
    # end for

    # Get username and password for Shibboleth login
    username = raw_input("Username: ")
    password = getpass.getpass("Password: ")

    coursesBaseUrl = "https://webreg.usc.edu/Courses?DeptId="
    # If geckodriver installed, can debug with
    # driver = webdriver.Firefox()
    driver = webdriver.PhantomJS()

    # Disclaimer
    print("")
    print("\033[1mPlease do NOT abuse this tool\033[0m")
    print("")

    # Redirect to USC Shibboleth Login page
    print("Opening connection to USC Shibboleth")
    driver.get("https://my.usc.edu")
    sleep(3)

    # Login to USC Shibboleth
    print("Logging into USC Shibboleth as \033[4m" + username + "\033[0m")
    driver.find_element_by_name('j_username').send_keys(username)
    driver.find_element_by_name('j_password').send_keys(password)
    driver.find_element_by_name('_eventId_proceed').click()
    sleep(3)

    # Redirect to USC Web Registration
    print("Redirecting to USC Web Registration")
    driver.get("https://my.usc.edu/portal/oasis/webregbridge.php")
    sleep(3)

    # Redirecting to Term
    print("Redirecting to Term " + str(term))
    driver.get("https://webreg.usc.edu/Terms/termSelect?term=" + str(term))
    sleep(3)

    # Confirming URL
    if driver.current_url == "https://webreg.usc.edu/Departments":
        print("Successful access to Web Registration")
    else:
        print("Something went wrong!")
        quit()
    # end if
    print("")

    # Start monitoring
    classesMonitoring = len(classes)
    completedClasses = 0

    while True:
        # Print out date and time
        st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        print st

        # Loop through classes
        for c in classes:
            if not c["completed"]:
                depCode = c["depCode"]
                classCode = c["classCode"]
                sectionNumber = c["sectionNumber"]
                page = c["page"]
                inPage = False

                while not inPage:
                    url = coursesBaseUrl + depCode + "&page=" + str(page)
                    driver.get(url)
                    sleep(3)
                    html = driver.page_source

                    if "<b>" + sectionNumber in html:
                        inPage = True

                        # Cache page so it's quicker
                        if c["page"] != page:
                            c["page"] = page
                        # end if

                        sectionHtml = sectionNumber + find_between(html, "<b>" + sectionNumber, "</b>")
                        sectionSpan = driver.find_element_by_xpath("//b[text() = '" + sectionHtml + "']/../..")
                        sectionSpanHtml = sectionSpan.get_attribute("innerText")

                        classAvailability = find_between(sectionSpanHtml, "Registered: ", "\n").strip()
                        classDays = find_between(sectionSpanHtml, "Days: ", "\n").strip()
                        classTime = find_between(sectionSpanHtml, "Time: ", "\n").strip()
                        classInstructor = find_between(sectionSpanHtml, "Instructor: ", "\n").strip()

                        classMetaFormatted = depCode + classCode + " " + sectionNumber + " (" + classInstructor + ") [" + classDays + " / " + classTime + "] - " + classAvailability

                        if classAvailability != "Closed":
                            webbrowser.open(youtubeAlertLink)
                            print '\033[92m' + '\033[1m' + classMetaFormatted + '\033[0m' + '\033[0m'

                            c['completed'] = True
                            completedClasses += 1
                        else:
                            print classMetaFormatted
                        # end if
                    else:
                        page += 1
                    # end if
                # end while
            # end if
        # end for
        print("")
        if classesMonitoring == completedClasses:
            break
        else:
            sleep(30)
        # end if
    # end while
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print("Completed check on "),
    print st
    print("")
# end def main

# Man's Not Hot
def find_between(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
    # end try
# end def find_between

if __name__ == "__main__":
    main()
# end if
