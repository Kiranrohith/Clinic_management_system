def success_response(message: str, data: dict | list | None = None) -> dict:
    return {
        "success": True,
        "message": message,
        "data": {} if data is None else data,
    }


def error_response(message: str, errors: list | None = None) -> dict:
    return {
        "success": False,
        "message": message,
        "errors": [] if errors is None else errors,
    }
