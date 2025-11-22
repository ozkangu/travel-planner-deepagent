"""Mock activity and attraction search tools."""

from typing import Dict, List, Any
from langchain_core.tools import tool
import random


@tool
def search_activities(
    city: str,
    category: str = "all",
    date: str = None,
    max_price: float = None,
    duration_hours: int = None
) -> List[Dict[str, Any]]:
    """
    Search for activities and attractions in a city.

    Args:
        city: City name (e.g., 'Istanbul', 'Paris')
        category: Activity category - 'all', 'tours', 'museums', 'food', 'adventure', 'culture', 'entertainment'
        date: Preferred date in YYYY-MM-DD format (optional)
        max_price: Maximum price in USD (optional)
        duration_hours: Preferred duration in hours (optional)

    Returns:
        List of available activities
    """

    # Mock activity database
    activities_db = {
        "istanbul": [
            {
                "name": "Bosphorus Sunset Cruise",
                "category": "tours",
                "description": "Enjoy a scenic cruise along the Bosphorus with stunning views of Istanbul's skyline",
                "duration_hours": 2,
                "price": 45,
                "rating": 4.8,
                "reviews": 2341,
                "highlights": [
                    "See iconic landmarks from the water",
                    "Professional guide",
                    "Complimentary drinks",
                    "Sunset viewing"
                ]
            },
            {
                "name": "Hagia Sophia Guided Tour",
                "category": "culture",
                "description": "Explore the magnificent Hagia Sophia with an expert guide",
                "duration_hours": 1.5,
                "price": 35,
                "rating": 4.9,
                "reviews": 5432,
                "highlights": [
                    "Skip-the-line access",
                    "Expert historian guide",
                    "Small group tour"
                ]
            },
            {
                "name": "Turkish Cooking Class",
                "category": "food",
                "description": "Learn to cook traditional Turkish dishes with a local chef",
                "duration_hours": 4,
                "price": 85,
                "rating": 4.7,
                "reviews": 876,
                "highlights": [
                    "Hands-on cooking experience",
                    "Market tour included",
                    "Enjoy your creations",
                    "Recipe booklet"
                ]
            },
            {
                "name": "Grand Bazaar Walking Tour",
                "category": "culture",
                "description": "Navigate the world's oldest covered market with a local guide",
                "duration_hours": 2,
                "price": 25,
                "rating": 4.6,
                "reviews": 1543,
                "highlights": [
                    "Discover hidden gems",
                    "Shopping tips",
                    "Historical insights"
                ]
            },
            {
                "name": "Whirling Dervishes Show",
                "category": "entertainment",
                "description": "Experience the mesmerizing Sufi whirling ceremony",
                "duration_hours": 1,
                "price": 40,
                "rating": 4.8,
                "reviews": 2109,
                "highlights": [
                    "Traditional ceremony",
                    "Historic venue",
                    "Cultural experience"
                ]
            }
        ],
        "paris": [
            {
                "name": "Eiffel Tower Skip-the-Line",
                "category": "tours",
                "description": "Skip the queues and access the Eiffel Tower with a guide",
                "duration_hours": 2,
                "price": 65,
                "rating": 4.7,
                "reviews": 8765,
                "highlights": [
                    "Priority access",
                    "Summit access",
                    "Guide included"
                ]
            },
            {
                "name": "Louvre Museum Tour",
                "category": "museums",
                "description": "Explore the world's largest art museum",
                "duration_hours": 3,
                "price": 75,
                "rating": 4.9,
                "reviews": 6543,
                "highlights": [
                    "See Mona Lisa",
                    "Expert art historian",
                    "Skip-the-line access"
                ]
            },
            {
                "name": "Seine River Dinner Cruise",
                "category": "food",
                "description": "Romantic dinner cruise with panoramic views",
                "duration_hours": 2.5,
                "price": 95,
                "rating": 4.6,
                "reviews": 3421,
                "highlights": [
                    "3-course meal",
                    "Live music",
                    "See illuminated monuments"
                ]
            }
        ]
    }

    # Get activities for the city (default to generic if city not in database)
    city_lower = city.lower()
    activities = activities_db.get(city_lower, [
        {
            "name": f"City Walking Tour - {city}",
            "category": "tours",
            "description": f"Explore the highlights of {city} with a local guide",
            "duration_hours": 3,
            "price": 40,
            "rating": 4.5,
            "reviews": 234
        },
        {
            "name": f"Food Tasting Tour - {city}",
            "category": "food",
            "description": f"Sample the best local cuisine in {city}",
            "duration_hours": 3,
            "price": 70,
            "rating": 4.7,
            "reviews": 567
        },
        {
            "name": f"Museum Pass - {city}",
            "category": "museums",
            "description": f"Access to major museums in {city}",
            "duration_hours": 8,
            "price": 50,
            "rating": 4.4,
            "reviews": 890
        }
    ])

    # Filter by category
    if category != "all":
        activities = [a for a in activities if a["category"] == category]

    # Filter by price
    if max_price:
        activities = [a for a in activities if a["price"] <= max_price]

    # Filter by duration
    if duration_hours:
        activities = [a for a in activities if abs(a["duration_hours"] - duration_hours) <= 1]

    # Add additional metadata
    result = []
    for activity in activities:
        result.append({
            "activity_id": f"ACT{random.randint(1000, 9999)}",
            **activity,
            "currency": "USD",
            "availability": random.choice([
                "Available daily",
                "Available Mon-Fri",
                "Available weekends",
                "Limited availability"
            ]),
            "cancellation_policy": random.choice([
                "Free cancellation up to 24 hours",
                "Free cancellation up to 48 hours",
                "Non-refundable"
            ]),
            "languages": random.sample(["English", "Spanish", "French", "German", "Turkish", "Arabic"], k=random.randint(2, 4)),
            "group_size": f"Max {random.randint(8, 20)} people" if "private" not in activity["name"].lower() else "Private tour",
            "instant_confirmation": random.choice([True, True, False])
        })

    return result


