import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
from backend import sourcing  # import your backend logic
import pandas as pd

import base64
import os

def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Path to the local image
image_path = os.path.join("app", "static", "background.jpg")
img_base64 = get_base64(image_path)

st.set_page_config(page_title="Espeeria Search", layout="wide")

# Inject it as background
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Main section ---
st.title("🧭 Espeeria Supplier Finder")
st.markdown(
    "Use the sidebar to search for hotels, restaurants, activities and transport "
    "options around your selected destination."
)

# Define the initial location and zoom level (e.g., Marseille)
initial_lat = 43.296482
initial_lon = 5.369780
zoom_start = 12

# Create custom icon
icon_path = os.path.join('app', 'static', 'marker.png')
if os.path.exists(icon_path):
    custom_icon = folium.CustomIcon(
        icon_image=icon_path,
        icon_size=(30, 30),  # Adjust size as needed
        icon_anchor=(15, 15)  # Center the icon on the point
    )
else:
    custom_icon = None

# Initialize session state for location and zoom if not already set
if 'current_lat' not in st.session_state:
    st.session_state.current_lat = initial_lat
    st.session_state.current_lon = initial_lon
    st.session_state.zoom_level = zoom_start

# --- Sidebar filters ---
with st.sidebar:
    st.header("Search Settings")

    # Get the search radius from the slider
    radius_km = st.slider("Search Radius (km)", 1, 20, 5)

    # Create the map with current location and zoom level
    m = folium.Map(
        location=[st.session_state.current_lat, st.session_state.current_lon],
        zoom_start=st.session_state.zoom_level
    )

    # Add the marker with custom icon at the current location
    if custom_icon:
        marker = folium.Marker(
            [st.session_state.current_lat, st.session_state.current_lon],
            draggable=True,  # Marker is draggable
            icon=custom_icon
        )
    else:
        marker = folium.Marker(
            [st.session_state.current_lat, st.session_state.current_lon],
            draggable=True  # Marker is draggable
        )
    marker.add_to(m)

    # Add a circle to represent the search radius
    radius_meters = radius_km * 1000
    folium.Circle(
        location=[st.session_state.current_lat, st.session_state.current_lon],
        radius=radius_meters,
        color='#3186cc',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.2,
        popup=f'Search radius: {radius_km} km'
    ).add_to(m)

    # Render the map
    st.write("Select your destination on the map:")
    output = st_folium(
        m,
        width=300,
        height=300,
        returned_objects=["last_object_clicked", "last_clicked"],
        key="map"
    )

    # Update location if map was clicked or marker was dragged
    if output is not None:
        if 'last_object_clicked' in output and output['last_object_clicked'] is not None:
            # Marker was dragged
            st.session_state.current_lat = output['last_object_clicked']['lat']
            st.session_state.current_lon = output['last_object_clicked']['lng']
        elif 'last_clicked' in output and output['last_clicked'] is not None:
            # Map was clicked
            st.session_state.current_lat = output['last_clicked']['lat']
            st.session_state.current_lon = output['last_clicked']['lng']
        
        # Update zoom level if it changed
        if 'zoom' in output:
            st.session_state.zoom_level = output['zoom']

    # Get the location name
    location = sourcing.get_location_name(st.session_state.current_lat, st.session_state.current_lon)

    # Display the current location
    st.write(f"Selected Location: {location}")

    supplier_types = st.multiselect(
        "Types to include",
        options=["Accommodation", "Food", "Experience", "Transport"],
        default=["Accommodation", "Food"]
    )

    min_google_rating = st.slider("Min Google Rating", 1.0, 5.0, 4.0)

    # Create dynamic price inputs based on selected supplier types
    st.subheader("Max Price per Person by Type (€)")

    # Dictionary to store max prices for each type
    max_prices = {}

    # Only show price inputs for selected supplier types
    for supplier_type in supplier_types:
        max_prices[supplier_type] = st.number_input(
            f"Max Price for {supplier_type} (€)",
            min_value=0,
            value=100 if supplier_type == "Accommodation" else 50,
            step=5
        )

    # If no specific type is selected, use the general max price
    if not supplier_types:
        st.info("Select supplier types to set specific price limits")

    # Search button
    if st.button("Search"):
        with st.spinner("Sourcing suppliers..."):
            # Get current coordinates from session state
            coords = sourcing.get_coordinates()
            if coords:
                lat, lon = coords
                # This is where your backend sourcing logic would be called
                suppliers = sourcing.fetch_suppliers(
                    lat=lat,
                    lon=lon,
                    radius_km=radius_km,
                    types=supplier_types,
                    min_rating=min_google_rating,
                    max_price=max_prices
                )
                
                # Display results in the container below the title and description
                if suppliers:
                    df = pd.DataFrame(suppliers)
                    st.success(f"Found {len(df)} suppliers!")
                    st.dataframe(df)
                else:
                    st.warning("No results found for the given criteria.")
            else:
                st.error("No location selected. Please select a location on the map.")

