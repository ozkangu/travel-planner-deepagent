"""Mock weather forecast tools."""

from typing import Dict, List, Any
from langchain_core.tools import tool
from datetime import datetime, timedelta
import random


@tool
def get_weather_forecast(
    city: str,
    date: str = None,
    days: int = 7
) -> Dict[str, Any]:
    """
    Get weather forecast for a city.

    Args:
        city: City name (e.g., 'Istanbul', 'London')
        date: Start date in YYYY-MM-DD format (default: today)
        days: Number of days to forecast (1-14, default: 7)

    Returns:
        Weather forecast information
    """

    # Parse date or use today
    if date:
        start_date = datetime.strptime(date, "%Y-%m-%d")
    else:
        start_date = datetime.now()

    # Mock weather conditions
    conditions = [
        "Clear sky",
        "Partly cloudy",
        "Cloudy",
        "Light rain",
        "Rain",
        "Thunderstorm",
        "Sunny"
    ]

    # Generate forecast for each day
    forecast = []
    for i in range(min(days, 14)):
        current_date = start_date + timedelta(days=i)

        # Random but realistic temperature
        base_temp = random.randint(10, 25)
        high = base_temp + random.randint(3, 8)
        low = base_temp - random.randint(2, 5)

        condition = random.choice(conditions)
        is_rainy = "rain" in condition.lower() or "storm" in condition.lower()

        day_forecast = {
            "date": current_date.strftime("%Y-%m-%d"),
            "day_name": current_date.strftime("%A"),
            "condition": condition,
            "temperature": {
                "high": high,
                "low": low,
                "unit": "celsius"
            },
            "feels_like": {
                "high": high - random.randint(0, 3),
                "low": low - random.randint(0, 3)
            },
            "humidity": random.randint(40, 85),
            "wind": {
                "speed": random.randint(5, 30),
                "direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
                "unit": "km/h"
            },
            "precipitation": {
                "probability": random.randint(60, 95) if is_rainy else random.randint(0, 30),
                "amount": f"{random.randint(5, 25)}mm" if is_rainy else "0mm"
            },
            "uv_index": random.randint(1, 10),
            "sunrise": f"{random.randint(5, 7):02d}:{random.randint(0, 59):02d}",
            "sunset": f"{random.randint(17, 20):02d}:{random.randint(0, 59):02d}",
            "visibility": random.randint(5, 10),
            "hourly_forecast": [
                {
                    "hour": f"{hour:02d}:00",
                    "temperature": base_temp + random.randint(-3, 5),
                    "condition": random.choice(conditions[:4]),  # Less extreme for hourly
                    "precipitation_prob": random.randint(0, 50)
                }
                for hour in range(0, 24, 3)
            ]
        }

        forecast.append(day_forecast)

    return {
        "city": city,
        "country": "Turkey" if city.lower() in ["istanbul", "ankara", "izmir"] else "Unknown",
        "forecast_start": start_date.strftime("%Y-%m-%d"),
        "forecast_days": len(forecast),
        "current_conditions": forecast[0] if forecast else None,
        "daily_forecast": forecast,
        "summary": generate_weather_summary(forecast),
        "travel_advice": generate_travel_advice(forecast)
    }


def generate_weather_summary(forecast: List[Dict]) -> str:
    """Generate a human-readable weather summary."""
    if not forecast:
        return "No forecast data available"

    avg_high = sum(d["temperature"]["high"] for d in forecast) / len(forecast)
    avg_low = sum(d["temperature"]["low"] for d in forecast) / len(forecast)

    rainy_days = sum(1 for d in forecast if "rain" in d["condition"].lower() or "storm" in d["condition"].lower())

    summary = f"Average temperatures: {avg_high:.1f}°C high, {avg_low:.1f}°C low. "

    if rainy_days > len(forecast) / 2:
        summary += f"Expect rain on {rainy_days} out of {len(forecast)} days. "
    elif rainy_days > 0:
        summary += f"Some rain expected ({rainy_days} days). "
    else:
        summary += "Mostly dry conditions expected. "

    return summary


