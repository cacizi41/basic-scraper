import requests
import io
from bs4 import BeautifulSoup
import sys
import geocoder
import re
import json
from pprint import pprint
import lxml


DOMAIN = 'http://info.kingcounty.gov'
PATH = '/health/ehs/foodsafety/inspections/Results.aspx'
PARAMS = {
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
    """Get data and encoding from web page."""
    url = DOMAIN + PATH
    params = PARAMS.copy()
    for key, val in kwargs.items():
        if key in PARAMS:
            params[key] = val
    req = requests.get(url, params=params)
    req.raise_for_status()
    write_inspection_page('inspection_page.html', req.content)
    return req.content, req.encoding


def write_inspection_page(file, data):
    """Write data into file."""
    with io.open(file, 'wb') as file:
        file.write(data)


def load_inspection_page(file):
    """Read file."""
    with io.open(file, 'rb') as file:
        return file.read()


def parse_source(html, encoding='utf-8'):
    """Parse html using beautiful soup."""
    parsed = BeautifulSoup(html, 'html5lib', from_encoding=encoding)
    return parsed


def extract_data_listings(html):
    """Find div sections in html."""
    id_finder = re.compile(r'PR[\d]+~')
    return html.find_all('div', id=id_finder)


def has_two_tds(ele):
    """Find table rows w two table data."""
    is_tr = ele.name == 'tr'
    td_children = ele.find_all('td', recursive=False)
    has_two = len(td_children) == 2
    return is_tr and has_two


def clean_data(td):
    """Clean up data, striping off unwanted characters."""
    data = td.string
    # print(type(data))
    try:
        return data.strip(" \n:-")
    except AttributeError:
        return u""


def extract_restaurant_metadata(elem):
    """Extract restaurants table data."""
    metadata_rows = elem.find('tbody').find_all(has_two_tds, recursice=False)
    rdata = {}
    current_lable = ''
    for row in metadata_rows:
        key_cell, val_cell = row.find_all('td', recursive=False)
        new_lable = clean_data(key_cell)
        current_lable = new_lable if new_lable else current_lable
        rdata.setdefault(current_lable, []).append(clean_data(val_cell))
    return rdata


def is_inspection_row(elem):
    """Find rows start with inspection."""
    is_tr = elem.name == 'tr'
    if not is_tr:
        return False
    td_children = elem.find_all('td', recursive=False)
    has_four = len(td_children) == 4
    this_text = clean_data(td_children[0]).lower()
    contains_word = 'inspection' in this_text
    does_not_start = not this_text.startswith('inspection')
    return is_tr and has_four and contains_word and does_not_start


def extract_score_data(elem):
    """Extract inspection score data."""
    inspection_rows = elem.find_all(is_inspection_row)
    samples = len(inspection_rows)
    total = high_score = average = 0
    for row in inspection_rows:
        str_val = clean_data(row.find_all('td')[2])
        try:
            int_val = int(str_val)
        except(ValueError, TypeError):
            samples -= 1
        else:
            total += int_val
        high_score = int_val if int_val > high_score else high_score
    if samples:
        average = total/float(samples)
    data = {
        u'Average Score': average,
        u'high_score': high_score,
        u'Total Inspections': samples
    }
    return data


def generate_results(test=False, count=10):
    kwargs = {
        'Inspection_Start': '2/1/2013',
        'Inspection_End': '2/1/2015',
        'Zip_Code': '98109'
    }
    if test:
        html = load_inspection_page('inspection_page.html')
        doc = parse_source(html)
        encoding = 'utf-8'
    else:
        html, encoding = get_inspection_page(**kwargs)
        doc = parse_source(html, encoding)
    listings = extract_data_listings(doc)
    for listing in listings[:count]:
        metadata = extract_restaurant_metadata(listing)
        score_data = extract_score_data(listing)
        metadata.update(score_data)
        yield metadata
        # print(metadata)


def get_geojson(result):
    address = " ".join(result.get('Address', ''))
    if not address:
        return None
    geocoded = geocoder.google(address)
    geojson = geocoded.geojson
    inspection_data = {}
    useful_keys = (
        'Business Name', 'Average Score', 'Total Inspections', 'High Score', 'Address',
    )
    for key, val in result.items():
        if key not in useful_keys:
            continue
        if isinstance(val, list):
            val = " ".join(val)
        inspection_data[key] = val
    new_address = geojson['properties'].get('address')
    if new_address:
        inspection_data['Address'] = new_address
    geojson['properties'] = inspection_data
    return geojson


if __name__ == '__main__':
    test = len(sys.argv) > 1 and sys.argv[1] == 'test'
    total_result = {'type': 'Featurecollection', 'features': []}
    for result in generate_results(test):
        geo_result = get_geojson(result)
        pprint(geo_result)
        total_result['features'].append(geo_result)
    with open('restaurants_map.json', 'w') as fh:
        json.dump(total_result, fh)
