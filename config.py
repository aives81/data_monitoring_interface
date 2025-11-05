import os
from dotenv import load_dotenv

load_dotenv()

LOGO = os.getenv("LOGO_PATH", "")
YEAR = os.getenv("YEAR")
MONTH = os.getenv("MONTH_TO_CONSOLIDATE")
BASE_DIR_MONITORING_INTERFACE = os.getenv("BASE_DIR_MONITORING_INTERFACE")

# Les "pays" à traiter
COUNTRIES = os.getenv("COUNTRIES", "CSAS,CSW").split(",")

# Les interfaces de monitoring par pays
MONITORING_INTERFACES = {
    "CSAS": os.getenv("CSAS_MONITORING_INTERFACES", "").split(","),
    "CSW": os.getenv("CSW_MONITORING_INTERFACES", "").split(",")
}
