import base64
from typing import Optional, Union
from urllib.parse import urljoin

import click
import requests


class JiraServer:
    host: str
    auth_string: str
    session: requests.Session
    dry_run: bool

    def __init__(self, host: str, auth_string: str, dry_run: bool = False) -> None:
        self.host = host
        self.auth_string = auth_string
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.headers.update(self._get_auth_header())

    def _get_auth_header(self) -> dict:
        encoded_auth = base64.b64encode(self.auth_string.encode()).decode()

        auth_header = {"Authorization": f"Basic {encoded_auth}"}
        return auth_header

    def _get_url(self, path: str) -> str:
        return urljoin(self.host, path)

    def get(self, path: str, params: Optional[dict] = None) -> Union[dict, list]:

        response = self.request(method="GET", path=path, params=params)
        return response

    def post(self, path: str, payload: dict) -> Union[dict, list]:
        response = self.request(method="POST", path=path, payload=payload)
        return response

    def request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        payload: Optional[dict] = None,
    ) -> Union[dict, list]:
        url = self._get_url(path)

        if self.dry_run:
            click.echo(f"Url: {url}")
            click.echo(f"Payload: {payload}")
            return {}

        response = self.session.request(method, url, params=params, json=payload)

        return response.json()
