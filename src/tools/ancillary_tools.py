"""Mock ancillary services tools (baggage, seats, insurance, etc.)."""

from typing import Dict, List, Any
from langchain_core.tools import tool
import random


@tool
def get_baggage_options(flight_id: str, passengers: int = 1) -> Dict[str, Any]:
    """
    Get available baggage options for a flight.

    Args:
        flight_id: The flight identifier
        passengers: Number of passengers

    Returns:
        Available baggage options and pricing
    """

    return {
        "flight_id": flight_id,
        "passengers": passengers,
        "included_baggage": {
            "cabin": {
                "quantity": 1,
                "weight": "8 kg",
                "dimensions": "55x40x20 cm"
            },
            "checked": {
                "quantity": 1,
                "weight": "23 kg",
                "note": "Included in ticket price"
            }
        },
        "additional_options": [
            {
                "id": "BAG001",
                "type": "extra_checked",
                "description": "Additional checked baggage (23kg)",
                "price_per_bag": 50,
                "total_price": 50 * passengers,
                "currency": "USD",
                "max_quantity": 3
            },
            {
                "id": "BAG002",
                "type": "heavy_bag",
                "description": "Heavy baggage (23-32kg)",
                "price_per_bag": 75,
                "total_price": 75 * passengers,
                "currency": "USD",
                "max_quantity": 2
            },
            {
                "id": "BAG003",
                "type": "sports_equipment",
                "description": "Sports equipment (ski, golf, bicycle)",
                "price_per_item": 100,
                "total_price": 100 * passengers,
                "currency": "USD",
                "note": "Subject to availability and size restrictions"
            },
            {
                "id": "BAG004",
                "type": "pet_cabin",
                "description": "Pet in cabin (max 8kg including carrier)",
                "price_per_pet": 150,
                "total_price": 150,
                "currency": "USD",
                "restrictions": "Small dogs and cats only, subject to approval"
            }
        ],
        "policies": {
            "oversized_fee": "$200 per bag over 32kg",
            "last_minute_fee": "Add 50% if purchased at airport",
            "refund_policy": "Non-refundable once purchased"
        }
    }


@tool
def get_seat_options(flight_id: str, cabin_class: str = "economy") -> Dict[str, Any]:
    """
    Get available seat selection options for a flight.

    Args:
        flight_id: The flight identifier
        cabin_class: Cabin class - 'economy', 'business', 'first'

    Returns:
        Available seat options and pricing
    """

    # Generate seat map
    if cabin_class == "economy":
        total_seats = 264
        rows = 44
        config = "3-3-3"
    elif cabin_class == "business":
        total_seats = 30
        rows = 5
        config = "2-2-2"
    else:  # first
        total_seats = 12
        rows = 2
        config = "1-2-1"

    # Random seat availability
    available_seats = random.sample(
        [f"{random.randint(1, rows)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J'])}"
         for _ in range(total_seats)],
        random.randint(50, 150)
    )

    seat_types = []

    if cabin_class == "economy":
        seat_types = [
            {
                "id": "SEAT001",
                "type": "standard",
                "description": "Standard seat",
                "price": 0,
                "currency": "USD",
                "features": ["Standard legroom"],
                "available_count": len([s for s in available_seats if int(s[:-1]) > 10])
            },
            {
                "id": "SEAT002",
                "type": "extra_legroom",
                "description": "Extra legroom seat",
                "price": 35,
                "currency": "USD",
                "features": ["Extra 7cm legroom", "Priority boarding"],
                "available_count": 24,
                "rows": ["12", "13", "27", "28"]
            },
            {
                "id": "SEAT003",
                "type": "exit_row",
                "description": "Exit row seat",
                "price": 50,
                "currency": "USD",
                "features": ["Extra legroom", "Quick exit access"],
                "restrictions": "Must be 18+ and able-bodied",
                "available_count": 12
            },
            {
                "id": "SEAT004",
                "type": "preferred",
                "description": "Preferred seat (front rows)",
                "price": 20,
                "currency": "USD",
                "features": ["Quick boarding/deboarding", "Near front galley"],
                "rows": ["5", "6", "7", "8", "9"]
            }
        ]
    else:
        seat_types = [
            {
                "id": "SEAT101",
                "type": "standard_business",
                "description": "Standard business seat",
                "price": 0,
                "currency": "USD",
                "features": ["Lie-flat bed", "Direct aisle access", "Premium dining"],
                "note": "Included in business class ticket"
            }
        ]

    return {
        "flight_id": flight_id,
        "cabin_class": cabin_class,
        "aircraft_config": config,
        "total_seats": total_seats,
        "seat_types": seat_types,
        "seat_map_url": f"https://seatmap.example.com/{flight_id}",
        "recommendations": [
            "Seats 12A, 12F - Extra legroom, window seats",
            "Seats 7D, 7E - Front section, easy access"
        ]
    }


