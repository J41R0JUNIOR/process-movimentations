from enum import Enum

class FOLDERS(str, Enum):
    INPUT_FOLDER = "data/input/sources"
    OUTPUT_FOLDER = "data/output"  
   
class FILES(str, Enum):
    MONTHLY_CHART_FILE = FOLDERS.OUTPUT_FOLDER + "/graphs/values_by_month.png"
    DATABASE_FILE = "data/database/financial.db"