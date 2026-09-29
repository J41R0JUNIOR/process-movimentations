from enum import Enum


class Configuration(str, Enum):
    INPUT_FOLDER = "data/input"
    RAW_DATA_FILE = "data/output/transactions.json"
    GROUPED_TRANSACTIONS_FILE = "data/output/grouped_transactions.json"
    MONTHLY_VALUES_FILE = "data/output/values_by_month.json"
    MONTHLY_CHART_FILE = "data/output/values_by_month.png"
    GROUPING_FIELD = "description"
    GROUP_TRANSACTIONS = "group_transactions"
    VALUES_BY_MONTH = "values_by_month"


class CleanupConfiguration(str, Enum):
    CLEANED_DATA_FILE = "data/output/cleaned_transactions.json"
    CLEAN_TRANSACTIONS = "clean_transactions"
    SAVINGS_APPLICATION = "Aplicação RDB"
    SAVINGS_REDEMPTION = "Resgate RDB"
