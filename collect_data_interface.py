import os
import pandas as pd
import datetime

from pandas import DataFrame

from config import DATA_INTERFACES
from utils import return_x_characters, define_status_correspondence, define_countries_correspondence


def collect_data_interface(base_dir, countries, year, month, day):
    """
        Parcourt tous les pays, toutes les data, pour collecter logs &
        errors du jour.
        """
    date = f"{year}{int(month):02d}{int(day):02d}"
    promark_date = f"{year}-{int(month):02d}-{int(day):02d}"
    all_data = []

    for country in countries:
        country_dir = os.path.join(base_dir, country)
        if not os.path.exists(country_dir):
            print(f"⛔ Dossier pays non trouvé: {country_dir}")
            continue

        # Liste des interfaces pour ce pays
        for interface in DATA_INTERFACES.get(country, []):
            interface_dir = os.path.join(country_dir, interface)
            if not os.path.isdir(interface_dir):
                continue

            if country == "CSAS":
                # IN
                in_path = os.path.join(interface_dir, "IN")
                nb_ins = read_file(in_path, date)

                # ERRORS
                errors_path = os.path.join(interface_dir, "ERROR")
                nb_errors = read_file(errors_path, date)

                # ARCHIVES
                archive_path = os.path.join(interface_dir, "ARCHIVE")
                nb_archives = read_file(archive_path, date)

                nb_total = nb_errors + nb_archives + nb_ins

                row = {
                    "Interface": country + "_" + interface,
                    "Pays": define_countries_correspondence(country),
                    "Appli - emmetteur": "SHAREPOINT",
                    "Appli - Recepteur": "S4 Cloud",
                    "Periodicite": "",
                    "Status": define_status_correspondence(nb_total, nb_errors, nb_archives),
                    "Nb OK": nb_archives,
                    "Nb Warning": "",
                    "Nb Kos": nb_errors + nb_ins,
                    "Nb Total": nb_total,
                    "Pourcentage d'intégration": f"{nb_archives / nb_total * 100:.2f} %" if (nb_total>0) else f"{0.00}%",
                    "Commentaire": ""
                }

                all_data.append(row)

            if country == "CSW":
                # IN
                in_path = os.path.join(interface_dir, "IN")
                nb_ins = read_promark_file(in_path, date)

                # ERRORS
                errors_path = os.path.join(interface_dir, "ERROR")
                nb_errors = read_promark_file(errors_path, date)

                # ARCHIVES
                archive_path = os.path.join(interface_dir, "ARCHIVE")
                nb_archives = read_promark_file(archive_path, date)
                
                for file_type in ["SAP140", "SAP220"]:
                    total = nb_ins[file_type] + nb_errors[file_type] + nb_archives[file_type]
                    errors = nb_ins[file_type] + nb_errors[file_type]
                    archives = nb_archives[file_type]

                    row = {
                        "Interface": country + "_" + interface + "_" + file_type,
                        "Pays": define_countries_correspondence(country),
                        "Appli - emmetteur": "Promark",
                        "Appli - Recepteur": "S4 Cloud",
                        "Periodicite": "Daily",
                        "Status": define_status_correspondence(total, errors, archives),
                        "Nb OK": archives,
                        "Nb Warning": "",
                        "Nb Kos": errors,
                        "Nb Total": total,
                        "Pourcentage d'intégration": f"{archives / total * 100:.2f} %" if (
                                    total > 0) else f"{0.00}%",
                        "Commentaire": ""
                    }

                    all_data.append(row)


    if all_data:
        return pd.DataFrame(all_data)
    return pd.DataFrame()


def read_file(path, date) -> int:
    nb_data = 0
    date = f"_{date}_"
    if not os.path.exists(path):
        return nb_data

    file_content = []
    for file in os.listdir(path):
        if file.endswith(".csv") and date in file:
            file_path = os.path.join(path, file)
            try:
                df = pd.read_csv(file_path)
                file_content.append(df)

            except Exception as e:
                print(f"Erreur lecture {file_path}: {e}")

    if file_content:
        combined_df = pd.concat(file_content, ignore_index=True)
        nb_data = combined_df.shape[0]

    return nb_data

def read_promark_file(path, date) -> dict[str, int]:
    nb_data = {
        "SAP140": 0,
        "SAP220": 0
    }

    edit_time = os.path.getmtime(path)
    edit_time = datetime.datetime.fromtimestamp(edit_time)

    if not os.path.exists(path):
        return nb_data

    file_sap140_content = []
    file_sap220_content = []
    for file in os.listdir(path):
        if file.endswith(".txt") and date == str(edit_time.date()):

            file_path = os.path.join(path, file)
            content = produce_data_frame(file_path, file)

            if "SAP140" in file:
                if content is not None:
                    file_sap140_content.append(content)

            if "SAP220" in file:
                if content is not None:
                    file_sap220_content.append(content)

    if file_sap140_content:
        combined_sap140_df = pd.concat(file_sap140_content, ignore_index=True)
        nb_data["SAP140"] = combined_sap140_df.shape[0]

    if file_sap140_content:
        combined_sap220_df = pd.concat(file_sap220_content, ignore_index=True)
        nb_data["SAP220"] = combined_sap220_df.shape[0]

    return nb_data

def produce_data_frame(path, file) -> DataFrame | None:
    file_path = os.path.join(path, file)
    try:
        return pd.read_csv(path, sep=";")

    except Exception as e:
        print(f"Erreur lecture {file_path}: {e}")