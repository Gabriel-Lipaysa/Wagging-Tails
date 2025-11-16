from flask import current_app
from app import mysql

class DBHelper:
    @staticmethod
    def query_one(sql, params=()):
        cursor = mysql.connection.cursor()
        cursor.execute(sql,params)
        row = cursor.fetchone()
        cursor.close()
        return row

    @staticmethod
    def query_all(sql, params=()):
        cur = mysql.connection.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return rows
    
    @staticmethod
    def execute(sql, params=()):
        cursor = mysql.connection.cursor()
        cursor.execute(sql, params)
        mysql.connection.commit()
        cursor.close()