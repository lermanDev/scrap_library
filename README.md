# WebConnector
The WebConnector class provides a streamlined interface for performing web requests, handling sessions, and extracting data from web responses. Built on top of the popular requests library and leveraging the lxml library for parsing and extracting data, it simplifies the process of logging in and out of web services, making custom requests, and processing HTML responses.

## Features
* Session Management: Handles session persistence across requests, making it easier to manage logged-in states.
* Flexible Data Extraction: Extracts data from HTML responses using XPath, supporting various input formats for flexibility.
* Dynamic Header Management: Allows for dynamic updating of request headers, useful for setting custom authentication tokens or content types.
* Versatile Request Handling: Supports making generic HTTP requests with customizable methods and parameters.

## Installation
Before using WebConnector, ensure you have Python installed on your system and the required packages requests and lxml. You can install these packages using pip:

    pip install requests lxml

## Usage
Here is a basic example of how to use the WebConnector class:


    from web_connector import WebConnector

    # Initialize the WebConnector with the base URL of the website you're interacting with
    connector = WebConnector(base_url="https://example.com", username="user", password="pass")

    # Login
    connector.login(login_url="/login")

    # Perform a custom request
    response = connector.make_request(method="GET", url="/dashboard")

    # Extract data from the response
    data = connector.extract_data_from_response(xpaths="//div[@class='data']", response=response)
    print(data)

    # Logout
    connector.logout(logout_url="/logout")

## Methods
* login(login_url: str, login_data: Optional[Dict[str, str]] = None) -> Response: Logs into a web service.
* logout(logout_url: str) -> Response: Logs out of a web service.
extract_data_from_response(xpaths: Union[str, Dict[str, str], List[str], Tuple[str, ...]], response: Optional[Response] = None) -> Union[str, Dict[str, str]]: Extracts data from an HTML response.
* set_headers(headers: Dict[str, str]): Updates session headers.
* make_request(method, url: str, **kwargs) -> Response: Makes an HTTP request.


## Contributing
Contributions to the WebConnector class are welcome! Please feel free to fork the repository, make your changes, and submit a pull request.