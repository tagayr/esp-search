import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
from backend import sourcing  # import your backend logic
import pandas as pd
import os

st.set_page_config(page_title="Espeeria Search", layout="wide")

# --- Main section ---
st.title("🧭 Espeeria Supplier Finder")
st.markdown(
    "Use the sidebar to search for hotels, restaurants, activities and transport "
    "options around your selected destination."
)

# --- Sidebar filters ---
st.sidebar.header("Search Settings")

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

# Initialize session state for location if not already set
if 'current_lat' not in st.session_state:
    st.session_state.current_lat = initial_lat
    st.session_state.current_lon = initial_lon

# Get the search radius from the slider
radius_km = st.sidebar.slider("Search Radius (km)", 1, 20, 5)

# Create the map with current location
m = folium.Map(location=[st.session_state.current_lat, st.session_state.current_lon], zoom_start=zoom_start)

# Add the marker with custom icon
if custom_icon:
    marker = folium.Marker(
        [st.session_state.current_lat, st.session_state.current_lon],
        draggable=True,
        icon=custom_icon
    )
else:
    marker = folium.Marker(
        [st.session_state.current_lat, st.session_state.current_lon],
        draggable=True
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

# Render the map in the sidebar
with st.sidebar:
    st.write("Select your destination on the map:")
    output = st_folium(m, width=300, height=300)

# Update location if map was interacted with
if output is not None:
    # Check for marker drag (last_object_clicked)
    if 'last_object_clicked' in output and output['last_object_clicked'] is not None:
        st.session_state.current_lat = output['last_object_clicked']['lat']
        st.session_state.current_lon = output['last_object_clicked']['lng']
    # Check for map click (last_clicked)
    elif 'last_clicked' in output and output['last_clicked'] is not None:
        st.session_state.current_lat = output['last_clicked']['lat']
        st.session_state.current_lon = output['last_clicked']['lng']

# Get the location name
location = sourcing.get_location_name(st.session_state.current_lat, st.session_state.current_lon)

# Display the current location
st.sidebar.write(f"Selected Location: {location}")

supplier_types = st.sidebar.multiselect(
    "Types to include",
    options=["Accommodation", "Food", "Experience", "Transport"],
    default=["Accommodation", "Food"]
)

min_google_rating = st.sidebar.slider("Min Google Rating", 1.0, 5.0, 4.0)

# Create dynamic price inputs based on selected supplier types
st.sidebar.subheader("Max Price per Person by Type (€)")

# Dictionary to store max prices for each type
max_prices = {}

# Only show price inputs for selected supplier types
for supplier_type in supplier_types:
    max_prices[supplier_type] = st.sidebar.number_input(
        f"Max Price for {supplier_type} (€)",
        min_value=0,
        value=100 if supplier_type == "Accommodation" else 50,
        step=5
    )

# If no specific type is selected, use the general max price
if not supplier_types:
    st.sidebar.info("Select supplier types to set specific price limits")

# Create a container for search results
results_container = st.container()

# Search button in sidebar
if st.sidebar.button("Search"):
    with st.spinner("Sourcing suppliers..."):
        # This is where your backend sourcing logic would be called
        suppliers = sourcing.fetch_suppliers(
            location=location,
            radius_km=radius_km,
            types=supplier_types,
            min_rating=min_google_rating,
            max_price=max_prices
        )
        
        # Display results in the container below the title and description
        with results_container:
            if suppliers:
                df = pd.DataFrame(suppliers)
                st.success(f"Found {len(df)} suppliers!")
                st.dataframe(df)
            else:
                st.warning("No results found for the given criteria.")