@tool
def get_activity_details(activity_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific activity.

    Args:
        activity_id: The activity identifier

    Returns:
        Detailed activity information
    """

    return {
        "activity_id": activity_id,
        "name": "Bosphorus Sunset Cruise",
        "category": "tours",
        "rating": 4.8,
        "reviews_count": 2341,
        "description": """
        Experience Istanbul from a unique perspective on this scenic Bosphorus cruise.
        As the sun sets over the city, you'll glide past magnificent palaces, historic
        fortresses, and modern bridges that span two continents. This 2-hour journey
        includes a professional guide who will share fascinating stories about the
        landmarks you'll see.
        """,
        "highlights": [
            "See iconic landmarks including Dolmabahçe Palace and Maiden's Tower",
            "Cross between Europe and Asia",
            "Professional English-speaking guide",
            "Complimentary drinks (tea, coffee, soft drinks)",
            "Perfect photo opportunities during sunset",
            "Learn about Istanbul's rich maritime history"
        ],
        "included": [
            "2-hour cruise",
            "Professional guide",
            "Complimentary beverages",
            "Hotel pickup (selected hotels only)"
        ],
        "not_included": [
            "Food and meals",
            "Alcoholic beverages",
            "Gratuities"
        ],
        "meeting_point": {
            "name": "Eminönü Pier",
            "address": "Eminönü Meydanı, Fatih, Istanbul",
            "coordinates": {"lat": 41.0166, "lng": 28.9714},
            "instructions": "Meet at the main ticket booth 15 minutes before departure"
        },
        "schedule": {
            "duration_hours": 2,
            "start_times": ["17:00", "18:30"],
            "days_available": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "seasonal_note": "Times vary by season to catch the best sunset"
        },
        "pricing": {
            "adult": 45,
            "child": 25,
            "infant": 0,
            "currency": "USD",
            "group_discount": "10% off for groups of 6+"
        },
        "accessibility": {
            "wheelchair_accessible": True,
            "suitable_for_elderly": True,
            "fitness_level": "Easy - minimal walking"
        },
        "cancellation_policy": {
            "free_cancellation_hours": 24,
            "refund_percentage": 100,
            "note": "Cancel up to 24 hours before for a full refund"
        },
        "requirements": [
            "Valid ID required",
            "Arrive 15 minutes before departure",
            "Dress warmly in winter months"
        ],
        "reviews_summary": {
            "excellent": 78,
            "very_good": 15,
            "average": 5,
            "poor": 1,
            "terrible": 1,
            "recent_reviews": [
                {
                    "reviewer": "Sarah M.",
                    "date": "2024-11-15",
                    "rating": 5,
                    "comment": "Absolutely magical experience! The sunset was breathtaking and our guide was very knowledgeable."
                },
                {
                    "reviewer": "John D.",
                    "date": "2024-11-10",
                    "rating": 5,
                    "comment": "Highlight of our Istanbul trip. Highly recommend!"
                }
            ]
        },
        "photos": [
            "https://example.com/cruise1.jpg",
            "https://example.com/cruise2.jpg",
            "https://example.com/cruise3.jpg"
        ]
    }


@tool
def get_restaurant_recommendations(
    city: str,
    cuisine_type: str = "all",
    price_range: str = "moderate",
    meal_type: str = "dinner"
) -> List[Dict[str, Any]]:
    """
    Get restaurant recommendations in a city.

    Args:
        city: City name
        cuisine_type: Type of cuisine - 'all', 'local', 'italian', 'asian', 'mediterranean', etc.
        price_range: Price range - 'budget', 'moderate', 'fine_dining'
        meal_type: Meal type - 'breakfast', 'lunch', 'dinner'

    Returns:
        List of recommended restaurants
    """

    price_symbols = {
        "budget": "$",
        "moderate": "$$",
        "fine_dining": "$$$"
    }

    price_ranges = {
        "budget": "10-25",
        "moderate": "25-60",
        "fine_dining": "60-150"
    }

    restaurants = [
        {
            "restaurant_id": f"REST{random.randint(1000, 9999)}",
            "name": "The Golden Fork",
            "cuisine": cuisine_type if cuisine_type != "all" else "Mediterranean",
            "rating": round(random.uniform(4.0, 4.9), 1),
            "reviews": random.randint(200, 2000),
            "price_level": price_symbols[price_range],
            "average_cost_per_person": f"${price_ranges[price_range]}",
            "address": f"{random.randint(1, 999)} Main Street, {city}",
            "phone": f"+1-555-{random.randint(1000, 9999)}",
            "hours": {
                meal_type: "11:00-23:00" if meal_type != "breakfast" else "07:00-11:00"
            },
            "specialties": [
                "Grilled sea bass",
                "Traditional mezze platter",
                "Homemade pasta"
            ],
            "features": random.sample([
                "Outdoor seating",
                "Waterfront view",
                "Live music",
                "Private dining room",
                "Wine cellar",
                "Vegetarian options",
                "Kids menu"
            ], k=random.randint(3, 5)),
            "reservation_required": price_range == "fine_dining",
            "dress_code": "Smart casual" if price_range == "fine_dining" else "Casual"
        }
        for _ in range(5)
    ]

    return restaurants
