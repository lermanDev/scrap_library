import requests
import csv
import json
from typing import Any, Dict, List

class WebJsonDataExtractor:
    def __init__(self, config: Dict[str, Any], csv_filename: str):
        """
        Inicializa el extractor de datos JSON que lee desde una URL de página web.

        :param config: Un diccionario que especifica cómo extraer datos del JSON.
        :param csv_filename: Nombre del archivo CSV donde se guardarán los datos.
        """
        self.config = config
        self.csv_filename = csv_filename

    def fetch_json_from_url(self, url: str) -> Dict[str, Any]:
        """
        Realiza una solicitud HTTP a la URL dada y devuelve el contenido JSON.

        :param url: La URL de la página web que devuelve el contenido JSON.
        :return: Un diccionario con los datos JSON.
        """
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch JSON data. Status code: {response.status_code}")

    def extract_values(self, data: Dict[str, Any], path: str) -> List[str]:
        """
        Extrae valores del diccionario JSON basado en una ruta de claves separadas por puntos.
        
        :param data: El diccionario de datos JSON de donde extraer los valores.
        :param path: La ruta de acceso a los datos dentro del JSON, separada por puntos.
        :return: Una lista de valores extraídos.
        """
        # Divide la ruta en claves individuales
        keys = path.split('.')
        
        # Función auxiliar para navegar recursivamente a través de las claves
        def navigate(data, keys):
            if not keys:
                return data

            # Special case only one value on list return value
            if isinstance(data, list) and len(data) == 1:
                data = data[0]
            
            # Verifica si la clave actual es una lista para manejar múltiples valores
            if isinstance(data, list):
                return [navigate(item, keys.copy()) for item in data.copy()]
            
            key = keys.pop(0)
            if key in data:
                return navigate(data[key], keys)
            else:
                return []
        
        result = navigate(data, keys)
        
        # Parte final modificada para concatenar valores o devolver el valor único
        if isinstance(result, list):
            # Elimina duplicados y None
            unique_results = [str(v).strip() for v in result if v is not None and str(v).strip()]
            
            # Concatena los valores en una cadena de texto si hay más de uno, 
            # de lo contrario devuelve el único valor o una cadena vacía si no hay resultados
            return str(unique_results) if len(unique_results) > 1 else (next(iter(unique_results), ''))
        else:
            return str(result) if result is not None else ''

    def process_json(self, url: str) -> Dict[str, List[str]]:
        """
        Procesa el JSON obtenido de una URL y extrae los datos según el diccionario de configuración.

        :param url: La URL de la página web para obtener el JSON.
        :return: Un diccionario con los datos extraídos.
        """
        json_data = self.fetch_json_from_url(url)
        return self.extract_data(json_data)

    def extract_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Extrae los datos del diccionario JSON según el diccionario de configuración.

        :param data: El diccionario de datos JSON.
        :return: Un diccionario con los datos extraídos.
        """
        results = {}
        for key in self.config.keys():
            results[key] = self.extract_values(data, self.config[key])
        return results

    def save_to_csv(self, data: Dict[str, List[str]]):
        """
        Guarda los datos extraídos en un archivo CSV.

        :param data: Un diccionario con los datos a guardar.
        """
        with open(self.csv_filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            file.seek(0, 2)  # Move to the end of the file to check if it's empty
            if file.tell() == 0:  # If file is empty, write the header
                writer.writerow(data.keys())  # Encabezados de columna
            writer.writerow(data.values())

if __name__ == "__main__":
    config = {
        "product_code": "productData.code",
        "product_name": "productData.name",
        "base_product": "productData.baseProduct",
        "classifications_code": "productData.classifications.code",
        "classifications_name": "productData.classifications.name",
        "features_names": "productData.classifications.features.name",
        "feature_values": "productData.classifications.features.featureValues.value",
        "gallery_images": "galleryImages.imageData.src",
        "cad_url": "productData.cadUrl",
        "order_code": "productData.orderCode",
        "min_order_quantity": "productData.minOrderQuantity",
        "max_order_quantity": "productData.maxOrderQuantity",
        "advantage_text": "productData.advantageText.longText",
        "promotional_text": "productData.promotionalText",
        "documentation_url": "productData.documentations.url",
    }

    

    extractor = WebJsonDataExtractor(config, "csv_name.csv")

    with open('csv_name_data_from.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        aux = 1
        for row in reader:
            if aux > 17338:
                try:
                    code = row['codigo']
                    json_url = "https://web.com/es/es/json/article/"+code+"/"  # Reemplaza con la URL real
                    extracted_data = extractor.process_json(json_url)
                    extractor.save_to_csv(extracted_data)
                except Exception as e:
                    print(str(e))
                    pass
            aux += 1
            
