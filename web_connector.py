import requests
from requests.models import Response
from typing import Optional, Union, Dict, List, Tuple
from lxml.html import fromstring
import json


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
        delimiter: str = ', ',
    ) -> Union[str, Dict[str, Union[str, List[str]]], List[Dict[str, str]]]:
        """
        Modified to extract all matches for given XPaths. Returns a dictionary for single values or lists of values,
        and a list of dictionaries for key-value data extraction.
        
        :param xpaths: A single XPath as a string, a dictionary, a list, or a tuple of XPaths.
        :param response: Optional, the response object from which to extract data. Uses the last response if not provided.
        :return: Depending on xpaths input, returns a single data value, a dictionary with lists of results,
                 or a list of dictionaries for key-value paired data.
        """
        if response is None:
            if self.last_response is None:
                raise ValueError("No response is available for extraction.")
            response = self.last_response

        soup = fromstring(response.text)
        print(response.text)
        def extract(xpath):
            aux = soup.xpath(xpath)
            return delimiter.join(set([elem.strip() for elem in soup.xpath(xpath) if elem.strip()]))

        if isinstance(xpaths, str):
            return extract(xpaths)

        elif isinstance(xpaths, (dict, list, tuple)):
            results = {}
            for key, xpath in (xpaths.items() if isinstance(xpaths, dict) else enumerate(xpaths)):
                extracted = extract(xpath)
                # If multiple values are found for a single XPath, return them all
                results[key] = extracted if len(extracted) > 1 else (extracted[0] if extracted else None)

            return results

        else:
            raise ValueError("xpaths must be a string, a dictionary, a list, or a tuple.")

    def extract_key_value_data(self, key_xpath: str, value_xpath: str, response: Optional[Response] = None) -> List[Dict[str, str]]:
        """
        Extracts key-value paired data from a page, useful for extracting data from tables or structured formats.

        :param key_xpath: The XPath to extract keys.
        :param value_xpath: The XPath to extract corresponding values.
        :param response: Optional, the response object from which to extract data. Uses the last response if not provided.
        :return: A list of dictionaries, each representing a key-value pair.
        """
        if response is None:
            if self.last_response is None:
                raise ValueError("No response is available for extraction.")
            response = self.last_response

        soup = fromstring(response.text)
        keys = soup.xpath(key_xpath)
        values = soup.xpath(value_xpath)

        return [{key.strip(): value.strip()} for key, value in zip(keys, values) if key.strip() and value.strip()]

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



# Example usage
# if __name__ == "__main__":
#     connector = WebConnector("https://example.com")
#     connector.make_request("GET", "/products")
#     xpaths = {
#         "product_names": "//div[@class='product']/name/text()",
#         "product_prices": "//div[@class='product']/price/text()"
#     }
#     products_data = connector.extract_data_from_response(xpaths)
#     print(json.dumps(products_data, indent=4))
    
#     # Extracting key-value pair data
#     table_data = connector.extract_key_value_data("//table[@id='product-details']")
#     print(json.dumps(table_data, indent=4))

