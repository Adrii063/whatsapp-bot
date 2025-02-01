import re
import logging

def extract_reservation_details(message):
    """Extrae fecha, hora y número de personas de un mensaje de reserva"""
    date_match = re.search(r'(\d{1,2}/\d{1,2}|\d{1,2} de [a-zA-Z]+)', message)
    time_match = re.search(r'(\d{1,2}[:h]\d{2}|\d{1,2} (?:AM|PM|am|pm))', message)
    people_match = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

    date_str = date_match.group(0) if date_match else None
    time_str = time_match.group(0) if time_match else None
    people_count = people_match.group(1) if people_match else None

    logging.debug(f"📊 Datos extraídos - Fecha: {date_str}, Hora: {time_str}, Personas: {people_count}")

    return date_str, time_str, people_count