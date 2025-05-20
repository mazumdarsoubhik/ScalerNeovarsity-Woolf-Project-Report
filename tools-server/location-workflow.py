import os
import numpy as np
import pandas as pd
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.distance import distance

# Load API key from environment variable
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Initialize geolocator
geolocator = Nominatim(user_agent="geo_spiral")

def generate_spiral_points(state: State) -> State:
    lat_center = 12.9716
    lon_center = 77.5946
    radius_km = 300
    num_points = 200
    distance_step = np.sqrt((radius_km**2) / num_points)
    angle_step = 137.5

    points = []
    for i in range(num_points):
        r = distance_step * np.sqrt(i)
        theta = np.radians(i * angle_step)
        if r > radius_km:
            break
        new_point = distance(kilometers=r).destination((lat_center, lon_center), np.degrees(theta))
        points.append((new_point.latitude, new_point.longitude))

    df = pd.DataFrame(points, columns=["Latitude", "Longitude"])
    state["df"] = df
    return state

def fetch_address(state: State) -> State:
    df = state["df"]

    def get_address(lat, lon):
        try:
            location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True)
            return location.address if location else "Unknown Location"
        except GeocoderTimedOut:
            return "Timeout Error"

    df["Address"] = df.apply(lambda row: get_address(row["Latitude"], row["Longitude"]), axis=1)
    state["df"] = df
    return state

def fetch_weather_data(state: State) -> State:
    df = state["df"]

    def get_weather(lat, lon):
        if not API_KEY:
            return {"error": "API key not found"}
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&exclude=minutely,hourly&appid={API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    df["Weather"] = df.apply(lambda row: get_weather(row["Latitude"], row["Longitude"]), axis=1)
    state["df"] = df
    return state

def calculate_weekly_avg_max_temp(state: State) -> State:
    df = state["df"]

    def get_weekly_avg_temp(weather_data):
        try:
            daily_forecast = weather_data.get("daily", [])
            if not daily_forecast:
                main_content = weather_data.get("main", {})
                return round(main_content.get("temp_max", 0) - 273.15, 1)
            max_temps_celsius = [(day["temp"]["max"] - 273.15) for day in daily_forecast]
            return sum(max_temps_celsius) / len(max_temps_celsius)
        except (KeyError, TypeError):
            return None

    df["Weekly Temperature"] = df["Weather"].apply(get_weekly_avg_temp)
    state["df"] = df
    return state

def filter_final_result(state: State) -> State:
    df = state["df"]
    # Example filter: remove rows with missing temperature
    df = df[df["Weekly Temperature"].notnull()]
    state["df"] = df
    return state


from langgraph.graph import StateGraph

# Initialize the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("generate_spiral_points", generate_spiral_points)
workflow.add_node("fetch_address", fetch_address)
workflow.add_node("fetch_weather_data", fetch_weather_data)
workflow.add_node("calculate_weekly_avg_max_temp", calculate_weekly_avg_max_temp)
workflow.add_node("filter_final_result", filter_final_result)

# Define edges
workflow.set_entry_point("generate_spiral_points")
workflow.add_edge("generate_spiral_points", "fetch_address")
workflow.add_edge("fetch_address", "fetch_weather_data")
workflow.add_edge("fetch_weather_data", "calculate_weekly_avg_max_temp")
workflow.add_edge("calculate_weekly_avg_max_temp", "filter_final_result")
workflow.set_finish_point("filter_final_result")

# Compile the graph
app = workflow.compile()


# Initialize the state
initial_state = {}

# Execute the workflow
final_state = app.invoke(initial_state)

# Retrieve the resulting DataFrame
result_df = final_state["df"]

# Save to CSV
result_df.to_csv("spiral_coordinates_with_addresses_and_temperature.csv", index=False)
print("Data saved to spiral_coordinates_with_addresses_and_temperature.csv")
