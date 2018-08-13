#!/usr/bin/env python


import os
import re
import json
import requests
from bs4 import BeautifulSoup


# URLs were made global vars for visibility and some reuse across functions
url_map_base = 'http://www.nws.noaa.gov/nwr'
url_coverage = 'http://www.nws.noaa.gov/nwr/coverage/'
url_state_base = 'http://www.nws.noaa.gov/nwr/Maps/PHP/' # + st + .php required
url_marine_base = 'http://www.nws.noaa.gov/om/marine/'
url_outages = 'http://www.nws.noaa.gov/nwr/outages/outages.php'
total_bytes = 0

def soup_init(url):
    global total_bytes
    r = requests.get(url)
    total_bytes += len(r.content)
    soup = BeautifulSoup(r.text, 'lxml')
    
    return soup
      
def county_coverage(soup):
    ''' Also tries to format it for JSON
    Locate the only table with "header" column tags.
    Navigate up to its parent row and up to the parent "tbody."
    Then find all rows within the table body and scan the columns.
    http://www.nws.noaa.gov/nwr/coverage/county_coverage.html'''
    counties = {}
    counties['updated'] = county_update(soup)
    counties['list'] = []
    cnt = 0
    rows = soup.find('th').parent.parent.find_all('tr')
    for tr in rows:
        row = []
        row_dict = []
        cols = tr.find_all('td')
        if cols:
            for td in cols:
                cell = td.text.strip()
                row.append(cell)
            cnt += 1
            entry = { \
                'county': row[0], \
                'same': row[1], \
                'nwrtx': row[2], \
                'callsign': row[3], \
                'frequency': row[4], \
                'remarks': row[5], \
            }
            counties['list'].append(entry)
    counties['count'] = cnt
            
    return counties

def county_update(soup):
    updated = soup.find('td', text=re.compile('county coverage as of', flags=re.IGNORECASE)).text
    updated = re.sub('\.|\(|\)', '', updated)
    updated = re.sub('\s+', ' ', updated)
    updated = re.sub('county coverage as of ?', '', updated, flags=re.IGNORECASE)

    return updated

def station_coverage(soup):
    ''' Also tries to format it for JSON
    Locate the only table with "header" column tags.
    Navigate up to its parent row and up to the parent "tbody."
    Then find all rows within the table body and scan the columns.
    http://www.nws.noaa.gov/nwr/coverage/station_listing.html'''

    stations = {}
    stations['list'] = []
    cnt = 0
    rows = soup.find('th').parent.parent.find_all('tr')
    for tr in rows:
        row = []
        row_dict = []
        cols = tr.find_all('td')
        if cols:
            for td in cols:
                link = td.find('a', href=True)
                if link:
                    url = url_coverage + link['href']
                cell = td.text.strip()
                row.append(cell)
            cnt += 1
            entry = { \
                'site': row[0], \
                'tx': row[1], \
                'callsign': row[2], \
                'frequency': row[3], \
                'power': row[4], \
                'wfo': row[5], \
                'url': url, \
                'gif': site_coverage_gif(url), \
                'pdf': site_coverage_pdf(url), \
            }
            stations['list'].append(entry)
    stations['count'] = cnt

    return stations    

def marine_zones():
    '''Get the list of zones
    Reference URLs:
    http://www.nws.noaa.gov/om/marine/marsameatl.htm
    http://www.nws.noaa.gov/om/marine/marsamemex.htm
    http://www.nws.noaa.gov/om/marine/marsamegtl.htm
    http://www.nws.noaa.gov/om/marine/marsamepac.htm
    http://www.nws.noaa.gov/om/marine/marsameak.htm
    http://www.nws.noaa.gov/om/marine/marsamehi.htm
    '''
    soup = soup_init(url_marine_base + 'marsame.htm')
    marines = []
    sames = soup.find_all('a', {'href': re.compile('marsame')})
    for ss in sames:
        name = ss.get_text()
        url = ss['href']
        code = re.match(r'marsame([a-z]+)\.htm', url)
        code = code.group(1)
        # list of tuples
        marines.append((name, code, url_marine_base + url))
    
    return marines
    
def marine_stations(soup):
    '''Marine table has no "th" header, so the largest is chosen
    O - Offshore forecast zone
    # - Used for watch/warning purposes only and not for routine forecasts
    W - Watch/warnings broadcast only, not routine forecasts
    * - Forecast synopsis 
    @ - Routine forecasts only, no warnings'''
    marine = {}
    marine['list'] = []
    cnt = 0
    tables = soup.find_all('table')
    tbl_lens = []
    # largest table on the page is the likely list we want
    for result in tables:
        tbl_lens.append(len(result))
    # reassign to the longest index
    table = tables[tbl_lens.index(max(tbl_lens))]
    rows = table.find_all('tr')
    # proceed as usual
    for tr in rows:
        row = []
        row_dict = []
        cols = tr.find_all('td')
        if cols:
            for td in cols:
                cell = td.text.strip()
                cell = re.sub('\s+', ' ', cell)
                row.append(cell)
            cnt += 1
            entry = { \
                'zoneid': row[0], \
                'area': row[1], \
                'description': row[2], \
                'same': row[3], \
                'type': row[4], \
                'tx': row[5], \
                'frequency': row[6], \
                'callsign': row[7], \
                'power': row[8], \
                'remarks': '', \
            }
            if len(row) == 10:
                entry['remarks'] = row[9]
            if entry['callsign']:
                marine['list'].append(entry)
    marine['count'] = cnt
            
    return marine
    
