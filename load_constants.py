import json


def load_constants():
    """Load constants from JSON file."""
    try:
        with open('constants.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: constants.json file not found. Using default values.")
        return {
            "test_summary": {
                "test_id": "HP-2023-045",
                "start_date": "Oct 15, 2023",
                "sample_size": "45,328 visitors",
                "status": "Completed",
                "status_class": "bg-success",
                "confidence_level": "95%"
            },
            "sample_size_calculation": {
                "required_sample": "40,000 visitors",
                "achieved_sample": "45,328 visitors",
                "power": "80%",
                "progress_percentage": 100,
                "minimum_detectable_effect": "10%"
            },
            "confidence_interval": {
                "conversion_rate_difference": "1.2% ± 0.4%",
                "confidence_level": "95%",
                "probability_variant_best": "98.7%",
                "probability_control_best": "1.3%"
            },
            "recommendation": {
                "title": "Implement Variant B",
                "description": "The test achieved statistical significance with a 14.3% improvement in conversion rate. This change is expected to generate substantial annual revenue increase.",
                "alert_class": "alert-success",
                "button_text": "Create Implementation Ticket"
            }
        }
