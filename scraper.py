# web driver ===> scraper functionalities
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# import extract util functions
from extract_utils import find_element
from extract_utils import extract_from_table
from extract_utils import extract_from_detail_page

# import extract util functions
from object_utils import create_employer_object
from object_utils import create_notice_object

# file/data ===> data wrangling
import os
import re
import json
from requests import get,post,put
import time
from datetime import datetime
from uuid import uuid4

# email notifications
import smtplib
from email_utils import send_notification

# loads environment variable values
from dotenv import load_dotenv
APP_ROOT = os.path.join(os.path.dirname('__file__'), '.') # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)
pw = os.getenv('GMAIL_PASSWORD')
s = smtplib.SMTP('smtp.gmail.com', 587)

# URL
url = 'https://www.vermontjoblink.com/ada/mn_warn_dsp.cfm?def=false'

# settings for Chrome
chrome_options = Options()
# comment --headless option out if you want to see the browser window action happening
chrome_options.add_argument('--headless')
# sets window to large size
chrome_options.add_argument('--window-size=1325x744')
# points to the browser binary. Here I'm using Google Canary because I just wanted a browser dedicated to this.
# You could use other versions of Chrome, but you'd need to change the path.
# If you want to use other browser like Firefox, you'd need to change line 51 below.
chrome_options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'

# start browser with webdriver (chromedriver file in root) & options
driver = webdriver.Chrome(executable_path=os.path.abspath('chromedriver'),chrome_options=chrome_options)

# # COMMENTED OUT, BUT USEFUL IF YOU NEED TO DOWNLOAD FILES
# # change browser settings to allows downloads without prompt
# driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
# params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_path}}
# command_result = driver.execute('send_command', params)

# send get request
driver.get(url)

# set time of explicit wait for page elements
wait = WebDriverWait(driver, 10)

# look for button in form
submit = find_element(wait,'cfInputButton',By.CLASS_NAME)
# trigger click. this will make display the data
submit.click()

# paginate
first_page = [False]
# looks for pagination element below table
paginator = find_element(wait,'cfSearchNavigation',By.CLASS_NAME)
# creates os pages starting on page 2
list_pages = [a.get_attribute('href') for a in paginator.find_elements_by_tag_name('a')]
# joins all pages in a list. First page will be a False value to avoid paginations in iteration starting below
list_pages = first_page + list_pages

# initialize empty lists that will store data scraped
# every row in every page
rows = []
# every new entry
# will be looped over to send notifications
new_rows = []

# iterate over pages
# page 1 is extracted, then driver loads another page and extracts data again.
# data is appended to empty list above
for page in list_pages:
    if not page: # extract first page
        # find table in page with explicit wait
        table = find_element(wait,'cfOutputTableSmall',By.ID)
        # extract top level data from table
        data_from_table = extract_from_table(table)
        # iterate over extracted data, save employer information, create list of follow-up urls
        for d in data_from_table:
            rows.append(d)

    else: # extract other pages
        # send get request to paginate
        driver.get(page)
        # find table in page with explicit wait
        table = find_element(wait,'cfOutputTableSmall',By.ID)
        # extract top level data from table
        data_from_table = extract_from_table(table)
        # iterate over extracted data and append dicts to list (or pandas DataFrame??)
        for d in data_from_table:
            rows.append(d)

# checks data extracted against database
for notice in rows:
    # request current data from API
    employers = get('https://dig-warn-api.herokuapp.com/api/search/employers')
    employers = json.loads(employers.text)['data']

    # check if employer is in database:
    # creating list w comprehension to "filter" API response
    # assumption is this will always return 0 matches (meaning not in database) >>>
    # >>> or 1 match (meaning in database). If employer variable's length > 1, something is wrong
    employer = [x for x in employers if x['employer_name'] == notice['employer_name']]

    # if employer in db:
    # check if notice id is in notice list (by id)
    if employer:
        employer = employer[0]

        # if notice in list:
        # continue statement. nothing below in this loop will be executed >>>
        # >>> and we jump to the next row, restarting from the top
        if notice['notice_id'] in employer['notices']:
            print('notice already scraped')
            continue

        # if notice not in list:
        # navigate to detail page
        # extract data
        # create notice object
        # update employer object in database by pushing new id to notices array
        # post notice do database
        else:
            print('updating employer',notice['employer_name'], 'notice', notice['notice_id'])

            # navigate to detailed page url
            driver.get(notice['notice_url'])
            time.sleep(0.5)

            # find table and extract data from it
            table = find_element(wait,'td table',By.CSS_SELECTOR)
            detailed_data = extract_from_detail_page(table)

            # get employer unique id
            employer_id = employer["employer_id"]
            # compute current time
            timestamp = datetime.now().isoformat()

            # create notice object
            notice_obj = create_notice_object(notice,detailed_data,employer_id,timestamp)

            # add notice id to list in employer object
            # send put request
            put(f'https://dig-warn-api.herokuapp.com/api/update/employers?employerId={employer["employer_id"]}',\
                json={"notice_id":notice_obj['notice_id']})

            # add notice to collection in database
            # send post request
            post('https://dig-warn-api.herokuapp.com/api/post/notices',json=notice_obj)

            # add new row to list
            new_rows.append({**notice_obj,**{"employer_name":notice['employer_name']}})

    # if employer not in db:
    # navigate to detail page
    # extract data
    # create employer object
    # create notice object
    # post data do database
    else:
        print('creating employer',notice['employer_name'])
        print('creating notice',notice['notice_id'])

        # navigate to detailed page url
        driver.get(notice['notice_url'])
        # for some reason I cant explain, explicit wait was working perfectly, so added half a second wait here.
        time.sleep(0.5)

        # find table and extract data from it
        table = find_element(wait,'td table',By.CSS_SELECTOR)
        detailed_data = extract_from_detail_page(table)

        # create unique id
        employer_id = str(uuid4())
        # compute current time
        timestamp = datetime.now().isoformat()

        # create employer object
        employer_obj = create_employer_object(notice,employer_id,timestamp)

        # create notice object
        notice_obj = create_notice_object(notice,detailed_data,employer_id,timestamp)

        # add objects to collection in database
        # send post requests
        post('https://dig-warn-api.herokuapp.com/api/post/employers',json=employer_obj)
        post('https://dig-warn-api.herokuapp.com/api/post/notices',json=notice_obj)

        # add new row to list
        new_rows.append({**notice_obj,**{"employer_name":notice['employer_name']}})

if len(new_rows) > 0:
    send_notification(new_rows,s,pw)

# close browser
driver.close()
