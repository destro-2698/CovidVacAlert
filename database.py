import psycopg2

#crete a new database named botdb
def createDatabase():
    #establishing the connection
    conn = psycopg2.connect(
        database="postgres", user='postgres', password='admin', host='127.0.0.1', port= '5432'
    )

    conn.autocommit = True

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    #Preparing query to create a database
    sql = '''CREATE database botDB''';

    #Creating a database
    cursor.execute(sql)
    print("Database created successfully........")

    #Closing the connection
    conn.close()

#create a new table
def createTable():
    #Establishing the connection
    conn = psycopg2.connect(
        database="botdb", user='postgres', password='admin', host='127.0.0.1', port= '5432'
    )
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    #Doping EMPLOYEE table if already exists.
    cursor.execute("DROP TABLE IF EXISTS logger")

    #Creating table as per requirement
    sql ='''CREATE TABLE logger(
        id SERIAL PRIMARY KEY,
        log TEXT NOT NULL
    )'''
    cursor.execute(sql)
    conn.commit()
    print("Table created successfully........")

    #Closing the connection
    conn.close()

#main function to run one time to create a database and a table
def main():
    createDatabase()
    createTable

main()