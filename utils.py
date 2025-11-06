import pandas as pd


def get_static_source_and_target_from_interface(interface) -> dict[str, str]:
    interface_source_target = {
        "CSAS_INTERFACE_EXCHANGES_RATES": {"source": "ECB", "target": "S4 Cloud"},
        "CSAS_INTERFACE_WORKFORCE": {"source": "Eurecia", "target": "S4 Cloud"},
        "CSAS_INTERFACE_TIME_RECORDING": {"source": "Eurecia", "target": "S4 Cloud"},
        "CSW_INTERFACE_TIME_RECORDING": {"source": "Promark", "target": "S4 Cloud"},
        "CSW_INTERFACE_ASCENDO_INVOICES": {"source": "InExchange", "target": "S4 Cloud"},
        "CSAS_CSW_Replicate_Project_S4": {"source": "S4 Cloud", "target": "Promark"},
        "CSAS_INTERFACE_TRAVEL_EXPENSE": {"source": "SHAREPOINT", "target": "S4 Cloud"},
        "CSAS_Replicate_BankStatement_S4": {"source": "SHAREPOINT", "target": "S4 Cloud"},
        "CSAS_INTERFACE_PAYROLL": {"source": "SHAREPOINT", "target": "S4 Cloud"}
    }

    return interface_source_target.get(interface, {})


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
    if nb_total == 0:
        return "No file uploaded"
    else:
        if nb_total == nb_ok:
            return correspondence["0"]
        elif nb_total == nb_kos:
            return correspondence["1"]
        elif nb_kos > 0 and nb_ok > 0:
            return correspondence["2"]
        return ""


def return_x_characters(s: str, x: int) -> str:
    """
    Retourne les x premiers caractères d'une chaîne.
    """
    if pd.isnull(s):
        return ""
    return str(s)[:x]