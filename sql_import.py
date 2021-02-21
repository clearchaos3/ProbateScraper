import pandas as pd
import mariadb
import sys
from dotenv import load_dotenv
import os

load_dotenv()
host = os.environ.get("host")
user = os.environ.get("user")
password = os.environ.get("password")

data = pd.read_csv('probatesScraped.csv',index_col=False)
data.fillna('', inplace=True)

try:
    conn = mariadb.connect(host=host, user=user, password=password)
    cursor = conn.cursor()
    print("MySQL Connection -  OK.")
except mariadb.Error as e:
    print("Error while connecting to MySQL", e)
    sys.exit(1)

cursor.execute("TRUNCATE TABLE EFlatHomes.ProbateCombined;")
print("Table Truncated")
conn.commit()

for i,row in data.iterrows():
	sql1 = "INSERT INTO EFlatHomes.ProbateCombined VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	cursor.execute(sql1, tuple(row))
	conn.commit()

print("Records inserted")
