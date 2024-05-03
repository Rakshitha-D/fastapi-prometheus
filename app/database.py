import psycopg2
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI,HTTPException,status

class Connection():
    try:
        conn = psycopg2.connect(host='postgres',port='5432',database='obsrv',user='obsrv_user',password='obsrv123',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was succesfull")
    except Exception as error:
        print("Failed to connect Database")
        print("Error: ",error)

connection = Connection()