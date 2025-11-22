"""Mock hotel search and booking tools."""

from typing import Dict, List, Any
from langchain_core.tools import tool
import random


@tool
def search_hotels(
    city: str,
    check_in: str,
    check_out: str,
    guests: int = 2,
    rooms: int = 1,
    min_stars: int = 3,
    max_price_per_night: int = None
) -> List[Dict[str, Any]]:
    """
    Search for available hotels in a city.

    Args:
        city: City name (e.g., 'Istanbul', 'London')
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        guests: Number of guests (default: 2)
        rooms: Number of rooms (default: 1)
        min_stars: Minimum star rating 1-5 (default: 3)
        max_price_per_night: Maximum price per night in USD (optional)

    Returns:
        List of available hotels with details
    """

    # Mock hotel data
    hotel_names = [
        "Grand Palace Hotel",
        "Seaside Resort & Spa",
        "City Center Inn",
        "Historic Boutique Hotel",
        "Modern Plaza Hotel",
        "Luxury Towers",
        "Cozy Garden Hotel"
    ]

    neighborhoods = [
        "City Center",
        "Old Town",
        "Business District",
        "Waterfront",
        "Historic Quarter"
    ]

    amenities_pool = [
        "Free WiFi",
        "Swimming Pool",
        "Fitness Center",
        "Spa",
        "Restaurant",
        "Bar",
        "Room Service",
        "Airport Shuttle",
        "Parking",
        "Business Center",
        "Concierge",
        "Laundry Service"
    ]

    hotels = []
    for i in range(5):
        stars = random.randint(min_stars, 5)
        base_price = stars * 30 + random.randint(20, 100)

        # Skip if over max price
        if max_price_per_night and base_price > max_price_per_night:
            base_price = max_price_per_night - random.randint(10, 30)

        # Calculate total price (example: 3 nights)
        nights = 3
        total_price = base_price * nights * rooms

        # Select random amenities
        num_amenities = random.randint(6, len(amenities_pool))
        amenities = random.sample(amenities_pool, num_amenities)

        hotel = {
            "hotel_id": f"HTL{random.randint(1000, 9999)}",
            "name": random.choice(hotel_names),
            "stars": stars,
            "rating": round(random.uniform(7.5, 9.8), 1),
            "reviews_count": random.randint(100, 2000),
            "location": {
                "city": city,
                "neighborhood": random.choice(neighborhoods),
                "address": f"{random.randint(1, 999)} Main Street",
                "distance_to_center": f"{random.uniform(0.5, 5):.1f} km"
            },
            "room_type": "Standard Double Room" if guests <= 2 else "Family Suite",
            "price_per_night": base_price,
            "total_price": total_price,
            "currency": "USD",
            "amenities": amenities,
            "cancellation": "Free cancellation" if random.choice([True, False]) else "Non-refundable",
            "breakfast_included": random.choice([True, False]),
            "available_rooms": random.randint(1, 10)
        }

        hotels.append(hotel)

    # Sort by rating
    hotels.sort(key=lambda x: x["rating"], reverse=True)

    return hotels


@tool
def get_hotel_details(hotel_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific hotel.

    Args:
        hotel_id: The unique hotel identifier

    Returns:
        Detailed hotel information
    """

    return {
        "hotel_id": hotel_id,
        "name": "Grand Palace Hotel",
        "stars": 5,
        "rating": 9.2,
        "reviews": {
            "total": 1547,
            "categories": {
                "cleanliness": 9.5,
                "comfort": 9.3,
                "location": 9.0,
                "facilities": 9.1,
                "staff": 9.4,
                "value": 8.8
            },
            "recent_comments": [
                {
                    "guest": "John D.",
                    "date": "2024-11-15",
                    "rating": 10,
                    "comment": "Exceptional service and beautiful rooms!"
                },
                {
                    "guest": "Sarah M.",
                    "date": "2024-11-10",
                    "rating": 9,
                    "comment": "Great location, very clean and comfortable."
                }
            ]
        },
        "location": {
            "address": "123 Grand Avenue",
            "city": "Istanbul",
            "country": "Turkey",
            "coordinates": {"lat": 41.0082, "lng": 28.9784},
            "nearby_attractions": [
                {"name": "Hagia Sophia", "distance": "0.5 km"},
                {"name": "Blue Mosque", "distance": "0.7 km"},
                {"name": "Grand Bazaar", "distance": "1.2 km"}
            ],
            "transportation": {
                "airport": "35 km to Istanbul Airport",
                "metro": "200m to Sultanahmet Station"
            }
        },
        "rooms": [
            {
                "type": "Standard Double",
                "size": "25 sqm",
                "beds": "1 Queen Bed",
                "max_guests": 2,
                "price_per_night": 150
            },
            {
                "type": "Deluxe Suite",
                "size": "45 sqm",
                "beds": "1 King Bed",
                "max_guests": 3,
                "price_per_night": 250
            }
        ],
        "amenities": {
            "general": [
                "Free WiFi",
                "24-hour Front Desk",
                "Concierge Service",
                "Currency Exchange",
                "Luggage Storage"
            ],
            "activities": [
                "Swimming Pool",
                "Fitness Center",
                "Spa & Wellness Center",
                "Turkish Bath"
            ],
            "food_drink": [
                "Restaurant",
                "Bar",
                "Room Service",
                "Breakfast Buffet"
            ]
        },
        "policies": {
            "check_in": "14:00",
            "check_out": "12:00",
            "cancellation": "Free cancellation up to 24 hours before check-in",
            "pets": "Not allowed",
            "children": "Children of all ages welcome"
        }
    }
