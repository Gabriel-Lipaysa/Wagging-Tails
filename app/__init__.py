from flask import Flask
import mysql.connector
import os

class DBHelper:
    @staticmethod
    def get_connection():
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='elec4_endterm'
        )

    @staticmethod
    def query_one(sql, params=()):
        conn = DBHelper.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row

    @staticmethod
    def query_all(sql, params=()):
        conn = DBHelper.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def execute(sql, params=()):
        conn = DBHelper.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return last_id

db = DBHelper

def init_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'your-very-secure-secret-key'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_PORT'] = 3306
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'elec4_endterm'

    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    # Register blueprints
    from app.routes.admin import admin
    from app.routes.user import user
    app.register_blueprint(admin)
    app.register_blueprint(user)
    return app
