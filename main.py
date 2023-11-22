import streamlit as st
from functions import (get_db_list, update_users_temperature_scale_units,
                       update_users_cities, get_city_weather, get_city_data_html, get_user_data_html,
                       scale_symbols, get_weather_description_html, epoch_to_human_readable_date)

st.set_page_config(
        page_title="Weather App",
        page_icon="🧊",
        layout="centered")
# ================================DATA
err_code, users = get_db_list('users')
err_code, cities = get_db_list('cities')
err_code, temperature_scale_units = get_db_list('temperature_scale_units')

users = update_users_cities(users, cities)
users = update_users_temperature_scale_units(users, temperature_scale_units)
cities_list = {city["display_name"]: city for city in cities}
users_list = {user["display_name"]: user for user in users}
users_keys = users_list.keys()
cities_keys = cities_list.keys()
# ==================================
# To run this app, use the command line to navigate to the app's directory and type:
# streamlit run main.py
st.title('Weather App')
st.header("POC by :blue[Harel Karni]", divider="green")
st.caption(
        'This application demonstrates, as a project on the DC course, the implementation \
        of Python functionality with the help of a weather display application, and user preferences.')
temp_scale_code = 'metric'
scale_symbol , wind_speed = scale_symbols(temp_scale_code)

col1, col2 = st.columns(2)
with (col1):
    selected_user = st.selectbox(label="", label_visibility='collapsed', options=users_keys, index=None,
                                 placeholder="select a user")

    if  selected_user:
        user = users_list[selected_user]
        scale_symbol, wind_speed = scale_symbols(user["temp_scale_code"])
        st.markdown(get_user_data_html(user),
                    unsafe_allow_html=True)
        selected_city_index = user["default_city_index"]
    else:
        selected_city_index = 0

with (col2):
    selected_city = st.selectbox(label="", label_visibility='collapsed', options=cities_keys,
                                 index=selected_city_index, placeholder="select a city")
    if not selected_city:
        st.stop()

    city = cities_list[selected_city]
    st.markdown(get_city_data_html(city), unsafe_allow_html=True)
    err_code, weather_data = get_city_weather(selected_city, temp_scale_code)
    #st.caption(weather_data)
    if err_code != 0:
        st.warning(weather_data)

if not selected_city:
    st.stop()
# https://share.streamlit.io/streamlit/emoji-shortcodes
# https://docs.streamlit.io/library/api-reference/data/st.metric
st.divider()
st.markdown(get_weather_description_html(weather_data["name"],
                                         weather_data["weather"][0]["description"] ,
                                         str(weather_data["weather"][0]["icon"]))
    , unsafe_allow_html=True
)
st.divider()
metrict1 = st.container()
with metrict1:
    '''
    #### ***Weather condition***
    '''
    col4, col5, col5a, col5b = st.columns(4)
    with col4:
        temp_text = str(weather_data["main"]["temp"]) + " °" + scale_symbol
        st.metric(label="Temperature", value=temp_text)
    with col5:
        feels_like_text = str(weather_data["main"]["feels_like"]) + " °" + scale_symbol
        st.metric("Temperature feels like", feels_like_text,
                  help='This temperature parameter accounts for the human perception of weather.')
    with col5a:
        pressure_text = str(weather_data["main"]["pressure"]) + " hPa"
        st.metric(label="Pressure", value=pressure_text, help='Atmospheric pressure on the sea level, hPa')
    with col5b:
        humidity_text = str(weather_data["main"]["humidity"]) + " %"
        st.metric(label="Humidity", value=humidity_text)
st.divider()
with st.container():
    '''
    #### ***Wind, Cloudiness and Visibility***
    '''
    col6, col7, col8, col9 = st.columns(4)
    with col6:
        wind_speed_text = str(weather_data["wind"]["speed"]) + wind_speed
        st.metric(label="Wind Speed", value=wind_speed_text)
    with col7:
        wind_direction_text = str(weather_data["wind"]["deg"]) + "°"
        st.metric(label="Wind direction", value=wind_direction_text, help="Wind direction, degrees (meteorological)")
    with col8:
        cloudiness_text = str(weather_data["clouds"]["all"]) + " %"
        st.metric(label="Cloudiness", value=cloudiness_text)
    with col9:
        visibility_text = str(weather_data["visibility"]) + " m"
        st.metric(label="Visibility", value=visibility_text, help="The maximum value of the visibility is 10 km")
st.divider()
metrict4 = st.container()
with metrict4:
    '''
    #### :sunglasses:  ***Local Time, Sunrise and Sunset time***
    '''
    col14, col15, col16 = st.columns(3)
    with col14:
        st.caption('**Current Time**')
        time_text = epoch_to_human_readable_date(weather_data["dt"])
        st.subheader(time_text)
    with col15:
        st.caption('**:sunglasses: Sunrise time**')
        sunrise_time_text = epoch_to_human_readable_date(weather_data["sys"]["sunrise"])
        st.subheader(sunrise_time_text)
    with col16:
        st.caption('**Sunset time**')
        sunset_time_text = epoch_to_human_readable_date(weather_data["sys"]["sunset"]) #convert_utc_to_local_time(weather_data["sys"]["sunset"], pytz.timezone("Asia/Jerusalem"))
        st.subheader(sunset_time_text)
st.header("Data Tables", divider=True)
metrict5 = st.container()
with metrict5:
    col17, col18 = st.columns(2)
    with col17:
        st.subheader("Users")
        st.dataframe(
                users,
                hide_index=True,
                column_order=("user_id", "display_name", "default_city_name", "temp_scale_display"),
                column_config=dict(user_id=st.column_config.TextColumn("User ID", disabled=True),
                                   display_name=st.column_config.TextColumn("User Name"),
                                   default_city_name=st.column_config.TextColumn("Default City"),
                                   temp_scale_display=st.column_config.TextColumn("Temp Scale")),
        )

    with col18:
        st.subheader("Cities")
        st.dataframe(
                cities,
                hide_index=True,
                column_order=("display_name", "code", "time_zone", "is_default"),
                column_config=dict(display_name=st.column_config.TextColumn("City Name"),
                                   code=st.column_config.TextColumn("City Code"),
                                   time_zone=st.column_config.TextColumn("Time Zone"),
                                   is_default=st.column_config.TextColumn("Is Default")),
        )

st.divider()
data: dict[str, list[float]] = {
    "latitude" : [float(weather_data["coord"]["lat"])],
    "longitude": [float(weather_data["coord"]["lon"])]
}
st.map(data, zoom=10)


