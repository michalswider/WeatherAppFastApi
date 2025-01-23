def connection_error_response_model(city: str, error: str):
    return {
        "city": city,
        "error": "Connection error",
        "details": error,
    }


def timeout_error_response_model(city: str, error: str):
    return {"city": city, "error": "Request timeout", "details": error}


def request_error_response_model(city: str, error: str):
    return {"city": city, "error": "Network error", "details": error}


def not_found_error_response_model(city: str, error: str):
    return {"city": city, "error": "Not Found", "details": error}


def invalid_error_response_model(city: str, error: str):
    return {"city": city, "error": "Invalid error", "details": error}


def http_error_response_model(city: str, status_code: int, error: str):
    return {"city": city, "status_code": status_code, "details": error}
