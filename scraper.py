from lxml import html
import requests
from bs4 import BeautifulSoup
import sys


# r = requests.get('http://info.kingcounty.gov/health/ehs/foodsafety/inspections/Results.aspx?Output=W&Business_Name=&Business_Address=&Longitude=&Latitude=&City=&Zip_Code=98102&Inspection_Type=All&Inspection_Start=3/1/2015&Inspection_End=3/1/2016&Inspection_Closed_Business=A&Violation_Points=&Violation_Red_Points=&Violation_Descr=&Fuzzy_Search=N&Sort=H')


INSPECTION_DOMAIN = 'http://info.kingcounty.gov'
INSPECTION_PATH = '/health/ehs/foodsafety/inspections/Results.aspx'
INSPECTION_PARAMS = {
    'Output': 'W',
    'Business_Name': '',
    'Business_Address': '',
    'Longitude': '',
    'Latitude': '',
    'City': '',
    'Zip_Code': '',
    'Inspection_Type': 'All',
    'Inspection_Start': '',
    'Inspection_End': '',
    'Inspection_Closed_Business': 'A',
    'Violation_Points': '',
    'Violation_Red_Points': '',
    'Violation_Descr': '',
    'Fuzzy_Search': 'N',
    'Sort': 'H'
}

def get_inspection_page(**kwargs):
    url = INSPECTION_DOMAIN + INSPECTION_PATH
    payload = INSPECTION_PARAMS.copy()
    for key, val in kwargs.items():
        if key in INSPECTION_PARAMS:
            params[key] = val
    req = requests.get(url, params=payload)
    req.raise_for_status()
    return req.content, req.encoding
    # It must accept keyword arguments for the possible query parameters
    # It will build a dictionary of request query parameters from incoming keywords
    # It will make a request to the King County server using this query
    # It will return the bytes content of the response and the encoding if there is no error
    # It will raise an error if there is a problem with the response


def load_inspection_page():
    url = INSPECTION_DOMAIN + INSPECTION_PATH
    payload = INSPECTION_PARAMS.copy()
    page = requests.get(url, params=payload)
    inspection_page_html = html.fromstring(page.content)
    print inspection_page_html


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(inspection_page_html, html5lib, from_encoding=encoding)
    print parsed


if __name__ == '__main__':
    kwargs = {
        'Inspection_Start': '3/1/15',
        'Inspection_End': '9/1/15',
        'Zip_Code': 98102
    }
    # if len(sys.argv) > 1 and sys.argv[1] == 'test'
    #     inspection_page_html, encoding = load_inspection_page()
    # else:
    #     inspection_page_html, encoding = get_inspection_page(**kwargs)

