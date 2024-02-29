import requests
from requests.models import Response
from typing import Optional, Union, Dict, List, Tuple
from lxml.html import fromstring


class WebConnector:
    def __init__(
        self,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = base_url
        self._session = requests.Session()
        self.username = username
        self.password = password
        self.last_response = None

        if default_headers:
            self._session.headers.update(default_headers)

    def login(
        self, login_url: str, login_data: Optional[Dict[str, str]] = None
    ) -> Response:
        """
        Performs a login operation using provided credentials.

        :param login_url: The URL endpoint for the login request.
        :param login_data: Optional dictionary containing login credentials.
                           If None, uses the username and password provided during class initialization.
        :return: The response object from the login request.
        """
        login_data = login_data or {
            "username": self.username,
            "password": self.password,
        }
        self.last_response = self._session.post(
            f"{self.base_url}{login_url}", data=login_data
        )
        return self.last_response

    def logout(self, logout_url: str) -> Response:
        """
        Performs a logout operation by sending a request to the specified logout URL.

        This method is used to terminate a session or log out from a web service. It updates `self.last_response`
        with the response from the logout request.

        :param logout_url: The URL endpoint for the logout request.
        :return: The response object received after the logout request.
        """
        self.last_response = self._session.get(f"{self.base_url}{logout_url}")
        return self.last_response

    def extract_data_from_response(
        self,
        xpaths: Union[str, Dict[str, str], List[str], Tuple[str, ...]],
        response: Optional[Response] = None,
    ) -> Union[str, Dict[str, str]]:
        """
        Extracts data from a response object using a provided XPath, a dictionary of XPaths,
        or a list/tuple of XPaths. If no response is provided, the last response is used.

        :param xpaths: A string representing a single XPath, a dictionary with XPaths, or a list/tuple of XPaths.
        :param response: (Optional) The response object from which to extract data.
        :return: A single data value, a dictionary of results, or an ordered dictionary depending on xpaths input.
        """
        if response is None:
            if self.last_response is None:
                raise ValueError("No response is available for extraction.")
            response = self.last_response

        soup = fromstring(response.text)

        def extract_single_xpath(xpath):
            result = soup.xpath(xpath)

            # return result[0] if result else None
            try:
                return result[0]
            except IndexError:
                return None

        if isinstance(xpaths, str):
            return extract_single_xpath(xpaths)

        elif isinstance(xpaths, (dict, list, tuple)):
            results = {}
            # Create an iterable to unify handling of dict and list/tuple
            
            # iterable = xpaths.items() if isinstance(xpaths, dict) else enumerate(xpaths)
            try:
                items = xpaths.items()
            except AttributeError:
                items = enumerate(xpaths)

            for key, xpath in items:
                results[key] = extract_single_xpath(xpath)

            return results

        else:
            raise ValueError(
                "xpaths must be a string, a dictionary, a list, or a tuple."
            )

    def set_headers(self, headers: Dict[str, str]):
        """
        Updates the session headers with the provided header dictionary.

        This method allows you to modify the headers that will be sent with subsequent requests made by the session.
        It can be used to set authentication tokens, content types, or any other necessary HTTP headers.

        :param headers: A dictionary of header key-value pairs to be added to or updated in the session headers.
        """
        self._session.headers.update(headers)

    def make_request(self, method, url: str, **kwargs) -> Response:
        """
        Makes a web request using the specified HTTP method and URL.

        :param method: The HTTP method to use for the request (e.g., 'GET', 'POST').
        :param url: The URL endpoint for the request.
        :param kwargs: Additional arguments to pass to the request method (e.g., headers, data).
        :return: The response object from the request.
        """
        url = f"{self.base_url}{url}"
        self.last_response = self._session.request(method, url, **kwargs)
        return self.last_response