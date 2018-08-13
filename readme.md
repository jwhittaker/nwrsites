## Introduction

**Webscrapes weather radio station tuning data and stores it in JSON**

A backend data gathering tool for offline records of emergency weather radio station locations and frequencies. Without internet or phone access, this provides an alternative for regional look-ups of weather stations in the USA and its territories. The data is gathered into an easier to parse JSON structure.

The NOAA site is scraped for the list of all NWR stations by county coverage and their state. The results are stored locally in JSON format for offline backup. Items gathered:

- List of weather radio stations by state
- List of county coverage by state
- URLs to state radio propagation maps
- List of weather radio marine stations
- List of NWR tx outages and special [notices posted](http://www.nws.noaa.gov/nwr/outages/outages.php)
- Last updated date posted per the NOAA webmaster
- 50 MB of http traffic for all national data gets stored as 2.8 MB of JSON, just under 6%

[Example archive - latest nwrdump download](https://github.com/jwhittaker/nwrdumps/archive/master.zip)

### Utility

It is useful to have offline backup copies of public data, especially for communications resources in times of emergencies. If the internet and cell service is out during an emergency, a radio becomes a valuable tool. This script gathers the latest data published to the NOAA website for all local weather stations and SAME codes. The website data can be printed out, but this tool was an exercise to prepare a backend for linking to future software.

### Future Applications

The NOAA site provides a lot of useful resources, but the frontend itself is outdated and could use improvement. This script's ability to automatically grab that data facilitates a way for 3rd party tools and  better front ends to use this data. It could go into an SQL database, an automatic radio programmer, or an app which highlights the local station and SAME code based on GPS coordinates (for those who have more rudimentary weather radios like myself).

**This project is open for:**
- Re-Use/improve the NOAA scraping methodology
- Create better data structures
- Develop frontends
- Develop utilities for mapping
- Develop utilities for radio programming

## Lazy Start

### Requirements
- Python
- Python library BeautifulSoup (`bs4`)
- Python library Requests (`requests`)

### Copy-Paste & Go

```bash
sudo apt install -y python-pip
pip install bs4 requests
git clone git@github.com:jwhittaker/nwrsites.git
cd nwrsites
./nwr.py
```

### Reading Results

```bash
cat states/AL.json | python -m json.tool | grep -i -C5 demo
```

### Archived Results Dump

[Latest nwrdump download](https://github.com/jwhittaker/nwrdumps/archive/master.zip)

## About NWR

[About NWR All Hazards on NOAA.gov](http://www.nws.noaa.gov/nwr/index.php)

### Initialisms
- **NOAA** - National Oceanic and Atmospheric Administration
- **SAME** - Specific Area Message Encoding (protocol)
- **NWR** - NOAA Weather Radio
- **FCC** - Federal Communication Commission
- **EAS** - Emergency Alert System
- **WAT** - Warning Alarm Tone
- **VHF** - Very High Frequency (radio band)
- **FM** - Frequency Modulation (radio technology)
- **TX** - Transmitter (referring to a weather radio station)

### Synopsis

NWR All Hazards is a nationwide network of radio stations broadcasting comprehensive weather forecasts and warnings 24/7/365. Additionally it may broadcast about weather watches, amber alerts, 911 outages, terrorism, national security, environmental hazards, natural disasters, and other hazard information. NWR is provided as a public service by the NOAA, part of the Department of Commerce. NWR includes ~1025 transmitters, covering all 50 states, adjacent coastal waters, and U.S. Territories.

## Listening

A weather radio receiver is required, as the frequencies are not within the design of a typical FM radio; the frequencies are outside of the band and have narrower bandwidths. Complete broadcast cycles are typically 3 to 8 minutes in length. It may also broadcast FCC EAS messages and public safety information.

## Frequencies

**VHF-FM, 25kHz bandwidth**

| Official Name |   Frequency | Marine | Public |
|:-------------:|------------:|:------:|:------:|
|      WX8      | 161.650 MHz |    21B |        |
|      WX9      | 161.775 MHz |    83B |        |
|      WX2      | 162.400 MHz |    36B |    1   |
|      WX4      | 162.425 MHz |    96B |    2   |
|      WX5      | 162.450 MHz |    37B |    3   |
|      WX3      | 162.475 MHz |    97B |    4   |
|      WX6      | 162.500 MHz |    38B |    5   |
|      WX7      | 162.525 MHz |    98B |    6   |
|      WX1      | 162.550 MHz |    39B |    7   |
|      WX10     | 163.275 MHz |   113B |        |

### SAME

- [NOAA Using NWR Same](http://www.nws.noaa.gov/nwr/info/usingsame.html)
- [Wikipedia details for SAME](https://en.wikipedia.org/wiki/Specific_Area_Message_Encoding)

A protocol used to encode EAS and NWR alert messages by county.

- *When an NWS office broadcasts a warning, watch or non-weather emergency, it also broadcasts a digital SAME code that may be heard as a very brief static burst, depending on the characteristics of the receiver. This SAME code contains the type of message, county(s) affected, and message expiration time.*
- *A programmed NWR SAME receiver will turn on for that message, with the listener hearing the 1050 Hz warning alarm tone as an attention signal, followed by the broadcast message.*
- *At the end of the broadcast message, listeners will hear a brief digital end-of-message static burst followed by a resumption of the NWR broadcast cycle.*

#### Four part messages

1. Header - digital - (AFSK data burst of 520.83 bps)
2. Attention Signal - audio - 8 to 10-second long 1050 Hz tone
3. Message - audio, video image, or video text
4. Tail - digital - End of Message (AFSK data burst of 520.83 bps)

#### Receiver

To program NWR SAME receivers with the proper county(s) and marine area(s) of choice, you need to know the 6-digit SAME code number. Then follow the directions in your radio's user's manual.

**Obtaining SAME Codes:**
- Online at the [United States and Territories Table](http://www.nws.noaa.gov/nwr/coverage/county_coverage.html)
- This script, which parses and organizes the data from the NWR coverage website mentioned
- By telephone at **1-888-NWR-SAME (1-888-697-7263)** for a voice menu

## Data Structure Examples

### State counties & stations

`states/AL.json`
```json
{
    "map": [
        "http://www.nws.noaa.gov/nwr/Maps/GIF/states/alabama.gif"
    ], 
    "counties": {
        "count": 157, 
        "updated": "August 10 2018 20:05:15 UTC", 
        "list": [
            {
                "nwrtx": "Demopolis", 
                "same": "001023", 
                "county": "Choctaw", 
                "frequency": "162.475", 
                "callsign": "WXL72", 
                "remarks": ""
            }, 
            {
                "nwrtx": "Demopolis", 
                "same": "001025", 
                "county": "Clarke", 
                "frequency": "162.475", 
                "callsign": "WXL72", 
                "remarks": ""
            }
        ]
    }, 
    "stations": {
        "count": 21, 
        "list": [
            {
                "gif": "http://www.nws.noaa.gov/nwr/Maps/GIF/WXL72.gif", 
                "callsign": "WXL72", 
                "frequency": "162.475", 
                "power": "1000", 
                "tx": "Jefferson", 
                "url": "http://www.nws.noaa.gov/nwr/coverage/site2.php?State=AL&Site=WXL72", 
                "pdf": "http://www.nws.noaa.gov/nwr/Maps/PDF/WXL72.pdf", 
                "site": "Demopolis", 
                "wfo": "Calera, AL"
            }, 
        ]
    }
}
```

### Marine

`marine/atl.json`
```json
{
    "count": 436, 
    "code": "atl", 
    "list": [
        {
            "power": "1000", 
            "frequency": "162.400", 
            "callsign": "KEC93", 
            "description": "Synopsis for Eastport ME to Stonington (Deer Isle) ME out 25NM", 
            "tx": "Ellsworth ME", 
            "area": "", 
            "remarks": "", 
            "type": "*", 
            "same": "073005", 
            "zoneid": "ANZ005"
        }, 
    ], 
    "name": "Atlantic"
}
```

### Outages & Notices

`outages/outages.json`
```json
{
    "count": 9, 
    "notices": [
        [
            "KWN62 Ord, NE transmitter Out of Service (Updated 6/4/18)", 
            "(6/4/18) Transmitter is operating from a temporary antenna due to collapse of the radio tower at this site.  Restoration to normal service is expected in 6-8 months with the construction of a new tower."
        ]
    ], 
    "updated": "08/10/2018 20:05:15 UTC", 
    "list": [
        {
            "status": "OUT OF SERVICE", 
            "wfo": "North Little Rock AR", 
            "tx": "Morrilton", 
            "state": "AR", 
            "callsign": "KXI91", 
            "frequency": "162.475"
        }, 
        {
            "status": "DEGRADED", 
            "wfo": "Hastings NE", 
            "tx": "Ord", 
            "state": "NE", 
            "callsign": "KWN62", 
            "frequency": "162.525"
        }
    ]
}
```
