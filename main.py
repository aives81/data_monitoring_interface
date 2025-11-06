import os
import pandas as pd

from config import YEAR, MONTH, BASE_DIR_MONITORING_INTERFACE, BASE_DIR_DATA_INTERFACE, COUNTRIES, LOGO
from collect_monitoring_interface import collect_all_monitoring_data
from collect_data_interface import collect_data_interface
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

def main():
    # Demande le jour à traiter (par défaut aujourd'hui)
    day = input("Jour à consolider (ex: 22) ? ").zfill(2)
    while not day.isdigit() or not (1 <= int(day) <= 31):
        day = input("Jour à consolider (ex: 22) ? ").zfill(2)
    print(f"Consolidation du {YEAR}-{MONTH}-{day}")

    # Collecte globale
    monitoring_df = collect_all_monitoring_data(BASE_DIR_MONITORING_INTERFACE, COUNTRIES, YEAR, MONTH, day)
    data_interface_df = collect_data_interface(BASE_DIR_DATA_INTERFACE, COUNTRIES, YEAR, MONTH, day)

    #if monitoring_df.empty:
    #    print("⛔ Aucune donnée trouvée pour ce jour.")
    #    return

    columns_order = [
        "Interface",
        "Pays",
        "Appli - emmetteur",
        "Appli - Recepteur",
        "Periodicite",
        "Status",
        "Nb OK",
        "Nb Warning",
        "Nb Kos",
        "Nb Total",
        "Pourcentage d'intégration",
        "Commentaire",
    ]

    # Ajoute les colonnes manquantes si besoin
    for col in columns_order:
        if col not in monitoring_df.columns:
            monitoring_df[col] = ""
    monitoring_df = monitoring_df[columns_order]

    # Sauvegarde Excel
    os.makedirs("output", exist_ok=True)
    output_file = f"output/consolidation_{YEAR}_{MONTH}_{day}.xlsx"
    df_merged = pd.concat([monitoring_df, data_interface_df], ignore_index=True)
    df_merged.to_excel(output_file, index=False, startrow=4)

    # === Ouvre le fichier Excel avec openpyxl ===
    wb = load_workbook(output_file)
    ws = wb.active

    # === Ajout du logo ===
    if os.path.exists(LOGO):
        img = Image(LOGO)
        img.width = 180  # redimensionne le logo
        img.height = 90
        ws.add_image(img, "A1")

    # === Ajout du titre centré ===
    titre = f"Global Monitoring of Interfaces on {YEAR}-{MONTH}-{day}"
    ws.merge_cells("C2:H4")  # fusion de cellules pour le titre
    cell = ws["C2"]
    cell.value = titre
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.font = Font(size=18, bold=True)

    # Débute l'écriture dans à la ligne 6 (le compte débute à 0)
    ws.insert_rows(5)

    for column_cells in ws.columns:
        max_length = 0
        column = column_cells[0].column
        column_letter = get_column_letter(column)
        for cell in column_cells:
            try:
                cell_length = len(str(cell.value)) if cell.value else 0
                if cell_length > max_length:
                    max_length = cell_length
            except:
                pass
        ws.column_dimensions[column_letter].width = max_length + 2

    wb.save(output_file)
    print(f"✅ Fichier Excel final enrichi : {output_file}")

if __name__ == "__main__":
    main()
