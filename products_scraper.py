import requests
from lxml.html import fromstring
import csv
from typing import List, Dict

class Scraper:
    def __init__(self, base_url: str, xpaths: Dict[str, str], total_pages: int, csv_filename: str, product_dict: Dict[str, str]):
        """
        Initialize the scraper with configuration for paginated product extraction.

        :param base_url: The pagination base URL, expecting a {} for page numbers.
        :param xpaths: Dictionary containing XPaths for navigating pages.
        :param total_pages: Total number of pages to scrape.
        :param csv_filename: Name of the CSV file to save the extracted data.
        :param product_dict: Dictionary defining the product data to extract using XPaths.
        """
        self.base_url = base_url
        self.xpaths = xpaths
        self.total_pages = total_pages
        self.csv_filename = csv_filename
        self.product_dict = product_dict

    def fetch_page(self, page: int) -> str:
        """
        Fetches HTML content of a page.

        :param page: Page number to fetch.
        :return: HTML content of the page.
        """
        url = self.base_url.format(page)
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error fetching {url}")
            return ""

    def extract_data(self, html: str) -> List[Dict[str, str]]:
        """
        Extracts product data from HTML content.

        :param html: HTML content to extract data from.
        :return: List of dictionaries, each containing product data.
        """
        tree = fromstring(html)
        products = []

        product_nodes = tree.xpath(self.xpaths['products'])
        for product_node in product_nodes:
            product_data = {}
            for key, xpath in self.product_dict.items():
                results = product_node.xpath(xpath)
                product_data[key] = results[0].strip() if results else ""
            products.append(product_data)

        return products

    def save_to_csv(self, products: List[Dict[str, str]]):
        """
        Saves extracted product data to a CSV file.

        :param products: List of dictionaries containing product data.
        """
        with open(self.csv_filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.product_dict.keys())
            file.seek(0, 2)  # Move to the end of the file to check if it's empty
            if file.tell() == 0:  # If file is empty, write the header
                writer.writeheader()
            writer.writerows(products)

    def run(self):
        """
        Runs the scraper to extract data across multiple pages and save it to a CSV file.
        """
        for page in range(1, self.total_pages + 1):
            html = self.fetch_page(page)
            if html:
                products = self.extract_data(html)
                self.save_to_csv(products)
                print(f"Page {page} processed.")

if __name__ == "__main__":
    product_dict = {
        'name': './/h2[@class="product-title"]/a/text()',  # Ejemplo de XPath para el nombre del producto
        'price': './/span[@class="price"]/text()',  # Ejemplo de XPath para el precio
        'image_url': './/img[@class="img-fluid image-cover"]/@src',
        'descor': './/div[@class="product-desc mb-15"]/text()',
        'pdf': './/div[@class="ficha-producto"]/a/@href',
        'disponibilidad': './/div[@class="product-list-availability"]/span/text()',
        # Añade más campos según sea necesario
    }

    xpaths = {
        'products': '//*[@id="js-product-list"]/div/div[contains(@class, "item")]',  # XPath para contenedores de productos
    }

    scraper = Scraper(base_url="https://web.com?resultsPerPage=200&page={}",
                      xpaths=xpaths,
                      total_pages=141,  # Número de páginas a scrape
                      csv_filename="csv_name.csv",
                      product_dict=product_dict)
    scraper.run()
