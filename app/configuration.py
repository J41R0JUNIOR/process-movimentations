from enum import Enum

class FOLDERS(str, Enum):
    INPUT_FOLDER = "data/input/sources"
    OUTPUT_FOLDER = "data/output"  
   
class FILES(str, Enum):
    MONTHLY_CHART_FILE = FOLDERS.OUTPUT_FOLDER + "/graphs/values_by_month.png"
    MONTHLY_CASHFLOW_CHART_FILE = FOLDERS.OUTPUT_FOLDER + "/graphs/monthly_cashflow.png"
    PRODUCT_EXPENSES_CHART_FILE = FOLDERS.OUTPUT_FOLDER + "/graphs/expenses_by_product.png"
    CATEGORY_EXPENSES_CHART_FILE = FOLDERS.OUTPUT_FOLDER + "/graphs/expenses_by_category.png"
    TRANSACTION_ACTIVITY_CHART_FILE = FOLDERS.OUTPUT_FOLDER + "/graphs/transaction_activity.png"
    WEEKDAY_EXPENSES_CHART_FILE = FOLDERS.OUTPUT_FOLDER + "/graphs/expenses_by_weekday.png"
    DATABASE_FILE = "data/database/financial.db"