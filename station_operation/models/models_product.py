# import pyodbc




#
# cnxn1 = pyodbc.connect(
#     'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-H7EA1N4;DATABASE=center;Trusted_Connection=yes;')




def sql_run2(sql):
    cursor = cnxn1.cursor()
    cursor.execute(sql)
    cursor.commit()
    cursor.close()
