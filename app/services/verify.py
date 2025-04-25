import base64
import re
from fastapi import HTTPException


def verify_structure_password(password: str) -> bool:
    if len(password) < 8:
        return False
    patron = r'(?=.*[A-Z])(?=.*\d)'
    return bool(re.search(patron, password))


def verify_email(email: str) -> bool:
    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.search(patron, email))


def verify_cellphone_number(cellphone: str) -> bool:
    if 10 >= len(cellphone) >= 7:
        patron = r'^\d+$'
        return bool(re.search(patron, cellphone))
    else:
        return False


def verify_hour(hour: str) -> bool:
    patron = r'^([01]?[0-9]|2[0-3]):([0-5]?[0-9])$'
    return bool(re.search(patron, hour))

def verify_location_field(value: str, field_name: str) -> str:
    """
    Verifica si una ciudad o barrio es válido.

    - Solo permite letras y espacios.
    - Debe tener entre 3 y 50 caracteres.

    Retorna el valor limpio si es válido o lanza un error HTTP 400 si no lo es.
    """
    if not (3 <= len(value) <= 50):
        raise HTTPException(status_code=400, detail=f"{field_name} debe tener entre 3 y 50 caracteres.")

    if not re.fullmatch(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$', value):
        raise HTTPException(status_code=400, detail=f"{field_name} solo puede contener letras y espacios.")

    return value  # Devuelve el valor si pasa la validación

def verify_image_size(image_data_str: str, max_size=5 * 1024 * 1024) -> bytes:
    if image_data_str:
        try:
            image_bytes = base64.b64decode(image_data_str)
        except Exception as e:
            raise ValueError(f"Imagen inválida: {str(e)}")

        if len(image_bytes) > max_size:
            raise ValueError("La imagen excede el tamaño máximo permitido.")

        return image_bytes
    return None