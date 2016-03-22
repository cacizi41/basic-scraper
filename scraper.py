import requests


r = requests.get('http://info.kingcounty.gov/health/ehs/foodsafety/inspections/Results.aspx?Output=W&Business_Name=&Business_Address=&Longitude=&Latitude=&City=&Zip_Code=98102&Inspection_Type=All&Inspection_Start=3/1/2015&Inspection_End=3/1/2016&Inspection_Closed_Business=A&Violation_Points=&Violation_Red_Points=&Violation_Descr=&Fuzzy_Search=N&Sort=H')
print(r)


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

def get_inspection_page(domain, path, params):
    # It must accept keyword arguments for the possible query parameters
    # It will build a dictionary of request query parameters from incoming keywords
    # It will make a request to the King County server using this query
    # It will return the bytes content of the response and the encoding if there is no error
    # It will raise an error if there is a problem with the response