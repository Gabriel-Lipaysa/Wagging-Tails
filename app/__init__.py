from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import os

mysql = MySQL()  
bcrypt = Bcrypt()

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
        last_id = cursor.lastrowid
        cursor.close()
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
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    mysql.init_app(app)
    bcrypt.init_app(app)

    from app.routes.admin import admin
    from app.routes.user import user
    app.register_blueprint(admin)
    app.register_blueprint(user)
    return app
