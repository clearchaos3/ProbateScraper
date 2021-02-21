# Module Imports
import mariadb
import sys
import pandas as pd
From dotenv import load_dotenv
load_dotenv()
import os

host = os.environ.get("host")
user = os.environ.get("user")
password = os.environ.get("password")

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user=user,
        password=password,
        host=host,
        port=3306,
        database="EFlatHomes"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

cur.callproc("ProbateLeadsGet")

result = cur.fetchall()

df = pd.DataFrame(result)
df.to_csv('filteredList.csv',index=False)

cur.close()
conn.close()
