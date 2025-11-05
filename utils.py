import pandas as pd

def define_countries_correspondence(country_code):
    """
    Définit la correspondance entre le code pays et son nom complet.
    """
    correspondence = {
        "CSAS": "France",
        "CSW": "Suède"
    }
    return correspondence.get(country_code, "Unknown Country")


def define_status_correspondence(nb_total, nb_kos, nb_ok) -> str:
    """
    Définit la correspondance entre le code status et son libellé.
    """
    correspondence = {
        "0": "COMPLETED",
        "1": "ERROR",
        "2": "COMPLETED WITH ERRORS"
    }
    if nb_total == nb_ok:
        return correspondence["0"]
    elif nb_total == nb_kos:
        return correspondence["1"]
    elif nb_kos > 0 and nb_ok > 0:
        return correspondence["2"]
    else:
        return "No file uploaded"


def return_x_characters(s: str, x: int) -> str:
    """
    Retourne les x premiers caractères d'une chaîne.
    """
    if pd.isnull(s):
        return ""
    return str(s)[:x]