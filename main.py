import os
from config import YEAR, MONTH, BASE_DIR_MONITORING_INTERFACE, COUNTRIES, LOGO
from collect import collect_all_monitoring_data
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
from openpyxl.styles import Alignment


def main():
    # Demande le jour à traiter (par défaut aujourd'hui)
    day = input("Jour à consolider (ex: 22) ? ").zfill(2)
    while not day.isdigit() or not (1 <= int(day) <= 31):
        day = input("Jour à consolider (ex: 22) ? ").zfill(2)
    print(f"Consolidation du {YEAR}-{MONTH}-{day}")

    # Collecte globale
    df = collect_all_monitoring_data(BASE_DIR_MONITORING_INTERFACE, COUNTRIES, YEAR, MONTH, day)
    if df.empty:
        print("⛔ Aucune donnée trouvée pour ce jour.")
        return

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
        if col not in df.columns:
            df[col] = ""
    df = df[columns_order]

    # Sauvegarde Excel
    os.makedirs("output", exist_ok=True)
    output_file = f"output/consolidation_{YEAR}_{MONTH}_{day}.xlsx"
    df.to_excel(output_file, index=False, startrow=4)

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
    titre = f"Consolidation Monitoring - {YEAR}-{MONTH}-{day}"
    ws.merge_cells("C1:H2")  # fusion de cellules pour le titre
    cell = ws["C1"]
    cell.value = titre
    cell.alignment = Alignment(horizontal="center", vertical="center")
    #cell.font = Font(size=16, bold=True)

    # === Décale les données vers le bas (pour ne pas écraser le logo/titre) ===
    # (Optionnel si tu veux que le tableau commence plus bas)
    ws.insert_rows(5)

    wb.save(output_file)
    print(f"✅ Fichier Excel final enrichi : {output_file}")

if __name__ == "__main__":
    main()
