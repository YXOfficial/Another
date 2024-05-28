import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Khoa12345@"
)

print(mydb)