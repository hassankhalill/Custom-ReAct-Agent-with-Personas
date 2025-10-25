"""
Tool functions for the BreatheEasy ReAct Agent
These tools provide the agent with capabilities to interact with business data
"""

import json
from datetime import datetime
from typing import Dict, List, Any


# Business data - services information
SERVICES_DATA = {
    "deep_cleaning": {
        "name": "Deep Cleaning Services",
        "description": "Comprehensive top-to-bottom cleaning of your entire home",
        "features": [
            "Focus on high-traffic areas and overlooked spaces",
            "Allergen elimination from carpets, upholstery, and air vents",
            "Perfect for seasonal refreshes or post-renovation cleanup"
        ],
        "duration": "4-8 hours",
        "pricing": "$200-$400 depending on home size"
    },
    "move_cleaning": {
        "name": "Move-In/Move-Out Cleaning",
        "description": "Thorough cleaning to prepare homes for new occupants",
        "features": [
            "Special attention to sanitizing kitchens and bathrooms",
            "Guarantee of allergen-free spaces for fresh starts",
            "Flexible scheduling to match your moving timeline"
        ],
        "duration": "3-6 hours",
        "pricing": "$180-$350 depending on home size"
    },
    "allergen_treatment": {
        "name": "Allergen Treatment Services",
        "description": "Specialized protocols for homes with allergy sufferers",
        "features": [
            "HEPA filtration vacuuming and air purification",
            "Dust mite elimination and prevention strategies",
            "Mold inspection and remediation",
            "Pet dander removal treatments"
        ],
        "duration": "2-4 hours",
        "pricing": "$150-$300 depending on treatment scope"
    },
    "regular_maintenance": {
        "name": "Regular Maintenance Cleaning",
        "description": "Weekly, bi-weekly, or monthly cleaning schedules",
        "features": [
            "Customized cleaning plans based on household needs",
            "Consistent team members who know your home",
            "Eco-friendly products tailored to your preferences"
        ],
        "duration": "2-3 hours per visit",
        "pricing": "$100-$200 per visit, discounts for recurring service"
    }
}

PRODUCTS_DATA = {
    "all_purpose_cleaner": {
        "name": "EcoClean All-Purpose Cleaner",
        "ingredients": "Plant-based surfactants, citric acid, essential oils",
        "certifications": ["EPA Safer Choice", "EWG Verified"],
        "allergen_free": True,
        "use_cases": ["Countertops", "Appliances", "General surfaces"]
    },
    "bathroom_cleaner": {
        "name": "GreenShine Bathroom Sanitizer",
        "ingredients": "Hydrogen peroxide, plant-based acids, natural enzymes",
        "certifications": ["EPA Safer Choice", "Leaping Bunny Certified"],
        "allergen_free": True,
        "use_cases": ["Toilets", "Showers", "Sinks"]
    },
    "floor_cleaner": {
        "name": "PureFloor Wood & Tile Cleaner",
        "ingredients": "Plant-derived cleaning agents, water",
        "certifications": ["Green Seal Certified", "EWG A-rated"],
        "allergen_free": True,
        "use_cases": ["Hardwood", "Tile", "Laminate"]
    },
    "glass_cleaner": {
        "name": "CrystalClear Glass Cleaner",
        "ingredients": "Vinegar, plant-based alcohols, filtered water",
        "certifications": ["EPA Safer Choice"],
        "allergen_free": True,
        "use_cases": ["Windows", "Mirrors", "Glass surfaces"]
    }
}

SERVICE_AREAS = [
    "Downtown Metropolitan Area",
    "Northside District",
    "Westend Village",
    "Eastbridge",
    "Southgate",
    "Riverside Community",
    "Hilltop Estates",
    "Lakeside"
]

# Storage for leads and feedback
customer_leads = []
customer_feedback = []


def search_services(query: str) -> str:
    """
    Search for cleaning services based on customer query.

    Args:
        query: Search query (e.g., "allergen", "move out", "regular")

    Returns:
        JSON string with matching services
    """
    query_lower = query.lower()
    matching_services = []

    for service_id, service_info in SERVICES_DATA.items():
        # Search in name, description, and features
        search_text = (
            service_info["name"] + " " +
            service_info["description"] + " " +
            " ".join(service_info["features"])
        ).lower()

        if query_lower in search_text:
            matching_services.append({
                "id": service_id,
                **service_info
            })

    if not matching_services:
        # Return all services if no match
        matching_services = [{"id": k, **v} for k, v in SERVICES_DATA.items()]

    return json.dumps(matching_services, indent=2)


def check_availability(location: str) -> str:
    """
    Check if BreatheEasy services are available in a specific location.

    Args:
        location: The location to check

    Returns:
        Availability status message
    """
    location_lower = location.lower()

    # Check if location matches any service area
    for area in SERVICE_AREAS:
        if location_lower in area.lower() or area.lower() in location_lower:
            return json.dumps({
                "available": True,
                "area": area,
                "message": f"Yes! We provide services in {area}. Contact us to schedule.",
                "contact": {
                    "email": "hello@breatheeasy.com",
                    "phone": "(555) 123-EASY",
                    "hours": "Monday-Saturday, 8am-6pm"
                }
            }, indent=2)

    return json.dumps({
        "available": False,
        "message": f"We don't currently service {location}, but we're expanding! Please leave your contact info and we'll notify you when we reach your area.",
        "nearby_areas": SERVICE_AREAS[:3]
    }, indent=2)


