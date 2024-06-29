import json
import logging
import os
from typing import Generator

from pydantic import ValidationError
from schemas import WindowBoundsSchema, BusSchema

from functools import wraps
import trio
import trio_websocket
from wsproto.utilities import LocalProtocolError

logger = logging.getLogger(__name__)


def generate_bus_id(route_id, bus_index) -> str:
    return f"{route_id}-{bus_index}"


def load_routes(directory_path="routes") -> Generator[str, None, None]:
    """Загружает маршруты автобусов из папки с маршрутами.

    Маршруты это json файл определенного формата
    """
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, "r", encoding="utf8") as file:
                yield json.load(file)


def configure_logger(logger_name: str, verbose: int = 0):
    """Настройка логгера."""
    logger_ = logging.getLogger(logger_name)
    if verbose > 1:
        logging_level = logging.DEBUG
    elif verbose == 1:
        logging_level = logging.INFO
    else:
        logging_level = logging.NOTSET

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level)
    formatter = logging.Formatter(f"%(levelname)s:%(module)s:%(asctime)s:%(message)s")
    console_handler.setFormatter(formatter)

    logger_.setLevel(logging_level)
    logger_.addHandler(console_handler)


def relaunch_on_disconnect(timeout: int):
    """Декоратор для переподключения к серверу через определенный timeout."""

    def decorator(async_function):
        @wraps(async_function)
        async def wrapper(*args, **kwargs):
            while True:
                try:
                    await async_function(*args, **kwargs)
                except* trio_websocket.ConnectionClosed as e:
                    logger.critical("Пропало соединение WebSocket")
                except* trio_websocket.HandshakeError as e:
                    logger.info("Не удалось соединиться с сервером")
                except* LocalProtocolError as e:
                    logger.info("Не удалось соединиться с браузером")
                logger.info(f"Попытка переподключения через: {timeout} сек")
                await trio.sleep(timeout)

        return wrapper

    return decorator


def validate_new_bounds(msg: str) -> tuple[WindowBoundsSchema | None, str | None]:
    try:
        received_bounds = WindowBoundsSchema.model_validate_json(msg)
    except ValidationError as e:
        logger.error(f"Невалидное сообщение границ окна Браузера: {e}")
        error_msg = {"msgType": "Errors", "errors": e.errors()}
        return None, json.dumps(error_msg)

    return received_bounds, None


def validate_bus_position(msg: str) -> tuple[BusSchema | None, str | None]:
    try:
        bus_position = BusSchema.model_validate_json(msg)
    except ValidationError as e:
        logger.error(f"Невалидное сообщение границ окна Браузера: {e}")
        error_msg = {"msgType": "Errors", "errors": e.errors()}
        return None, json.dumps(error_msg)

    return bus_position, None
