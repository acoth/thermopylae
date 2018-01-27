import sqlite3

file_name = 'temp_db.sqlite'
temp_table = 'temps'

db = sqlite3.connect(file_name)
c = db.cursor()

c.execute('CREATE TABLE temps (time integer, water_temp real, air_temp real)')
db.commit()

db.close()
