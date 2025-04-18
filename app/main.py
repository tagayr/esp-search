import streamlit as st
from backend import sourcing  # import your backend logic (we'll stub this)
import pandas as pd

st.set_page_config(page_title="Espeeria Search", layout="wide")

# --- Sidebar filters ---
st.sidebar.header("Search Settings")

location = st.sidebar.text_input("Destination", "Marseille")
radius_km = st.sidebar.slider("Search Radius (km)", 1, 20, 5)

supplier_types = st.sidebar.multiselect(
    "Types to include",
    options=["Accommodation", "Food", "Experience", "Transport"],
    default=["Accommodation", "Food", "Experience"]
)

min_google_rating = st.sidebar.slider("Min Google Rating", 1.0, 5.0, 4.0)
max_price_per_person = st.sidebar.number_input("Max Price per Person (€)", value=100)

if st.sidebar.button("Search"):
    with st.spinner("Sourcing suppliers..."):
        # This is where your backend sourcing logic would be called
        suppliers = sourcing.fetch_suppliers(
            location=location,
            radius_km=radius_km,
            types=supplier_types,
            min_rating=min_google_rating,
            max_price=max_price_per_person
        )

        if suppliers:
            df = pd.DataFrame(suppliers)
            st.success(f"Found {len(df)} suppliers!")
            st.dataframe(df)
        else:
            st.warning("No results found for the given criteria.")

# --- Main section ---
st.title("🧭 Espeeria Supplier Finder")
st.markdown(
    "Use the sidebar to search for hotels, restaurants, activities and transport "
    "options around your selected destination. Results are based on live API data."
)

