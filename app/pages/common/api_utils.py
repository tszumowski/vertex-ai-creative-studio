import os
from typing import Any

import google.auth.transport.requests
import google.oauth2.id_token
import requests
from config import config_lib

config = config_lib.AppConfig()


def make_secure_post_request(
    endpoint: str,
    json: dict[str, Any],
    timeout: int = 60,
) -> requests.Response:
    """Makes and authenticated request to an endpoint on the API Gateway.

    Args:
        endpoint: An API Gateway endpoint.
        json: The json payload to send.
        timeout: The timeout for the request.

    Returns:
        An HTTP response object.

    Raises:
        HTTP exception.
    """
    auth_request = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(
        auth_request,
        config.API_GATEWAY_URL,
    )
    headers = {"Authorization": f"Bearer {id_token}"}
    generate_images_url = os.path.join(config.API_GATEWAY_URL, endpoint)
    response = requests.post(
        generate_images_url,
        json=json,
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    return response
