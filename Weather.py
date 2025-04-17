import logging
import requests

def get_current_weather(location: str, unit: str = "celsius") -> str:
    """
    Fetches the current weather for a given location.

    Args:
    location (str): The city and country, e.g., "San Francisco, USA"
    unit (str): Temperature unit, either "celsius" or "fahrenheit"
    """
    logging.info(f"Getting weather for {location}")
    base_url = "https://api.open-meteo.com/v1/forecast"

    # Set up parameters for the weather API
    if unit == '':
        unit = "celsius"
    params = {
        "latitude": 0,
        "longitude": 0,
        "current_weather": "true",
        "temperature_unit": unit
    }

    # Set up geocoding to convert location name to coordinates
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    location_parts = location.split(',')
    city = location_parts[0].strip()
    country = location_parts[1].strip() if len(location_parts) > 1 else ""

    geo_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    try:
        # First attempt to get coordinates
        logging.info(f"Fetching coordinates for {location}")
        geo_response = requests.get(geocoding_url, params=geo_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        logging.debug(f"Geocoding response: {geo_data}")

        # If first attempt fails, try with full location string
        if "results" not in geo_data or not geo_data["results"]:
            geo_params["name"] = location
            geo_response = requests.get(geocoding_url, params=geo_params)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            logging.debug(f"Second geocoding attempt response: {geo_data}")

        # Extract coordinates if found
        if "results" in geo_data and geo_data["results"]:
            params["latitude"] = geo_data["results"][0]["latitude"]
            params["longitude"] = geo_data["results"][0]["longitude"]
            logging.info(
                f"Coordinates found: {params['latitude']}, {params['longitude']}")
        else:
            logging.warning(f"No results found for location: {location}")
            return f"Sorry, I couldn't find the location: {location}"

        # Fetch weather data using coordinates
        logging.info("Fetching weather data")
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        logging.debug(f"Weather data response: {weather_data}")

        # Extract and format weather information
        if "current_weather" in weather_data:
            current_weather = weather_data["current_weather"]
            temp = current_weather["temperature"]
            wind_speed = current_weather["windspeed"]
            if (unit.upper() == "FAHRENHEIT"):
                unit = "F"
            else:
                unit = "C"
        
            result = f"The current weather in {location} is {temp}°{unit} with a wind speed of {wind_speed} km/h."
            logging.info(f"Weather result: {result}")
            return result
        else:
            logging.warning(f"No current weather data found for {location}")
            return f"Sorry, I couldn't retrieve weather data for {location}"
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred while fetching weather data: {str(e)}")
        return f"An error occurred while fetching weather data: {str(e)}"