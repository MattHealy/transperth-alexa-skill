import logging
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from transperth import Transperth
from constants import TRAINLINES, STATIONS, DIRECTIONS


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch
def launch():
    trainline_msg = render_template('trainlines')
    return question(trainline_msg)


@ask.intent("TrainlineIntent", mapping={'trainline': 'TrainLine'})
def trainanswer(trainline):
    if trainline.lower() not in TRAINLINES:
        return supported_trainlines()
    else:
        session.attributes['trainline'] = trainline
        direction_msg = render_template('direction')
        return question(direction_msg).reprompt(direction_msg)


@ask.intent("DirectionIntent", mapping={'direction': 'Direction'})
def directionanswer(direction):
    if direction.lower() not in DIRECTIONS:
        direction_msg = render_template('direction')
        return question(direction_msg)
    else:
        session.attributes['direction'] = direction
        station_msg = render_template('station')
        return question(station_msg).reprompt(station_msg)


@ask.intent("StationIntent", mapping={'station': 'Station'})
def stationanswer(station):
    trainline = session.attributes['trainline']
    if station.lower() not in STATIONS[trainline]:
        return supported_stations(trainline)
    else:
        session.attributes['station'] = station
        return get_next_time()


@ask.intent("OneShotStationIntent",
            mapping={'station': 'Station', 'trainline': 'TrainLine',
                     'direction': 'Direction'},
            default={'direction': 'to perth'})
def one_shot_stationanswer(trainline, direction, station):

    if station is None:
        print("station=None provided")
        return launch()

    if not station_exists(station.lower()):
        print("station_exists returned FALSE")
        return launch()

    if trainline is not None and trainline.lower() not in TRAINLINES:
        return supported_trainlines()
    elif trainline:
        session.attributes['trainline'] = trainline
    else:
        trainline = get_trainline_from_station(station.lower())
        session.attributes['trainline'] = trainline

    if station.lower() not in STATIONS[trainline]:
        return supported_stations(trainline)
    else:
        session.attributes['station'] = station

    if direction.lower() not in DIRECTIONS:
        return launch()
    else:
        session.attributes['direction'] = direction

    return get_next_time()


def get_next_time():

    direction = session.attributes['direction']
    station = session.attributes['station']
    trainline = session.attributes['trainline']

    next_time, message = Transperth().next_time(trainline, direction, station)

    if next_time:
        statement_text = render_template('next_time', station=station,
                                         next_time=next_time)
    else:
        statement_text = render_template('error_getting_times',
                                         message=message)

    return statement(statement_text).simple_card("Transperth", statement_text)


def get_trainline_from_station(station):
    for trainline in TRAINLINES:
        if station in STATIONS[trainline]:
            return trainline

    return None


def station_exists(station):
    for trainline in STATIONS:
        if station in STATIONS[trainline]:
            return True
    return False


@ask.intent('SupportedTrainlinesIntent')
def supported_trainlines():
    trainlines = ", ".join(sorted(TRAINLINES))
    list_trainlines_text = render_template('list_trainlines',
                                           trainlines=trainlines)
    list_trainlines_reprompt_text = render_template('list_trainlines_reprompt')
    return question(list_trainlines_text) \
        .reprompt(list_trainlines_reprompt_text)


@ask.intent('SupportedStationsIntent', mapping={'trainline': 'TrainLine'})
def supported_stations(trainline):

    stations = ", ".join(sorted(STATIONS[trainline]))

    list_stations_text = render_template('list_stations', trainline=trainline,
                                         stations=stations)
    list_stations_reprompt_text = render_template('list_stations_reprompt')

    return question(list_stations_text).reprompt(list_stations_reprompt_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = render_template('help')
    list_trainlines_reprompt_text = render_template('list_trainlines_reprompt')
    return question(help_text).reprompt(list_trainlines_reprompt_text)


@ask.intent('AMAZON.StopIntent')
def stop():
    bye_text = render_template('bye')
    return statement(bye_text)


@ask.intent('AMAZON.CancelIntent')
def cancel():
    bye_text = render_template('bye')
    return statement(bye_text)


if __name__ == '__main__':
    app.run(debug=True)
