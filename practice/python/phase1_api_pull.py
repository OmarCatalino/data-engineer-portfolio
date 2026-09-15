import requests
import pandas as pd
import sqlite3

response = requests.get("https://api.github.com/users/OmarCatalino/repos")
print(response.status_code)
print(response.json()[0])

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

repos = response.json()
df = pd.DataFrame(repos)
print(df.shape)
print(df.columns.tolist())

df = df[["name", "description", "language", "size", "stargazers_count", "created_at", "updated_at", "visibility"]]
print(df)

connection = sqlite3.connect("github_repos.db")
df.to_sql("github_repos", connection, if_exists="replace", index=False)

check = pd.read_sql("SELECT * FROM github_repos", connection)
print(check)