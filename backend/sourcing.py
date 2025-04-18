# backend/sourcing.py
# todo

def fetch_suppliers(location, radius_km, types, min_rating, max_price):
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

def test():
    return True
