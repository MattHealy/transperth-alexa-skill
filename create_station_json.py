import json
from constants import STATIONS

my_dict = {"name": "LIST_OF_STATIONS"}
my_dict['values'] = []

for trainline in STATIONS:
    for station in STATIONS[trainline]:
        station_obj = {"name": {"value": station}}
        if station_obj not in my_dict['values']:
            my_dict['values'].append(station_obj)

print(json.dumps(my_dict, indent=4, sort_keys=True))
