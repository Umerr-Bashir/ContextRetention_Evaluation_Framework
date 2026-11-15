import json
from pydantic import ValidationError
from schemas import DocumentAnalysis

# Reference OpenAI GPT-4o mini pricing.
# These are configurable estimates, NOT confirmed HF Router prices.

INPUT_PRICE_PER_1M = 0.15
OUTPUT_PRICE_PER_1M = 0.60

def calculate_cost(input_tokens: int, output_tokens: int) -> float:

    input_cost = (
        input_tokens / 1_000_000
    ) * INPUT_PRICE_PER_1M

    output_cost = (
        output_tokens / 1_000_000
    ) * OUTPUT_PRICE_PER_1M

    return input_cost + output_cost



def validate_summary(summary_text: str, schema) -> dict:

    try:
        parsed_json = json.loads(summary_text)

        # Handle JSON encoded inside another JSON string.
        if isinstance(parsed_json, str):
            parsed_json = json.loads(parsed_json)

    except json.JSONDecodeError as error:
        return {
            "json_valid": False,
            "schema_valid": False,
            "error": str(error)
        }

    try:
        schema.model_validate(parsed_json)

        return {
            "json_valid": True,
            "schema_valid": True,
            "error": None
        }

    except ValidationError as error:
        return {
            "json_valid": True,
            "schema_valid": False,
            "error": str(error)
        }