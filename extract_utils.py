# selenium method for explicit wait
# is used to make script wait a bit while browser loads elements
from selenium.webdriver.support import expected_conditions as EC

# regex
import re

# defining functions
# function generalizes finding element w/ explicit wait
def find_element(w,search_string,search_by):
    try:
        # use explicit wait until object is found. search happens follown By Selenium classes
        element = w.until(EC.presence_of_element_located((search_by,search_string)))
    except:
        # error catching in case finding element fails
        print(f'{search_string} element not found.')
        driver.close()
        return None

    return element

# extract data from table in main pages
# function will be an iterator.
# it doesnt return, but yields
def extract_from_table(tb):
    # find all <tr>s in <tbody> that contain data, skip header row
    rows = tb.find_elements_by_class_name('cfOutputTableRow')

    # iterate over <tr>s and extract data.
    # format data as dict
    for row in rows:
        cells = row.find_elements_by_tag_name('td')
        url = cells[0].find_element_by_tag_name('a').get_attribute('href')

        # create dict
        data_obj = {
            'employer_name':cells[0].text.strip(),
            'city':cells[1].text.strip(),
            'zip':cells[2].text.strip(),
            'lwib_area':cells[3].text.strip(),
            'notice_date':cells[4].text.strip(),
            'notice_url':cells[0].find_element_by_tag_name('a').get_attribute('href'),
            'notice_id':int(re.search(r'id=(\d*)&',url).group(1))
        }

        yield data_obj

# extract data from table in detailed pages
# function generalizes finding element w/ explicit wait
def extract_from_detail_page(tb):
    # find all <tr>s in <tbody> that contain data, skip header row
    rows = tb.find_elements_by_class_name('cfOutputTableRow')
    rows.pop(4)
    rows.pop(0)

    # initalize empty list to gather data points
    d = []
    # list of headers to create data
    headers = ['street_address','city','state','total_affected']

    for row in rows:
        d.append(row.find_elements_by_tag_name('td')[1].text)

    return {headers[i]:d[i].strip() for i in range(len(headers))}