@tool
def get_insurance_options(
    trip_type: str,
    total_trip_cost: float,
    passengers: int = 1,
    destination_country: str = "US"
) -> List[Dict[str, Any]]:
    """
    Get available travel insurance options.

    Args:
        trip_type: Type of trip - 'domestic', 'international', 'multi_country'
        total_trip_cost: Total cost of the trip in USD
        passengers: Number of passengers
        destination_country: Destination country code

    Returns:
        Available insurance plans
    """

    # Calculate base premium (percentage of trip cost)
    base_premium_pct = {
        "domestic": 0.04,
        "international": 0.06,
        "multi_country": 0.08
    }

    base_premium = total_trip_cost * base_premium_pct.get(trip_type, 0.05)

    insurance_plans = [
        {
            "id": "INS001",
            "name": "Basic Protection",
            "type": "basic",
            "price_per_person": round(base_premium * 0.7, 2),
            "total_price": round(base_premium * 0.7 * passengers, 2),
            "currency": "USD",
            "coverage": {
                "trip_cancellation": {
                    "covered": True,
                    "max_amount": total_trip_cost,
                    "conditions": "Covered reasons only"
                },
                "medical_emergency": {
                    "covered": True,
                    "max_amount": 50000
                },
                "baggage_loss": {
                    "covered": True,
                    "max_amount": 1000
                },
                "trip_delay": {
                    "covered": True,
                    "max_amount": 500,
                    "min_delay_hours": 6
                },
                "covid_coverage": False,
                "adventure_sports": False
            },
            "deductible": 100
        },
        {
            "id": "INS002",
            "name": "Standard Protection",
            "type": "standard",
            "price_per_person": round(base_premium, 2),
            "total_price": round(base_premium * passengers, 2),
            "currency": "USD",
            "recommended": True,
            "coverage": {
                "trip_cancellation": {
                    "covered": True,
                    "max_amount": total_trip_cost,
                    "conditions": "Cancel for any reason available"
                },
                "medical_emergency": {
                    "covered": True,
                    "max_amount": 100000
                },
                "emergency_evacuation": {
                    "covered": True,
                    "max_amount": 250000
                },
                "baggage_loss": {
                    "covered": True,
                    "max_amount": 2500
                },
                "trip_delay": {
                    "covered": True,
                    "max_amount": 1000,
                    "min_delay_hours": 3
                },
                "missed_connection": {
                    "covered": True,
                    "max_amount": 500
                },
                "covid_coverage": True,
                "adventure_sports": False
            },
            "deductible": 50
        },
        {
            "id": "INS003",
            "name": "Premium Protection",
            "type": "premium",
            "price_per_person": round(base_premium * 1.5, 2),
            "total_price": round(base_premium * 1.5 * passengers, 2),
            "currency": "USD",
            "coverage": {
                "trip_cancellation": {
                    "covered": True,
                    "max_amount": total_trip_cost * 1.5,
                    "conditions": "Cancel for any reason - 75% refund"
                },
                "medical_emergency": {
                    "covered": True,
                    "max_amount": 500000
                },
                "emergency_evacuation": {
                    "covered": True,
                    "max_amount": 1000000
                },
                "baggage_loss": {
                    "covered": True,
                    "max_amount": 5000
                },
                "trip_delay": {
                    "covered": True,
                    "max_amount": 2000,
                    "min_delay_hours": 2
                },
                "missed_connection": {
                    "covered": True,
                    "max_amount": 1000
                },
                "rental_car_damage": {
                    "covered": True,
                    "max_amount": 50000
                },
                "covid_coverage": True,
                "adventure_sports": True,
                "pre_existing_conditions": True
            },
            "deductible": 0,
            "benefits": [
                "24/7 multilingual assistance",
                "Concierge services",
                "Identity theft protection",
                "Pet care coverage if hospitalized"
            ]
        }
    ]

    return insurance_plans


