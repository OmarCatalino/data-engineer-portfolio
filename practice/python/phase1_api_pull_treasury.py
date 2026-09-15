import requests
import pandas as pd
import sqlite3

params = {"page[size]":20, "sort": "-record_date"}
response = requests.get("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny", params=params)
print(response.status_code)
print(response.json()["data"])

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

debt_penny = response.json()["data"]
df = pd.DataFrame(debt_penny)
print(df.shape)
print(df.columns.tolist())

df = df[["debt_held_public_amt", "intragov_hold_amt", "tot_pub_debt_out_amt", "record_date"]]
print(df)

df["record_date"] = pd.to_datetime(df["record_date"], format="mixed")

amount_columns = ["debt_held_public_amt", "intragov_hold_amt", "tot_pub_debt_out_amt"]

for col in amount_columns:
    df[col] = df[col].str.replace(",", "", regex=False)
    df[col] = pd.to_numeric(df[col], errors="coerce")


connection = sqlite3.connect("gov_debt_penny.db")
df.to_sql("gov_debt_penny", connection, if_exists="replace", index=False)

check = pd.read_sql("SELECT * FROM gov_debt_penny", connection)
print(check)