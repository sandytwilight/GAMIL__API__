
import mysql.connector

# set up MySQL connection
cnx = mysql.connector.connect(user='root', password='',
                              host='localhost',
                              database='admin')
cursor = cnx.cursor()

# execute SELECT statement to retrieve data from the database
query = "SELECT * FROM emails"
cursor.execute(query)

# print the data to the console
for (id, subject, sender, date, body) in cursor:
    print(f"Email ID: {id}")
    print(f"Subject: {subject}")
    print(f"Sender: {sender}")
    print(f"Date: {date}")
    print(f"Body: {body}")

# close MySQL connection
cursor.close()
cnx.close()




