from enum import Enum

class FOLDERS(str, Enum):
    INPUT_FOLDER = "data/input"
    OUTPUT_FOLDER = "data/output"  
   
class NAMES(str, Enum):
    VALUES_BY_MONTH = "values_by_month"

class FILES(str, Enum):
    VALUES_BY_MONTH_FILE = FOLDERS.OUTPUT_FOLDER + "/values/" + NAMES.VALUES_BY_MONTH.value + ".json"
    MONTHLY_CHART_FILE = FOLDERS.OUTPUT_FOLDER + "/graphs/" + NAMES.VALUES_BY_MONTH.value + ".png"
    RAW_DATA_FILE = FOLDERS.OUTPUT_FOLDER + "/values/transactions.json"
    CLEANED_DATA_FILE = FOLDERS.OUTPUT_FOLDER + "/values/cleaned_transactions.json"
    MONTHLY_VALUES_FILE = FOLDERS.OUTPUT_FOLDER + "/values/" + NAMES.VALUES_BY_MONTH.value + ".json"