@tool
def get_car_rental_options(
    location: str,
    pickup_date: str,
    return_date: str,
    driver_age: int = 30
) -> List[Dict[str, Any]]:
    """
    Get available car rental options.

    Args:
        location: Pickup location (city or airport code)
        pickup_date: Pickup date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format
        driver_age: Driver's age (affects pricing and availability)

    Returns:
        Available car rental options
    """

    car_types = [
        {
            "id": "CAR001",
            "category": "economy",
            "name": "Economy Car",
            "example_models": ["Toyota Yaris", "Ford Fiesta", "VW Polo"],
            "passengers": 5,
            "luggage": 2,
            "transmission": "Manual",
            "fuel_type": "Gasoline",
            "price_per_day": 35,
            "total_price": 105,  # 3 days
            "currency": "USD",
            "features": ["Air Conditioning", "Radio"],
            "mileage": "Unlimited"
        },
        {
            "id": "CAR002",
            "category": "compact",
            "name": "Compact Car",
            "example_models": ["Toyota Corolla", "VW Golf", "Honda Civic"],
            "passengers": 5,
            "luggage": 3,
            "transmission": "Automatic",
            "fuel_type": "Gasoline",
            "price_per_day": 45,
            "total_price": 135,
            "currency": "USD",
            "features": ["Air Conditioning", "Bluetooth", "USB Charging"],
            "mileage": "Unlimited"
        },
        {
            "id": "CAR003",
            "category": "suv",
            "name": "SUV",
            "example_models": ["Toyota RAV4", "Honda CR-V", "Ford Escape"],
            "passengers": 7,
            "luggage": 4,
            "transmission": "Automatic",
            "fuel_type": "Gasoline",
            "price_per_day": 75,
            "total_price": 225,
            "currency": "USD",
            "features": ["Air Conditioning", "Navigation", "4WD", "Bluetooth"],
            "mileage": "Unlimited"
        },
        {
            "id": "CAR004",
            "category": "luxury",
            "name": "Luxury Sedan",
            "example_models": ["Mercedes E-Class", "BMW 5 Series", "Audi A6"],
            "passengers": 5,
            "luggage": 3,
            "transmission": "Automatic",
            "fuel_type": "Gasoline",
            "price_per_day": 120,
            "total_price": 360,
            "currency": "USD",
            "features": [
                "Premium Audio",
                "Navigation",
                "Leather Seats",
                "Sunroof",
                "Advanced Safety Features"
            ],
            "mileage": "Unlimited"
        }
    ]

    # Add young driver fee if under 25
    if driver_age < 25:
        for car in car_types:
            car["young_driver_fee"] = 25
            car["total_price"] += 25

    # Add insurance options
    for car in car_types:
        car["insurance_options"] = [
            {
                "type": "basic",
                "name": "Basic Coverage",
                "price_per_day": 15,
                "included": True
            },
            {
                "type": "full",
                "name": "Full Coverage",
                "price_per_day": 30,
                "coverage": "Zero deductible, theft protection, tire/glass coverage"
            }
        ]

    return car_types
