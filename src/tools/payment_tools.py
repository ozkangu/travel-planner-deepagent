"""Mock payment processing tools."""

from typing import Dict, Any
from langchain_core.tools import tool
import random
import string
from datetime import datetime


@tool
def process_payment(
    amount: float,
    currency: str,
    payment_method: str,
    card_number: str = None,
    cardholder_name: str = None,
    booking_reference: str = None
) -> Dict[str, Any]:
    """
    Process a payment for travel booking.

    Args:
        amount: Payment amount
        currency: Currency code (e.g., 'USD', 'EUR', 'TRY')
        payment_method: Payment method - 'credit_card', 'debit_card', 'paypal', 'bank_transfer'
        card_number: Card number (last 4 digits for display, e.g., '**** 1234')
        cardholder_name: Name on the card
        booking_reference: Associated booking reference number

    Returns:
        Payment processing result
    """

    # Simulate payment processing (always successful in mock)
    transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    # Mock payment processing delay
    success = random.choice([True, True, True, False])  # 75% success rate

    if success:
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method,
            "timestamp": datetime.now().isoformat(),
            "booking_reference": booking_reference or f"BKG{random.randint(100000, 999999)}",
            "card_last_four": card_number[-4:] if card_number else "****",
            "confirmation_code": ''.join(random.choices(string.ascii_uppercase, k=6)),
            "receipt_url": f"https://payments.example.com/receipt/{transaction_id}",
            "message": "Payment processed successfully"
        }
    else:
        error_reasons = [
            "Insufficient funds",
            "Card declined",
            "Invalid card details",
            "Payment gateway timeout"
        ]
        return {
            "status": "failed",
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": currency,
            "timestamp": datetime.now().isoformat(),
            "error_code": f"ERR{random.randint(1000, 9999)}",
            "error_message": random.choice(error_reasons),
            "message": "Payment failed. Please try again or use a different payment method."
        }


@tool
def verify_payment(transaction_id: str) -> Dict[str, Any]:
    """
    Verify the status of a payment transaction.

    Args:
        transaction_id: The transaction ID to verify

    Returns:
        Payment verification details
    """

    # Mock verification (assume all transactions exist and are completed)
    status = random.choice(["completed", "completed", "completed", "pending", "refunded"])

    return {
        "transaction_id": transaction_id,
        "status": status,
        "verified_at": datetime.now().isoformat(),
        "amount": random.uniform(100, 2000),
        "currency": "USD",
        "payment_method": random.choice(["credit_card", "debit_card", "paypal"]),
        "processed_at": "2024-11-20T14:30:00",
        "details": {
            "merchant": "Travel Planner Services",
            "merchant_id": "MERCH123456",
            "authorization_code": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
            "card_type": random.choice(["Visa", "Mastercard", "American Express"]),
            "card_last_four": f"{random.randint(1000, 9999)}"
        },
        "fraud_check": {
            "status": "passed",
            "risk_score": random.randint(1, 20),
            "checks_performed": ["AVS", "CVV", "3D Secure"]
        }
    }


@tool
def get_payment_methods(country: str = "US") -> Dict[str, Any]:
    """
    Get available payment methods for a specific country.

    Args:
        country: Country code (e.g., 'US', 'TR', 'GB')

    Returns:
        Available payment methods and their details
    """

    # Base payment methods
    methods = {
        "credit_cards": {
            "enabled": True,
            "accepted_brands": ["Visa", "Mastercard", "American Express", "Discover"],
            "currencies": ["USD", "EUR", "GBP", "TRY"],
            "processing_fee": "2.9% + $0.30"
        },
        "debit_cards": {
            "enabled": True,
            "accepted_brands": ["Visa", "Mastercard"],
            "currencies": ["USD", "EUR", "GBP", "TRY"],
            "processing_fee": "1.9% + $0.30"
        },
        "paypal": {
            "enabled": True,
            "currencies": ["USD", "EUR", "GBP"],
            "processing_fee": "3.5%"
        },
        "bank_transfer": {
            "enabled": True,
            "currencies": ["USD", "EUR", "TRY"],
            "processing_time": "1-3 business days",
            "processing_fee": "$5"
        }
    }

    # Country-specific additions
    if country == "TR":
        methods["troy"] = {
            "enabled": True,
            "accepted_brands": ["Troy"],
            "currencies": ["TRY"],
            "processing_fee": "1.5%"
        }
    elif country == "NL":
        methods["ideal"] = {
            "enabled": True,
            "currencies": ["EUR"],
            "processing_fee": "€0.29"
        }

    return {
        "country": country,
        "available_methods": methods,
        "default_currency": "USD" if country == "US" else "EUR",
        "currency_conversion_fee": "3%",
        "security_features": [
            "PCI DSS Compliant",
            "3D Secure",
            "Tokenization",
            "Fraud Detection"
        ]
    }
