import pandas as pd

df = pd.read_csv("data/leads_messy.csv")

print(df.head())
print(df.info())
print(df.isnull().sum())

# 1. new line — normalize company names first
df["company_name"] = df["company_name"].str.strip().str.lower().str.title()

df["industry"] = df["industry"].str.strip().str.lower().str.title()
df["status"] = df["status"].str.strip().str.lower().str.title()

df["signup_date"] = pd.to_datetime(df["signup_date"], format="mixed")

df["employee_count"] = df["employee_count"].str.replace(",", "", regex=False)
df["employee_count"] = pd.to_numeric(df["employee_count"], errors="coerce")

print(df["industry"].unique())
print(df["status"].unique())
print(df["employee_count"].dtype)
print(df["signup_date"].dtype)


# 2. replaces your old df.drop_duplicates() line
df = df.sort_values("contact_email").drop_duplicates(subset="company_name", keep="last")

# 3. new lines — just a sanity check, safe to add
counts = df["company_name"].value_counts()
assert (counts == 1).all(), counts[counts > 1]

df.to_csv("data/cleaned_data.csv", index=False)