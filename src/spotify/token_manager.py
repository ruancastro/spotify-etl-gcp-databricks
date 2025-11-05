# pylint: disable=R0903, E0611, E0401
"""Module to manage Spotify API tokens using Client Credentials Flow."""

import time
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
        self.token_timeout = None  # Token validity in seconds
        self.token = None

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
        self.token = body.get("access_token")
        if not self.token:
            raise RuntimeError(f"No access_token in response: {body}")

        self.token_timeout = (
            time.time() + body["expires_in"]
        )  # Token validity in seconds
        return self.token

    def is_token_valid(self, offset: int) -> bool:
        """
        Determine whether the stored token is currently valid, allowing an optional
        time offset to check validity proactively.
        Parameters
        ----------
        offset : int
            Number of seconds to add to the current time when evaluating validity.
            Use a positive offset to treat the token as expired earlier (e.g., to
            trigger refresh before actual expiration). A value of 0 checks the token
            against the current time.
        Returns
        -------
        bool
            True if a token timeout is set and the current time plus offset is
            strictly less than the token timeout (i.e., the token is considered valid);
            False if no timeout is set or the token has expired or will expire within
            the offset window.
        """
        if self.token_timeout is None:
            return False
        return time.time() + offset < self.token_timeout

    def get_token(self):
        """Get a valid token, refreshing it if necessary.

        Returns:
            A valid access token string.
        """
        if not self.is_token_valid(offset=60):
            return self.get_new_token()
        return self.token


if __name__ == "__main__":
    # Quick usage example
    load_env(env_path=r".env")

    try:
        token_manager = TokenManager(
            client_id=getenv("CLIENT_ID"), client_secret=getenv("CLIENT_SECRET")
        )
        token = token_manager.get_token()
        print(token)
    except (ValueError, RuntimeError, requests.RequestException) as e:
        print("Error obtaining token:", e)
