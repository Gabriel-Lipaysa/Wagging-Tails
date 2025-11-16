from flask import render_template, session, redirect, flash, url_for, request, Blueprint
from app import db, bcrypt
from app.forms import UserLoginForm, UserRegisterForm

# ------------------------------------------------------------
# USER LOGIN
# ------------------------------------------------------------
user = Blueprint('user',__name__)

@user.route('/login', methods=['GET', 'POST'])
def show_user_login():

    if session.get('role') == 'user':
        return redirect(url_for('user.user_dashboard'))

    # Validate login form
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.query_one("SELECT * FROM users WHERE email=%s",(email,))

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = 'user'
            flash('User logged in successfully!', 'success')
            return redirect(url_for('user.user_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/user-login.html')


# ------------------------------------------------------------
# USER REGISTRATION
# ------------------------------------------------------------
@user.route('/signup', methods=['GET', 'POST'])
def show_user_signup():

    if session.get('role') == 'user':
        return redirect(url_for('user.user_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name').strip()
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()
        confirm_password = request.form.get('confirm_password').strip()

        if not name:
            flash('Name is required.', 'warning')
            return redirect(url_for('user.show_user_signup'))
        
        if not username:
            flash('Name is required.', 'warning')
            return redirect(url_for('user.show_user_signup'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('user.show_user_signup'))

        existing_user = db.query_one('SELECT * FROM users WHERE email=%s', params=(email,))

        if existing_user:
            flash('Username or email already exists.', 'warning')
            return redirect(url_for('user.show_user_signup'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        db.execute('INSERT INTO users(`name`, `username`, `email`, `password`, `role`) VALUES (%s, %s, %s, %s, %s)',params=(name, username, email, hashed_pw, 'user'))
    
        user = db.query_one('SELECT id FROM users WHERE email=%s', (email,))
        print(user)

        session['user_id'] = user['id']
        session['role'] = 'user'

        flash('Registration successful! Welcome to Wagging Wonders.', 'success')
        return redirect(url_for('user.user_dashboard'))

    return render_template('auth/user-signup.html')

@user.route('/user/logout')
def user_logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user.show_user_login'))

@user.route('/user/dashboard')
def user_dashboard():
    if not session.get('user_id'):
        flash('Please log in first.', 'warning')
        return redirect(url_for('user.show_user_login'))

    if session.get('role') != 'user':
        flash('Access denied. Users only.', 'danger')
        return redirect(url_for('user.show_user_login'))

    return render_template('user/dashboard.html')
