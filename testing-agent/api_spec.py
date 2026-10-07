API_SPEC = {
    "service": "NEXA/AUTH Authentication API",
    "base_url": "http://127.0.0.1:8000",
    "endpoints": [
        {
            "method": "POST",
            "path": "/auth/signup",
            "description": "Create a new user account",
            "available": True,
        },
        {
            "method": "POST",
            "path": "/auth/login",
            "description": "Authenticate an existing user",
            "available": True,
        },
        {
            "method": "GET",
            "path": "/",
            "description": "API root status",
            "available": True,
        },
        {
            "method": "GET",
            "path": "/health",
            "description": "Health check",
            "available": True,
        },
    ],
    "authentication": {
        "type": "JWT Bearer",
        "implemented": True,
    },
    "features": {
        "signup": True,
        "login": True,
        "logout": False,
        "password_reset": False,
        "account_lockout": False,
        "rate_limiting": False,
        "protected_endpoints": False,
    },
}