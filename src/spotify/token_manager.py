# pylint: disable=R0903, E0611, E0401
"""Module to manage Spotify API tokens using Client Credentials Flow."""

from os import getenv
import base64
import requests
from utils.load_env import load_env


class TokenManager:
    """Class to manage Spotify API tokens."""

    load_env()  # Ensure env vars are loaded at class load time

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_new_token(self) -> str:
        """Obtain a Spotify access token using the Client Credentials Flow.

        The function will use the provided ``client_id`` and ``client_secret``.
        If those are missing, it will try to load a ``.env`` file from the project root.

        Args:
            client_id: Spotify Client ID. If ``None``, read from environment or
                ``.env``.
            client_secret: Spotify Client Secret. If ``None``, read from environment
                or ``.env``.

        Returns:
            The access token string.

        Raises:
            ValueError: If client_id or client_secret cannot be found in the
                arguments, environment, or .env file.
            RuntimeError: If the token endpoint returns a non-200 status code or
                the response does not contain an access token.
        """

        auth_b64 = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            headers=headers,
            data=data,
            timeout=10,
        )
        # time.sleep(2)  # to avoid hitting rate limits in tests
        if resp.status_code != 200:
            raise RuntimeError(
                f"Failed to obtain token: {resp.status_code} - {resp.text}"
            )

        body = resp.json()
        new_token = body.get("access_token")
        if not new_token:
            raise RuntimeError(f"No access_token in response: {body}")
        return new_token


if __name__ == "__main__":
    # Quick usage example
    load_env(env_path=r".env")

    try:
        token_manager = TokenManager(
            client_id=getenv("CLIENT_ID"), client_secret=getenv("CLIENT_SECRET")
        )
        token = token_manager.get_new_token()
        print(token)
    except (ValueError, RuntimeError, requests.RequestException) as e:
        print("Error obtaining token:", e)
