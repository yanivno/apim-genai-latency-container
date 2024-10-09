import os
class configuration:
    aoai_api_version = "2024-06-01"
    apim_url = "https://my-apim.azure-api.net"
    apim_api_key = "my"
    sleep_timeout = 120

    endpoints = [
        {
            "endpoint": "aoai-3-qkojak7tombza.openai.azure.com",
            "deployment_name": "gpt-4o",
            "api_key": "ddddddddddddddddddddddddddddddddd",
            "backend_id": "my-aoai-1-backend"
        },
       {
            "endpoint": "aoai-3-qkojak7tombza.openai.azure.com",
            "deployment_name": "gpt-4o-mini",
            "api_key": "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq",
            "backend_id": "my-aoai-2-backend"
        }
    ]