def site_coverage_gif(url_coverage):
    soup = soup_init(url_coverage)
    map = soup.find('img', {'src': re.compile(r'maps', flags=re.IGNORECASE)})
    map = url_map_base + map['src'].replace('..', '')
    
    return map

def site_coverage_pdf(url_coverage):
    soup = soup_init(url_coverage)
    map = soup.find('a', {'href': re.compile(r'/Maps/PDF/', flags=re.IGNORECASE)})
    map = url_map_base + map['href'].replace('..', '')
    
    return map
    
def state_coverage(state):
    map = []
    if len(state) != 2:
        return 'bad two-letter state code'
    if state == 'AK':
        state = ['AK-sw', 'AK-sc', 'AK-nc', 'AK-se']
    else:
        state = [state]
    for st in state:
        url = url_state_base + st + '.php'
        soup = soup_init(url)
        map_state = soup.find('img', {'src': re.compile(r'states.*gif', flags=re.IGNORECASE)})
        if map_state:
            map_state = url_map_base + map_state['src'].replace('../..', '')
            map.append(map_state)
    
    return map

def outages():
    soup = soup_init(url_outages)
    outages = {}
    outages['list'] = []
    cnt = 0
    try:
        updated = soup.find('p', text=re.compile(r'This information was current', flags=re.IGNORECASE))
        updated = updated.text
        updated = re.sub('\.|\(|\)', ' ', updated)
        updated = re.sub('\s+', ' ', updated)
        updated = re.match(r'This information was current on: (.*)', updated, flags=re.IGNORECASE)
        outages['updated'] = updated.group(1)
    except:
        outages['updated'] = 'scrape update needed--website format changed'
    # Find the correct table
    for tbl in soup.find_all('table'):
        result = tbl.find(string=re.compile(r'Frequency', flags=re.IGNORECASE))
        if result:
            table = result.find_parent('table')
            break
    # Now proceed
    if not table:
        return "error"
    rows = table.find_all('tr')
    for tr in rows:
        row = []
        row_dict = []
        cols = tr.find_all('td')
        if cols:
            for td in cols:
                cell = td.text.strip()
                row.append(cell)
            cnt += 1
            entry = { \
                'state': row[0], \
                'tx': row[1], \
                'callsign': row[2], \
                'frequency': row[3], \
                'wfo': row[4], \
                'status': row[5], \
            }
            outages['list'].append(entry)
    outages['count'] = cnt
    # Special Notices
    outages['notices'] = []
    headings = []
    messages = []
    head = soup.find_all('div', {'id': re.compile(r'headerdiv', flags=re.IGNORECASE)})
    msg = soup.find_all('div', {'id': re.compile(r'Advisory', flags=re.IGNORECASE)})
    for hh in head:
        header = hh.text.strip()
        header = header.replace('[+]', '')
        headings.append(header)
    for mm in msg:
        message = mm.find('p').text
        messages.append(message)
    for nn in xrange(len(headings)):
        entry = [headings[nn], messages[nn]]
        outages['notices'].append(entry)
    
    return outages
    
def scrape_states():
    '''Creates json data for nationwide stations and by county lookup'''
    state_list = ['AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL', 'GA', \
        'HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI', \
        'MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND', \
        'OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA', \
        'WA','WV','WI','WY','AS','GU','MH','FM','MP','PW','PR','VI']
    state = {}

    for st in state_list:
        print('working on',st)
        url = 'http://www.nws.noaa.gov/nwr/coverage/ccov.php?State=' + st
        soup = soup_init(url)
        counties = county_coverage(soup)
        
        url = 'http://www.nws.noaa.gov/nwr/coverage/stations.php?State=' + st
        soup = soup_init(url)
        stations = station_coverage(soup)
        
        state['counties'] = counties
        state['stations'] = stations
        state['map'] = state_coverage(st)

        data = json.dumps(state, indent=4)
        try:
            # os more compatible, but pathlib better
            os.makedirs('states')
        except OSError:
            if not os.path.isdir('states'):
                raise
        with open('states/' + st + '.json', 'w') as f:
            f.write(data)
    
def scrape_marine():
    marine = {}
    marines = marine_zones()
    for mm in marines:
        name = mm[0]
        print('working on', name)
        code = mm[1]
        url = mm[2]
        marine.update({'name': name})
        marine.update({'code': code})
        soup = soup_init(url)
        marine.update(marine_stations(soup))

        data = json.dumps(marine, indent=4)
        try: 
            os.makedirs('marine')
        except OSError:
            if not os.path.isdir('marine'):
                raise
        with open('marine/' + code + '.json', 'w') as f:
            f.write(data)

def scrape_outages():
    outage = outages()
    data = json.dumps(outage, indent=4)
    try: 
        os.makedirs('outages')
    except OSError:
        if not os.path.isdir('outages'):
            raise
    with open('outages/outages.json', 'w') as f:
        f.write(data)
            
def main():
    print("collecting state & station data")
    scrape_states()
    print("collecting marine data")
    scrape_marine()
    print("collecting outages & special reports")
    scrape_outages()
    print('kilobytes transferred:', total_bytes/1024)
    print('all done')

main()