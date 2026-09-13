from typing import Any


def validate_incident(data: dict) -> tuple[bool, list[str]]:
    errors = []
    
    if not isinstance(data, dict):
        return False, ["Item is not a valid object"]
    
    required_fields = ["incidente"]
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    if "riesgo" in data and data["riesgo"] not in ["bajo", "medio", "alto", "critico", None]:
        errors.append(f"Invalid riesgo value: {data['riesgo']}. Must be: bajo, medio, alto, critico")
    
    return len(errors) == 0, errors


def parse_incidents_response(data: list[dict]) -> tuple[list[dict], list[dict]]:
    valid_incidents = []
    errors = []
    
    if not isinstance(data, list):
        return [], [{"error": "Response must be a JSON array"}]
    
    for idx, item in enumerate(data):
        is_valid, item_errors = validate_incident(item)
        if is_valid:
            valid_incidents.append(item)
        else:
            errors.append({
                "index": idx,
                "errors": item_errors,
                "data": item
            })
    
    return valid_incidents, errors
