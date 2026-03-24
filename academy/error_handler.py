"""
Utilities for request validation and API error handling.
"""

from rest_framework.response import Response
from rest_framework.decorators import api_view
import binascii
from functools import wraps
import json
from .exceptions import (
    BinaryNotSupported,
    ResourceAlreadyExistsHelpers,
    ResourceNotExists,
    ResourceAlreadyExists,
    ParameterInvalid,
    InvalidPath,
)
from .file_access import FAL_RA
import os
from django.conf import settings
from copy import copy

CUSTOM_EXCEPTIONS = (
    ResourceNotExists,
    ResourceAlreadyExists,
    ParameterInvalid,
    InvalidPath,
    BinaryNotSupported,
    ResourceAlreadyExistsHelpers,
)

# Reuse a preconfigured file-access object and clone it per request so
# each wrapped view starts from the same backend paths safely.
local_fal = FAL_RA(
    settings.BASE_DIR,
    os.path.join(settings.BASE_DIR, "exercises"),
)


def error_wrapper(type: str, param: list[str | tuple] = []):
    """Decorator for API views with parameter validation and error handling."""

    def decorated(func):
        @wraps(func)
        @api_view([type])
        def wrapper(request):
            try:
                fal = copy(local_fal)
                check_parameters(
                    request.data if type == "POST" else request.GET,
                    param,
                )
                return func(fal, request)
            except CUSTOM_EXCEPTIONS as e:
                # Domain-specific exceptions already carry the status code that
                # should be exposed to the frontend.
                print(str(e))
                return Response({"message": str(e)}, status=e.error_code)
            except json.JSONDecodeError as e:
                print(str(e))
                return Response(
                    {"error": f"Invalid JSON format: {str(e)}"},
                    status=422,
                )
            except (binascii.Error, ValueError) as e:
                print(str(e))
                return Response(
                    {"error": f"Invalid B64 format: {str(e)}"},
                    status=422,
                )
            except Exception as e:
                print(str(e))
                return Response(
                    {"error": f"An error occurred: {str(e)}"},
                    status=500,
                )

        return wrapper

    return decorated


def check_parameters(request, param: list[str | tuple]):
    """
    Validate that required fields are present and meet length constraints.
    """

    for p in param:
        min_len = 0
        if type(p) is tuple:
            # A tuple parameter encodes both the field name and the minimum
            # accepted payload length, e.g. ("location", -1).
            min_len = p[1]
            p = p[0]
        if p not in request:
            raise ParameterInvalid(p)
        data = request.get(p)
        if data is None or len(data) <= min_len:
            raise ParameterInvalid(p)
