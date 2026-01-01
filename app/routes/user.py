from flask import render_template, session, redirect, flash, url_for, request, Blueprint, jsonify
from app import db
from app.utils.auth import require_role

user = Blueprint('user',__name__)

@user.route('/', methods=['GET', 'POST'])
def show_user_login():

    if session.get('role') == 'user':
        return redirect(url_for('user.home'))

    # Validate login form
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.query_one("SELECT * FROM users WHERE email=%s",(email,))

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['role'] = 'user'
            flash('User logged in successfully!', 'success')
            return redirect(url_for('user.hone'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/user-login.html')


#User Registration
@user.route('/signup', methods=['GET', 'POST'])
def show_user_signup():

    if session.get('role') == 'user':
        return redirect(url_for('user.home'))

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
        return redirect(url_for('user.home'))

    return render_template('auth/user-signup.html')

@user.route('/user/logout', methods=['GET'])
def user_logout(): 
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user.show_user_login'))

@user.route('/home', methods=['GET'])
def home():
    check = require_role('user', 'user.show_user_login', 'user.show_user_login')
    if check:
        return check
        
    uid = session.get('user_id')

    query = """
        SELECT p.*, 
        CASE WHEN w.id IS NOT NULL THEN 1 ELSE 0 END as is_wishlisted 
        FROM products p 
        LEFT JOIN wishlists w ON p.id = w.product_id AND w.user_id = %s
        WHERE p.category = %s LIMIT 3
    """

    dog_products = db.query_all(query, (uid, 'Dog Food'))
    cat_products = db.query_all(query, (uid, 'Cat Food'))
    all_products = db.query_all("SELECT * FROM products") 

    return render_template('user/home.html', 
                           all_p=all_products, 
                           dog_p=dog_products, 
                           cat_p=cat_products)

@user.route('/products/<category>', methods=['GET'])
@user.route('/products', defaults={'category': 'all'}, methods=['GET'])
def product_listing(category):
    uid = session.get('user_id', 0)
    page = request.args.get('page', 1, type=int)
    per_page = 12 # Show more on the full page
    offset = (page - 1) * per_page

    # Base Query
    query = """
        SELECT p.*, 
        CASE WHEN w.id IS NOT NULL THEN 1 ELSE 0 END as is_wishlisted 
        FROM products p 
        LEFT JOIN wishlists w ON p.id = w.product_id AND w.user_id = %s
    """
    
    # Filter logic
    params = [uid]
    if category != 'all':
        query += " WHERE p.category = %s"
        params.append(category)
    else:
        category = "All Products"
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    products = db.query_all(query, tuple(params))
    
    return render_template('user/products/products.html', 
                           products=products, 
                           current_category=category)



@user.route('/cart/items', methods=['GET'])
def cart_items():
    uid = session.get('user_id')
    if not uid:
        return jsonify([])
    rows = db.query_all("SELECT c.id, c.product_id, p.name, p.price, c.quantity, p.image FROM carts c JOIN products p ON c.product_id = p.id WHERE c.user_id=%s", (uid,))
    return jsonify(rows)

@user.route('/cart/items/upsert', methods=['POST'])
def cart_items_upsert():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error': 'Please login first'}), 401
    
    pid = request.form.get('product_id')
    qty = int(request.form.get('quantity', 1))
    mode = request.form.get('mode') # 'add' or 'set'

    # Check if this item is already in the user's cart
    existing = db.query_one("SELECT id, quantity FROM carts WHERE user_id=%s AND product_id=%s", (uid, pid))

    if existing:
        if mode == 'add':
            new_qty = existing['quantity'] + qty
        else: # mode is 'set'
            new_qty = qty
        db.execute("UPDATE carts SET quantity = %s WHERE id = %s", (new_qty, existing['id']))
    else:
        # If item doesn't exist, we ignore 'mode' and just create it
        db.execute("INSERT INTO carts (user_id, product_id, quantity) VALUES (%s, %s, %s)", (uid, pid, qty))
    
    return jsonify({'status': 'success'})

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

@user.route('/wishlist/items', methods=['GET'])
def get_wishlist_items():
    uid = session.get('user_id')
    if not uid:
        return jsonify([])

    # Join products with wishlists to get product details
    items = db.query_all("""
        SELECT p.id as product_id, p.name, p.price, p.image 
        FROM products p
        JOIN wishlists w ON p.id = w.product_id
        WHERE w.user_id = %s
    """, (uid,))
    
    return jsonify(items)

@user.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
def toggle_wishlist(product_id): # The ID comes from the URL, not the form
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    # 1. Check if this product is already in the user's wishlist
    # (Note: Use your 'wishlists' table, not 'carts')
    existing = db.query_one("SELECT id FROM wishlists WHERE user_id=%s AND product_id=%s", (uid, product_id))
    
    if existing:
        # 2. If it exists, remove it (Unlike)
        db.execute("DELETE FROM wishlists WHERE id = %s", (existing['id'],))
        return jsonify({'status': 'removed'})
    else:
        # 3. If it doesn't exist, add it (Like)
        db.execute("INSERT INTO wishlists (user_id, product_id) VALUES (%s, %s)", (uid, product_id))
        return jsonify({'status': 'added'})