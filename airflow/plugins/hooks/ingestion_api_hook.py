import json
from airflow.hooks.http_hook import HttpHook
from airflow.hooks.base import BaseHook

class IngestionApiHook(HttpHook):
    """
    A custom HTTP hook to handle API ingestion tasks.

    Inherits from HttpHook and allows sending GET and POST requests.
    """

    def __init__(self, http_conn_id, method='GET'):
        """
        Initializes the IngestionApiHook.

        Args:
            http_conn_id (str): The Airflow connection ID for the HTTP endpoint.
            method (str): The HTTP method to use for requests (default is 'GET').
        """
        super().__init__(method=method, http_conn_id=http_conn_id)

    def run(self, endpoint, data=None, headers=None):
        """
        Executes an HTTP request with the specified endpoint, data, and headers.

        Args:
            endpoint (str): The API endpoint to send the request to.
            data (dict, optional): The data to send in the body of the request (for POST requests).
            headers (dict, optional): The headers to include in the request.

        Returns:
            dict: The JSON response from the API.
        """
        self.method = self.method.upper()
        if self.method == 'POST' and data:
            response = super().run(
                endpoint,
                data=json.dumps(data),
                headers=headers
            )
            return response.json()

        response = super().run(
            endpoint,
            headers=headers
        )
        return response.json()