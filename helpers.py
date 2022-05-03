import json
import os


def generate_bus_id(route_id, bus_index):
    return f"{route_id}-{bus_index}"


def load_routes(directory_path='routes'):
    """Загружает маршруты автобусов из папки с маршрутами.

    Маршруты это json файл определенного формата
    """
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf8') as file:
                yield json.load(file)
