import pandas as pd

df = pd.read_csv("data/leads_messy.csv")

print(df.head())
print(df.info())
print(df.isnull().sum())

# 1. new line — normalize company names first
df["company_name"] = df["company_name"].str.strip().str.lower().str.title()

# 2. replaces your old df.drop_duplicates() line
df = df.sort_values("contact_email").drop_duplicates(subset="company_name", keep="last")

# 3. new lines — just a sanity check, safe to add
counts = df["company_name"].value_counts()
assert (counts == 1).all(), counts[counts > 1]