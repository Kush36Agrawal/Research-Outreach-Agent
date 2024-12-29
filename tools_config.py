tools = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                },
            },
            "required": ["location"],
        },
    },
    {
        "name": "get_conversational_response",
        "description": "Respond conversationally if no other tools should be called for a given query.",
        "parameters": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "Conversational response to the user.",
                },
            },
            "required": ["response"],
        },
    },
    {
        "name": "get_list_of_emails",
        "description": "Prepare emails to professors of given location(s) from a website",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "The Country, e.g. USA, Singapore, China, etc.",
                },
                "website": {
                    "type": "string",
                    "description": "The website where data is present, e.g. https://www.stanford.edu",
                },
            },
            "required": ["location", "website"],
        },
    },
]
