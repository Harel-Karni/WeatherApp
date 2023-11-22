import json
from enum import Enum
import datetime
import pytz
import requests


class Action(Enum):
    CREATE = 1
    DELETE = 2
    UPDATE = 3
    READ = 4


database_file = "database.json"


def db_event(list_name: str, action: Action, args: dict = None):
    if action == Action.READ:
        return get_db_list(list_name)
    elif action == Action.DELETE:
        return delete_item(list_name, args)
    elif action == Action.UPDATE:
        return update_item(list_name, args)
    elif action == Action.CREATE:
        return add_item(list_name, args)


def delete_item(list_name, args):
    item_id = args["item_id"]
    error_code, data = get_db_list(list_name)
    if error_code != 0:
        return error_code, data
    item_id_name = get_item_id_name(list_name)
    for item in data:
        if item[item_id_name] == item_id:
            del data[data.index(item)]
            update_db(list_name, data)
            break


def update_item(list_name, args):
    item_id = args["item_id"]
    new_item = args["item"]
    error_code, data = get_db_list(list_name)
    if error_code != 0:
        return error_code, data
    item_id_name = get_item_id_name(list_name)
    for item in data:
        if item[item_id_name] == item_id:
            data[data.index(item)] = new_item
            update_db(list_name, data)
            break


def add_item(list_name, args):
    new_item = args["item"]
    error_code, data = get_db_list(list_name)
    if error_code != 0:
        return error_code, data
    data.append(new_item)
    update_db(list_name, data)


def get_db_list(list_name=None):
    try:
        with open(database_file, "r") as file:
            list = json.load(file)
            file.close()
            return 0, list if list_name is None else list[list_name]
    except FileNotFoundError:
        return 1, "FileNotFoundError error"
    else:
        return 1, "Unexpected error"


def update_db(list_name, data):
    with open(database_file, "r") as file:
        list = json.load(file)
        file.close()
        list[list_name] = data
    with open(database_file, 'w') as f:
        json.dump(list, f, indent=2)
        f.close()


def get_item_id_name(list_name):
    if list_name == 'users':
        return 'user_id'
    elif list_name == 'cities':
        return 'city_code'


def update_users_temperature_scale_units(users, temperature_scale_units):
    for user in users:
        for unit in temperature_scale_units:
            if user["temp_scale_code"] == unit["temp_scale_code"]:
                user["temp_scale_display"] = unit["display"]
    return users


def update_users_cities(users, cities):
    for user in users:
        for city in cities:
            if user["default_city_code"] == city["code"]:
                user["default_city_name"] = city["display_name"]
    return users


def get_city_weather(city_code, units_code):
    api_key = 'ab69c559ff4df63bd47685182420c53a'
    base_url = 'http://api.openweathermap.org/data/2.5/weather'
    parameters = {
        'q'    : city_code,
        'appid': api_key,
        'units': units_code
    }
    try:
        response = requests.get(base_url, params=parameters)
        weather_data = response.json()
        if response.status_code == 200:
            return 0, weather_data
        else:
            return -1, f'Error: {weather_data["message"]}'
    except requests.exceptions.RequestException:
        return -1, 'Error: Could not retrieve weather data.'


def scale_symbols(temp_scale_code):
    if temp_scale_code == 'imperial':
        return 'F', 'miles/hour'
    elif temp_scale_code == 'standard':
        return 'K', 'meter/sec'
    elif temp_scale_code == 'metric':
        return 'C', 'meter/sec'


def get_open_weather_icon(icon_code):
    url = "https://openweathermap.org/img/wn/{}@2x.png".format(icon_code)
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None


def convert_utc_to_local_time(utc_timestamp, timezone):
    local_timestamp = datetime.datetime.utcfromtimestamp(utc_timestamp) + timezone
    return local_timestamp.strftime("%Y-%m-%d %H:%M:%S")


def get_weather_description_html(display_name, weather_description, icon_code):
    #display_name = weather_description["display_name"]
    #weather_description = weather_description["weather_description"]
    url_icon_code = "https://openweathermap.org/img/wn/{}@2x.png".format(icon_code)

    html_content = """
        <div style="display: flex; align-items: baseline;">
            <h3>{display_name}</h3>
            <h4>{weather_description}</h4>
            <span><img src = "{url_icon_code}"></span>
        </div>
      """.format(
            display_name=display_name,
            weather_description=weather_description,
            url_icon_code=url_icon_code
    )
    return html_content


def get_user_data_html(user):
    user_name = user["display_name"]
    default_city_name = user["default_city_name"]
    temp_scale_display = user["temp_scale_display"]
    html_content = """
    <h5>Selected User:</h5>
    <table  style="border: none;">
        <tr>
            <th><strong>User Name</strong></th>
            <td>{user_name}</td>
        </tr>
        <tr>
            <th><strong>Default City</strong></th>
            <td>{default_city_name}</td>
        </tr>
        <tr>
            <th><strong>Temp. Scale</strong></th>
            <td>{temp_scale_display}</td>
        </tr>
    </table>
    """.format(
            user_name=user_name,
            default_city_name=default_city_name,
            temp_scale_display=temp_scale_display
    )
    return html_content


def get_city_data_html(city):
    display_name = city["display_name"]
    time_zone = city["time_zone"]
    is_default = city["is_default"]
    html_content = """
    <h5>Selected City:</h5>
    <table  style="border: none;">
        <tr>
            <th><strong>City Name</strong></th>
            <td>{display_name}</td>
        </tr>
        <tr>
            <th><strong>Time Zone</strong></th>
            <td>{time_zone}</td>
        </tr>
        <tr>
            <th><strong>Is Default</strong></th>
            <td>{is_default}</td>
        </tr>
    </table>
    """.format(
            display_name=display_name,
            time_zone=time_zone,
            is_default=is_default
    )
    return html_content


def epoch_to_human_readable_date(epoch_seconds):
    datetime_obj = datetime.datetime.utcfromtimestamp(epoch_seconds)
    date_str = datetime_obj.strftime("%I:%M %p")
    return date_str