import os
import pandas as pd
from config import MONITORING_INTERFACES
from utils import return_x_characters, define_status_correspondence, define_countries_correspondence, get_static_source_and_target_from_interface


def collect_all_monitoring_data(base_dir, countries, year, month, day):
    """
    Parcourt tous les pays, toutes les interfaces, pour collecter logs &
    errors du jour.
    """
    all_data = []
    all_errors = []
    for country in countries:
        country_dir = os.path.join(base_dir, country)
        if not os.path.exists(country_dir):
            print(f"⛔ Dossier pays non trouvé: {country_dir}")
            continue

        # Liste des interfaces pour ce pays
        for interface in MONITORING_INTERFACES.get(country, []):
            interface_dir = os.path.join(country_dir, interface)
            if not os.path.isdir(interface_dir):
                continue

            # ERRORS
            errors_path = os.path.join(interface_dir, "ERROR", year, month, day)
            errors = read_csvs_error_in_dir(errors_path, country, interface)
            all_errors.extend(errors)

            # LOGS
            logs_path = os.path.join(interface_dir, "LOG", year, month, day)
            logs = read_csvs_in_dir(logs_path, country, interface, all_errors)
            all_data.extend(logs)

    if all_data:
        return pd.DataFrame(all_data)
    return pd.DataFrame()


def read_csvs_in_dir(path, country, interface, errors):
    """
    Lit tous les fichiers CSV d'un dossier, ajoute pays, interface,
    type à chaque ligne.
    """
    data = []
    if not os.path.exists(path):
        source_target = get_static_source_and_target_from_interface(country + "_" + interface)
        row = {
            "Interface": country + "_" + interface,
            "Pays": define_countries_correspondence(country),
            "Appli - emmetteur": source_target["source"],
            "Appli - Recepteur": source_target["target"],
            "Periodicite": "Daily",
            "Status": "The interface didn't run",
            "Nb OK": "",
            "Nb Warning": "",
            "Nb Kos": "",
            "Nb Total": "",
            "Pourcentage d'intégration": f"{""} %",
            "Commentaire": "",
            "Fichier Source": ""
        }
        data.append(row)
        return data

    file_content = []
    for file in os.listdir(path):
        if file.endswith(".csv"):
            file_path = os.path.join(path, file)
            try:
                df = pd.read_csv(file_path)
                file_content.append(df)

            except Exception as e:
                print(f"Erreur lecture {file_path}: {e}")

    if file_content:
        combined_df = pd.concat(file_content, ignore_index=True)
        nb_total = combined_df.shape[0]

        mask_ok = combined_df["STATUS"].apply(lambda s: return_x_characters(s, 3) == "COM" or return_x_characters(s, 3) == "")
        nb_ok = combined_df[mask_ok].shape[0]
        mask_warn = combined_df["STATUS"].apply(lambda s: return_x_characters(s, 3) == "WAR")
        nb_warn = combined_df[mask_warn].shape[0]
        mask_ko = combined_df["STATUS"].apply(lambda s: return_x_characters(s, 3) == "ERR")
        nb_kos = combined_df[mask_ko].shape[0]

        #Recuperation des messages d'erreurs se trouvant dans le fichier de log
        error_messages = ""
        if nb_kos > 0:
        #taille = len(errors)
        #if len(errors) == 0:
            err_mask = combined_df["STATUS"].apply(lambda s: return_x_characters(s, 3) == "ERR")
            error_messages = "\n".join(combined_df.loc[err_mask, "STATUS"].astype(str))

        pourcentage = round(nb_ok / nb_total * 100, 2) if nb_total > 0 else 0

        status = define_status_correspondence(nb_total, nb_kos, nb_ok)

        #Recupération des erreurs se trouvant dans les fichiers d'erreurs
        errors_from_error_file = get_error_messages_from_errors_and_interface(errors, interface)

        row = {
            "Interface": country + "_" + interface,
            "Pays": define_countries_correspondence(country),
            "Appli - emmetteur": combined_df["SOURCE"].iloc[0],
            "Appli - Recepteur": combined_df["TARGET"].iloc[0],
            "Periodicite": "Daily",
            "Status": status,
            "Nb OK": nb_ok,
            "Nb Warning": nb_warn,
            "Nb Kos": nb_kos,
            "Nb Total": nb_total,
            "Pourcentage d'intégration": f"{pourcentage} %",
            "Commentaire": "",
            #"Commentaire": define_comment_content(error_messages, errors_from_error_file),
            "Fichier Source": ", ".join([f for f in os.listdir(path) if f.endswith(".csv")])
        }
        data.append(row)

    return data


def define_comment_content(error_in_log, error_in_error_file) -> str :
    """
    Regroupement des messages d'erreurs des fichiers d'erreurs et des fichiers de logs
    """
    content = ""
    if len(error_in_log) > 0:
        content += error_in_log + "\n"
    if len(error_in_error_file) > 0:
        content += error_in_error_file + "\n"
    if len(error_in_log) == 0 and len(error_in_error_file) == 0:
        content = "N/A"

    return content

def read_csvs_error_in_dir(path, country, interface):
    """
    Lit tous les fichiers CSV d'erreurd'un dossier, ajoute pays, interface, type à chaque ligne.
    """
    errors = []
    if not os.path.exists(path):
        row = {
            "Interface": interface,
            "Pays": define_countries_correspondence(country),
            "ERROR_MESSAGE": "",
            "Fichier Source": ""
        }
        errors.append(row)
        return errors

    file_content = []
    for file in os.listdir(path):
        if file.endswith(".csv"):
            file_path = os.path.join(path, file)
            try:
                df = pd.read_csv(file_path)
                file_content.append(df)

            except Exception as e:
                print(f"Erreur lecture {file_path}: {e}")

    if file_content:
        combined_df = pd.concat(file_content, ignore_index=True)

        row = {
            "Interface": interface,
            "Pays": define_countries_correspondence(country),
            "ERROR_MESSAGE": combined_df["ERROR_MESSAGE"].tolist(),
            "Fichier Source": ", ".join([f for f in os.listdir(path) if f.endswith(".csv")])
        }
        errors.append(row)

    return errors


def get_error_messages_from_errors_and_interface(errors, interface):
    """
    Récupère les messages d'erreur pour une interface donnée.
    """
    messages = []
    for error in errors:
        if error["Interface"] == interface:
            messages.extend(error["ERROR_MESSAGE"])
    return "\n".join(messages)