def generate_travel_advice(forecast: List[Dict]) -> List[str]:
    """Generate travel advice based on weather."""
    advice = []

    if not forecast:
        return ["Check weather closer to travel date"]

    # Check for rain
    rainy_days = sum(1 for d in forecast if d["precipitation"]["probability"] > 50)
    if rainy_days > 0:
        advice.append("Pack an umbrella or rain jacket")

    # Check temperatures
    avg_high = sum(d["temperature"]["high"] for d in forecast) / len(forecast)
    avg_low = sum(d["temperature"]["low"] for d in forecast) / len(forecast)

    if avg_high > 28:
        advice.append("Hot weather expected - bring sunscreen and stay hydrated")
    elif avg_high > 20:
        advice.append("Pleasant temperatures - perfect for outdoor activities")
    elif avg_low < 10:
        advice.append("Cool weather - pack warm layers")

    # Check UV index
    high_uv_days = sum(1 for d in forecast if d["uv_index"] > 7)
    if high_uv_days > 0:
        advice.append("High UV levels - use sun protection")

    # Check wind
    windy_days = sum(1 for d in forecast if d["wind"]["speed"] > 25)
    if windy_days > len(forecast) / 2:
        advice.append("Windy conditions expected - secure loose items")

    return advice if advice else ["Weather conditions look favorable for travel"]


@tool
def get_climate_info(city: str, month: int = None) -> Dict[str, Any]:
    """
    Get general climate information for a city.

    Args:
        city: City name
        month: Month number 1-12 (optional, for month-specific info)

    Returns:
        Climate information and best time to visit
    """

    # Mock climate data
    climate_zones = {
        "istanbul": "Mediterranean/Temperate",
        "london": "Temperate Maritime",
        "paris": "Temperate Oceanic",
        "dubai": "Hot Desert",
        "new york": "Humid Subtropical",
        "tokyo": "Humid Subtropical"
    }

    city_lower = city.lower()
    climate_zone = climate_zones.get(city_lower, "Temperate")

    # Monthly averages (mock data)
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    monthly_data = []
    for i, month_name in enumerate(months, 1):
        # Simulate seasonal variations
        if i in [12, 1, 2]:  # Winter
            temp_high = random.randint(8, 15)
            temp_low = random.randint(2, 8)
            rain_days = random.randint(10, 15)
        elif i in [6, 7, 8]:  # Summer
            temp_high = random.randint(25, 35)
            temp_low = random.randint(18, 24)
            rain_days = random.randint(3, 8)
        else:  # Spring/Fall
            temp_high = random.randint(15, 25)
            temp_low = random.randint(10, 18)
            rain_days = random.randint(8, 12)

        monthly_data.append({
            "month": month_name,
            "month_number": i,
            "temperature_high": temp_high,
            "temperature_low": temp_low,
            "rainfall_mm": random.randint(30, 120),
            "rainy_days": rain_days,
            "sunshine_hours": random.randint(5, 12),
            "tourist_season": "High" if i in [6, 7, 8, 12] else "Low" if i in [1, 2, 11] else "Medium"
        })

    # Best months to visit
    best_months = sorted(monthly_data, key=lambda x: (
        -x["sunshine_hours"],
        x["rainy_days"],
        abs(x["temperature_high"] - 22)  # Prefer temps around 22°C
    ))[:3]

    return {
        "city": city,
        "climate_zone": climate_zone,
        "monthly_averages": monthly_data if not month else [m for m in monthly_data if m["month_number"] == month],
        "best_months_to_visit": [m["month"] for m in best_months],
        "peak_tourist_season": "June - August, December",
        "off_season": "January - February, November",
        "general_tips": [
            f"The climate in {city} is classified as {climate_zone}",
            "Shoulder seasons (spring and fall) often offer good weather with fewer crowds",
            "Check specific dates for local holidays and events"
        ]
    }
