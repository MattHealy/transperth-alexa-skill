import requests
from bs4 import BeautifulSoup


class Transperth(object):

    def __init__(self):
        self.url = 'http://136213.mobi/Trains/TrainResults.aspx'

    def next_time(self, trainline, direction, station):

        params = {
            "trainline": trainline,
            "direction": direction,
            "station": station
        }

        try:
            r = requests.get(self.url, params=params, timeout=2)
            r.raise_for_status()
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except requests.exceptions.HTTPError:
            return False, "404 not found"
        except requests.exceptions.ConnectionError:
            return False, "Connection error"
        except:
            return False, "Unknown error"

        html = r.content
        soup = BeautifulSoup(html, 'html.parser')

        try:
            results = soup.find(id='pnlLiveTimes')
            row = results.find_all('div', class_='tpm_row')[0]
            headings = row.find_all('a', class_='tpm_row_heading')
            span = headings[0].find_all('span')
            next_trip = span[0].contents[0]
            next_time = next_trip.split()[2]
            return next_time, ""
        except:
            return False, "Couldn't find train times"
