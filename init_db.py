import pandas as pd
import sqlite3


df= pd.DataFrame()

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
df.to_sql("database", conn)

cursor.execute("INSERT INTO posts (title, namrr,age) VALUES (?, ?,?)",
            ('title1', 'ss',22)
            )

cursor.execute("INSERT INTO posts (title, namrr,age) VALUES (?, ?,?)",
            ('title2', 'ss2',23)
            )

conn.commit()
conn.close()



for i in cursor:
    print(i)