def get_product_info(product_category: str = "all") -> str:
    """
    Get information about cleaning products used by BreatheEasy.

    Args:
        product_category: Category of products (all, all_purpose, bathroom, floor, glass)

    Returns:
        JSON string with product information
    """
    category_lower = product_category.lower().replace(" ", "_")

    if category_lower == "all":
        return json.dumps(PRODUCTS_DATA, indent=2)

    # Search for matching product
    for product_id, product_info in PRODUCTS_DATA.items():
        if category_lower in product_id or category_lower in product_info["name"].lower():
            return json.dumps({product_id: product_info}, indent=2)

    return json.dumps({
        "message": "Product category not found",
        "available_categories": list(PRODUCTS_DATA.keys())
    }, indent=2)


def record_customer_interest(name: str, email: str, message: str) -> str:
    """
    Record customer interest/lead information.

    Args:
        name: Customer's name
        email: Customer's email address
        message: Customer's message or interest details

    Returns:
        Confirmation message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lead_data = {
        'timestamp': timestamp,
        'name': name,
        'email': email,
        'message': message
    }

    customer_leads.append(lead_data)

    # Log to console
    print("\n" + "="*60)
    print("NEW CUSTOMER LEAD RECORDED")
    print("="*60)
    print(f"Timestamp: {timestamp}")
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Message: {message}")
    print("="*60 + "\n")

    # Save to file
    try:
        with open('customer_leads.json', 'w') as f:
            json.dump(customer_leads, f, indent=2)
    except Exception as e:
        print(f"Error saving lead to file: {e}")

    return json.dumps({
        "status": "success",
        "message": f"Thank you {name}! Your information has been recorded. We'll contact you at {email} shortly.",
        "next_steps": "Our team will reach out within 24 hours to discuss your needs and schedule a service."
    }, indent=2)


def record_feedback(question: str) -> str:
    """
    Record customer feedback or unanswered questions.

    Args:
        question: The question or feedback that couldn't be answered

    Returns:
        Confirmation message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    feedback_data = {
        'timestamp': timestamp,
        'question': question
    }

    customer_feedback.append(feedback_data)

    # Log to console
    print("\n" + "="*60)
    print("UNANSWERED QUESTION RECORDED")
    print("="*60)
    print(f"Timestamp: {timestamp}")
    print(f"Question: {question}")
    print("="*60 + "\n")

    # Save to file
    try:
        with open('customer_feedback.json', 'w') as f:
            json.dump(customer_feedback, f, indent=2)
    except Exception as e:
        print(f"Error saving feedback to file: {e}")

    return json.dumps({
        "status": "recorded",
        "message": "Your question has been recorded and will be reviewed by our team. We'll get back to you with an answer soon!",
        "contact_for_urgent": "For urgent matters, please call (555) 123-EASY"
    }, indent=2)


# Tool definitions for LangGraph/LangChain
TOOL_DEFINITIONS = [
    {
        "name": "search_services",
        "description": "Search for BreatheEasy cleaning services based on customer needs. Use this when the customer asks about what services are available, specific cleaning types, or wants to know what BreatheEasy offers.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query describing what the customer needs (e.g., 'allergen cleaning', 'move out', 'regular maintenance')"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "check_availability",
        "description": "Check if BreatheEasy services are available in a specific location or area. Use this when customer asks about service coverage or availability in their neighborhood.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location or area name to check (e.g., 'Downtown', 'Northside', 'Eastbridge')"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_product_info",
        "description": "Get detailed information about the eco-friendly cleaning products used by BreatheEasy. Use this when customers ask about product ingredients, certifications, allergen-safety, or what products are used for specific cleaning tasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_category": {
                    "type": "string",
                    "description": "Category of products to retrieve: 'all' for all products, 'all_purpose', 'bathroom', 'floor', or 'glass' for specific categories",
                    "default": "all"
                }
            },
            "required": []
        }
    },
    {
        "name": "record_customer_interest",
        "description": "Record customer contact information and interest in services. Use this when a customer wants to schedule a service, request a quote, or leave their details for follow-up. Always collect name, email, and details about what they need.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Customer's full name"
                },
                "email": {
                    "type": "string",
                    "description": "Customer's email address"
                },
                "message": {
                    "type": "string",
                    "description": "Details about their interest, service needed, or specific requirements"
                }
            },
            "required": ["name", "email", "message"]
        }
    },
    {
        "name": "record_feedback",
        "description": "Record customer questions or feedback that cannot be answered with available information. Use this as a last resort when you genuinely don't know the answer and none of the other tools can help.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question or feedback that could not be answered"
                }
            },
            "required": ["question"]
        }
    }
]


# Map function names to actual functions
TOOL_FUNCTIONS = {
    "search_services": search_services,
    "check_availability": check_availability,
    "get_product_info": get_product_info,
    "record_customer_interest": record_customer_interest,
    "record_feedback": record_feedback
}
