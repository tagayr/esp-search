import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
from backend import sourcing  # import your backend logic
import pandas as pd

st.set_page_config(page_title="Espeeria Search", layout="wide")

# --- Sidebar filters ---
st.sidebar.header("Search Settings")

# Define the initial location and zoom level (e.g., Marseille)
initial_lat = 43.296482
initial_lon = 5.369780
zoom_start = 12

# Create the map using folium
m = folium.Map(location=[initial_lat, initial_lon], zoom_start=zoom_start)

# Add a draggable marker to the map
marker = folium.Marker([initial_lat, initial_lon], draggable=True)
marker.add_to(m)

# Use st_folium to render the folium map in Streamlit
output = st_folium(m, width=700)

# Get the current marker position
if output and 'last_clicked' in output:
    current_lat = output['last_clicked']['lat']
    current_lon = output['last_clicked']['lng']
else:
    current_lat = initial_lat
    current_lon = initial_lon

# Get the location name
location = sourcing.get_location_name(current_lat, current_lon)

# Display the current location
st.sidebar.write(f"Selected Location: {location}")

radius_km = st.sidebar.slider("Search Radius (km)", 1, 20, 5)

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

# --- Main section ---
st.title("🧭 Espeeria Supplier Finder")
st.markdown(
    "Use the sidebar to search for hotels, restaurants, activities and transport "
    "options around your selected destination."
)

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

