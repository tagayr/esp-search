# backend/sourcing.py
# todo

import os
import requests
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

def get_location_name(lat, lon):
    """
    Get the location name from coordinates using OpenStreetMap's Nominatim service.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        str: Location name or coordinates if name not found
    """
    try:
        # Using Nominatim (OpenStreetMap) for reverse geocoding
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        headers = {'User-Agent': 'Espeeria Search App'}
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Extract city name
        address = data.get('address', {})
        city = address.get('city') or address.get('town') or address.get('village')
        if not city:
            # If no city found, use the display name
            city = data.get('display_name', '').split(',')[0]
        
        return city
    except Exception as e:
        print(f"Error getting location name: {str(e)}")
        return f"{lat:.4f}, {lon:.4f}"

def get_coordinates_nominatim(location):
    """
    Get coordinates from a location name using OpenStreetMap's Nominatim service.
    
    Args:
        location (str): Location name
        
    Returns:
        tuple: (latitude, longitude) or None if not found
    """
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
        headers = {'User-Agent': 'Espeeria Search App'}
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        return None
    except Exception as e:
        print(f"Error getting coordinates: {str(e)}")
        return None

def get_coordinates():
    """
    Get coordinates from the user's map selection using session state.
    
    Returns:
        tuple: (latitude, longitude)
    """
    if 'current_lat' in st.session_state and 'current_lon' in st.session_state:
        return st.session_state.current_lat, st.session_state.current_lon
    return None

def fetch_suppliers_dummy(location, radius_km, types, min_rating, max_price):
    """
    This is a stub function. In the future, it will use real APIs to source data.
    For now, returns sample data.
    """
    # Simulate results
    return [
        {
            "Name": "Hotel Bleu",
            "Type": "Accommodation",
            "Price (€)": 90,
            "Rating": 4.5,
            "Location": "Marseille",
            "Website": "http://hotelbleu.example.com"
        },
        {
            "Name": "Le Petit Bistro",
            "Type": "Food",
            "Price (€)": 35,
            "Rating": 4.2,
            "Location": "Marseille",
            "Website": "http://lepetitbistro.example.com"
        }
    ]

# There are a few approaches to source real supplier data:

# 1. Google Maps API (Recommended for production)
# - Use the Places API to search for businesses by type and location
# - Pros: Official, reliable, structured data
# - Cons: Requires API key and has usage costs
# Example implementation:

# def fetch_suppliers(location, radius_km, types, min_rating, max_price):
def fetch_suppliers(lat, lon, radius_km, types, min_rating, max_price):
    """
    Fetches suppliers using Google Maps Places API.
    Requires a Google Cloud Platform account and API key.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        raise ValueError("Google Maps API key not found in environment variables")
    
    # Map our supplier types to Google Places types
    type_mapping = {
        "Accommodation": ["lodging", "hotel"],
        "Food": ["restaurant", "cafe", "bar"],
        "Experience": ["tourist_attraction", "museum", "amusement_park", "art_gallery","spa"],
        "Transport": ["car_rental", "taxi_stand"]
    }
    
    results = []
    
    for supplier_type in types:
        if supplier_type not in type_mapping:
            continue
            
        for place_type in type_mapping[supplier_type]:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lon}",
                "radius": radius_km * 1000,  # Convert to meters
                "type": place_type,
                "minprice": 0,
                "maxprice": 4,  # Google uses 0-4 price levels
                "key": api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data["status"] == "OK":
                for place in data["results"]:
                    if place["rating"] >= min_rating:
                        # You would need to get price data separately
                        # as Google doesn't provide exact prices
                        price_level = place.get("price_level", 2)
                        estimated_price = price_level * 25  # Rough estimate
                        
                        if estimated_price <= max_price.get(supplier_type, 100):
                            # Get location coordinates from place geometry
                            location = place.get("geometry", {}).get("location", {})
                            latitude = location.get("lat")
                            longitude = location.get("lng")
                            
                            # Get city name using coordinates
                            city = get_location_name(latitude, longitude)
                            
                            results.append({
                                "Name": place["name"],
                                "Type": supplier_type,
                                "Price (€)": estimated_price,
                                "Rating": place["rating"],
                                "Address": place.get("vicinity", ""),
                                "Website": place.get("website", ""),
                                "City": city,
                                "Place ID": place["place_id"]
                            })
    
    # Remove duplicates based on Place ID
    seen_ids = set()
    unique_results = []
    for result in results:
        if result["Place ID"] not in seen_ids:
            seen_ids.add(result["Place ID"])
            unique_results.append(result)
    
    return unique_results

# 2. Web Scraping (Alternative approach)
# - Scrape data from Google Maps, TripAdvisor, etc.
# - Pros: No API costs
# - Cons: Less reliable, may violate terms of service

# 3. LLM with MCP (Modern alternative)
# - Use an LLM with Multi-modal Context Processing to extract data from websites
# - Pros: Flexible, can handle multiple sources
# - Cons: May be less accurate, higher compute costs

# def fetch_suppliers_with_llm(location, radius_km, types, min_rating, max_price):
#     """
#     Uses an LLM to extract supplier information from web searches.
#     Requires an LLM API like OpenAI's.
#     """
#     import openai
#     import os
#     
#     # You would need to set this environment variable
#     openai.api_key = os.environ.get("OPENAI_API_KEY")
#     
#     results = []
#     
#     for supplier_type in types:
#         # Create a prompt for the LLM
#         prompt = f"""
#         Find the top 5 {supplier_type.lower()} options in {location} with a rating of at least {min_rating}/5 
#         and a price under {max_price.get(supplier_type, 100)} euros per person.
#         
#         For each option, provide:
#         - Name
#         - Exact price in euros
#         - Rating
#         - Website URL
#         
#         Format the results as a JSON array.
#         """
#         
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.2
#         )
#         
#         # Parse the response (would need error handling)
#         import json
#         try:
#             llm_results = json.loads(response.choices[0].message.content)
#             for item in llm_results:
#                 results.append({
#                     "Name": item["Name"],
#                     "Type": supplier_type,
#                     "Price (€)": item["Exact price in euros"],
#                     "Rating": item["Rating"],
#                     "Location": location,
#                     "Website": item["Website URL"]
#                 })
#         except:
#             # Handle parsing errors
#             pass
#     
#     return results

# Recommendation:
# For a production app, use the Google Maps API approach
# For a prototype or if budget is a concern, the LLM approach could work
# Just be aware of the limitations and potential inaccuracies
