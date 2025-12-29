from flask import render_template, session, redirect, flash, url_for, request, Blueprint, jsonify
from app import db
from app.utils.auth import require_role

user = Blueprint('user',__name__)

@user.route('/', methods=['GET', 'POST'])
def show_user_login():

    if session.get('role') == 'user':
        return redirect(url_for('user.user_dashboard'))

    # Validate login form
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.query_one("SELECT * FROM users WHERE email=%s",(email,))

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['role'] = 'user'
            flash('User logged in successfully!', 'success')
            return redirect(url_for('user.user_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/user-login.html')


#User Registration
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

        db.execute('INSERT INTO users(`name`, `username`, `email`, `password`, `role`) VALUES (%s, %s, %s, %s, %s)',params=(name, username, email, password, 'user'))
    
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
    check = require_role('user', 'user.show_user_login', 'user.show_user_login')
    if check:
        return check

    return render_template('user/dashboard.html')

@user.route('/cart/items', methods=['GET'])
def cart_items():
    uid = session.get('user_id')
    if not uid:
        return jsonify([])
    rows = db.query_all("SELECT c.id, c.product_id, p.name, p.price, c.quantity, p.image FROM carts c JOIN products p ON c.product_id = p.id WHERE c.user_id=%s", (uid,))
    return jsonify(rows)

@user.route('/cart/items/update/<int:id>', methods=['POST'])
def cart_items_update(id):
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    new_quantity = request.form.get('quantity')
    db.execute("UPDATE carts SET quantity = %s WHERE id = %s AND user_id = %s", 
               (new_quantity, id, uid))
    return jsonify({'status': 'success', 'new_quantity': new_quantity})

@user.route('/cart/items/remove-selected', methods=['POST'])
def cart_items_remove_selected():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get list of IDs from the AJAX request
    # jQuery sends arrays with '[]' in the key name
    selected_ids = request.form.getlist('selected_items[]')
    
    if not selected_ids:
        return jsonify({'error': 'No items selected'}), 400
    
    # Delete only items belonging to the logged-in user
    for cart_id in selected_ids:
        db.execute("DELETE FROM carts WHERE id = %s AND user_id = %s", (cart_id, uid))
    
    return jsonify({'status': 'success'})