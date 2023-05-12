import mysql.connector

# establish connection to MySQL database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="admin"
)

# create a cursor object to execute SQL statements
mycursor = mydb.cursor()

# query the table
mycursor.execute("SELECT * FROM emails")
result = mycursor.fetchall()

# print the results
for row in result:
  print(row)


