from typing import Any, Optional, Dict

def return_message(
    results: Any,
    success: bool,
    time_elapsed: Optional[float] = None,
    response_message: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    response = {
        "results": results,
        "success": success,
        **kwargs,
    }
    if time_elapsed is not None:
        response["time_elapsed"] = time_elapsed
    if response_message is not None:
        response["response_message"] = response_message
    return response
        