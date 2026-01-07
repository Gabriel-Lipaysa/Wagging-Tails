import os
import json
import time
from flask import Response
from flask import render_template, session, redirect, flash, url_for, request, Blueprint, jsonify, current_app
from app import db
from app.utils.save_upload import save_upload
from app.utils.auth import require_role
from werkzeug.utils import secure_filename

user = Blueprint('user',__name__)

@user.route('/login/user', methods=['GET', 'POST'])
def show_user_login():

    if session.get('role') == 'user':
        return redirect(url_for('user.home'))

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.query_one("SELECT * FROM users WHERE email=%s", (email,))

        if user and user['password'] == password and user['is_active'] == 1:
            session['user_id'] = user['id']
            session['role'] = 'user'
            session['name'] = user['name'].split().pop(0)
            print(session['name'])
            session['email'] = email
            flash('User logged in successfully!', 'success')
            return redirect(url_for('user.home'))
        else:
            if user and user['is_active'] == 0:
                flash('Your account has been deactivated. Please contact support.', 'danger')
            else:
                flash('Invalid email or password.', 'danger')
            # Important: redirect back to login on failed POST
            return redirect(url_for('user.show_user_login'))

    # GET request — show login form
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

@user.route('/', methods=['GET'])
def home():
        
    uid = session.get('user_id')
    
    query = """
    SELECT p.*, 
    CASE WHEN %s IS NOT NULL AND w.id IS NOT NULL THEN 1 ELSE 0 END as is_wishlisted 
    FROM products p 
    LEFT JOIN wishlists w ON p.id = w.product_id AND w.user_id = %s
    WHERE p.category = %s LIMIT 4"""
    
    dog_products = db.query_all(query, (uid, uid, 'Dog Food'))
    cat_products = db.query_all(query, (uid, uid, 'Cat Food'))

    return render_template('user/home.html',  
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
    mode = request.form.get('mode', 'add')

    if not pid:
        return jsonify({'error': 'Invalid product'}), 400

    product = db.query_one("SELECT quantity FROM products WHERE id = %s", (pid,))
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    available_stock = product['quantity']
    existing = db.query_one("SELECT quantity FROM carts WHERE user_id=%s AND product_id=%s", (uid, pid))
    current_in_cart = existing['quantity'] if existing else 0

    if mode == 'add':
        new_qty = current_in_cart + qty
    else:
        new_qty = qty

    # Clamp to available stock — silently cap it
    if new_qty > available_stock:
        new_qty = available_stock  # Don't go beyond stock

    was_capped = new_qty < (current_in_cart + qty if mode == 'add' else qty)

    # Update cart (upsert)
    if existing:
        db.execute("UPDATE carts SET quantity = %s WHERE user_id = %s AND product_id = %s", 
                   (new_qty, uid, pid))
    else:
        db.execute("INSERT INTO carts (user_id, product_id, quantity) VALUES (%s, %s, %s)", 
                   (uid, pid, new_qty))
    
    return jsonify({
        'status': 'success',
        'new_quantity': new_qty,
        'available_stock': available_stock,
        'max_reached': was_capped  # Tell frontend if we hit the limit
    })

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
def toggle_wishlist(product_id):
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401

    # 1. Check if this product is already in the user's wishlist
    existing = db.query_one("SELECT id FROM wishlists WHERE user_id=%s AND product_id=%s", (uid, product_id))
    
    if existing:
        # 2. If it exists, remove it (Unlike)
        db.execute("DELETE FROM wishlists WHERE id = %s", (existing['id'],))
        return jsonify({'status': 'removed', 'is_wishlisted': False})  # Return updated status
    else:
        # 3. If it doesn't exist, add it (Like)
        db.execute("INSERT INTO wishlists (user_id, product_id) VALUES (%s, %s)", (uid, product_id))
        return jsonify({'status': 'added', 'is_wishlisted': True})  # Return updated status

    
def get_products_by_category(uid, category, limit=12, exclude_id=None):
    params = [uid]
    where_clause = ""
    
    if category and category != 'all' and category != 'All Products':
        where_clause = " WHERE p.category = %s"
        params.append(category)
        
    if exclude_id:
        # If there is already a WHERE clause, use AND; otherwise use WHERE
        where_clause += (" AND " if "WHERE" in where_clause else " WHERE ") + "p.id != %s"
        params.append(exclude_id)

    query = f"""
        SELECT p.*, 
        CASE WHEN w.id IS NOT NULL THEN 1 ELSE 0 END as is_wishlisted 
        FROM products p 
        LEFT JOIN wishlists w ON p.id = w.product_id AND w.user_id = %s
        {where_clause}
        ORDER BY RAND() LIMIT %s
    """
    params.append(limit)
    return db.query_all(query, tuple(params))

@user.route('/product/<int:product_id>', methods=['GET'])
def product_details(product_id):
    uid = session.get('user_id', 0)

    # Main Product
    query_main = """
        SELECT p.*, 
        CASE WHEN w.id IS NOT NULL THEN 1 ELSE 0 END as is_wishlisted 
        FROM products p 
        LEFT JOIN wishlists w ON p.id = w.product_id AND w.user_id = %s
        WHERE p.id = %s
    """
    product = db.query_one(query_main, (uid, product_id))

    if not product:
        return "Product not found", 404

    # Related Products
    query_related = """
        SELECT p.*, 
        CASE WHEN w.id IS NOT NULL THEN 1 ELSE 0 END as is_wishlisted 
        FROM products p 
        LEFT JOIN wishlists w ON p.id = w.product_id AND w.user_id = %s
        WHERE p.category = %s AND p.id != %s
        LIMIT 8
    """
    
    related_products = db.query_all(query_related, (uid, product['category'], product_id))
        
    return render_template('user/products/product_details.html', 
                           product=product, 
                           related_products=related_products)

@user.route('/checkouts', methods=['GET', 'POST'])
def checkouts():
    items_param = request.args.get('items')
    if not items_param:
        return redirect(url_for('user.home'))

    email = session.get('email')
    # Convert "1,2,3" string back into a list [1, 2, 3]
    item_ids = items_param.split(',')
    uid = session.get('user_id')

    # Fetch only the selected cart items with product details
    # Use "WHERE c.id IN (...)" to filter by your list of IDs
    placeholders = ', '.join(['%s'] * len(item_ids))
    query = f"""
        SELECT c.*, p.name, p.price, p.image 
        FROM carts c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.id IN ({placeholders}) AND c.user_id = %s
    """
    selected_products = db.query_all(query, tuple(item_ids + [uid]))

    # Calculate total for the summary
    total_price = sum(item['price'] * item['quantity'] for item in selected_products)

    return render_template('user/products/checkouts.html', 
                           email=email,
                           products=selected_products, 
                           total=total_price)

@user.route('/get_regions')
def get_regions():
    # current_app.root_path points to your main project folder
    base_path = os.path.join(current_app.root_path, 'static', 'js', 'addresses')
    file_path = os.path.join(base_path, 'region.json')
    
    try:
        # Use encoding='utf-8' to handle special characters in names
        with open(file_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        # This helps you debug by showing exactly where it looked
        return jsonify({"error": f"File not found at {file_path}"}), 404

@user.route('/get_provinces')
def get_provinces():
    base_path = os.path.join(current_app.root_path, 'static', 'js', 'addresses')
    file_path = os.path.join(base_path, 'province.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({"error": f"File not found at {file_path}"}), 404

@user.route('/get_cities')
def get_cities():
    base_path = os.path.join(current_app.root_path, 'static', 'js', 'addresses')
    file_path = os.path.join(base_path, 'city.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({"error": f"File not found at {file_path}"}), 404

@user.route('/get_barangays')
def get_barangays():
    base_path = os.path.join(current_app.root_path, 'static', 'js', 'addresses')
    file_path = os.path.join(base_path, 'barangay.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({"error": f"File not found at {file_path}"}), 404
    
@user.route('/process_order', methods=['POST'])
def process_order():
    uid = session.get('user_id')
    if not uid:
        return redirect(url_for('user.show_user_login'))  # Fixed: was 'user.login'

    # Get the specific IDs from the hidden input
    items_param = request.form.get('selected_item_ids')
    if not items_param:
        flash("No items selected for checkout.", "danger")
        return redirect(url_for('user.home'))
    
    item_ids = [int(id) for id in items_param.split(',') if id.isdigit()]

    # Collect Form Data
    payment_method = request.form.get('payment')
    region = request.form.get('region')
    province = request.form.get('province')
    city = request.form.get('city')
    barangay = request.form.get('barangay')
    street = request.form.get('address') 
    postal = request.form.get('postal')

    full_address = f"{street}, Brgy. {barangay}, {city}, {province}, {region} {postal}"
    
    # Handle Proof of Payment Image
    payment_image = request.files.get('image')
    payment_rel_path = 'none'

    if payment_image and payment_image.filename:
        payment_image.seek(0)
        payment_rel_path = save_upload(payment_image, subfolder='payments')
        if not payment_rel_path:
            flash('Invalid payment image file format.', 'danger')
            return redirect(url_for('user.checkouts'))

    # Get Selected Cart Items with product_id and quantity
    placeholders = ', '.join(['%s'] * len(item_ids))
    query = f"""
        SELECT c.product_id, c.quantity, p.price, p.quantity AS stock 
        FROM carts c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.id IN ({placeholders}) AND c.user_id = %s
    """
    cart_items = db.query_all(query, tuple(item_ids + [uid]))
    
    if not cart_items:
        flash("Selected items no longer in cart.", "danger")
        return redirect(url_for('user.home'))
    
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

    try:
        # 1. Insert into 'orders' table
        order_query = """
            INSERT INTO orders (user_id, total_price, payment_method, status, shipping_address, payment_screenshot) 
            VALUES (%s, %s, %s, 'Pending', %s, %s)
        """
        order_id = db.execute(order_query, (uid, total_price, payment_method, full_address, payment_rel_path))

        # 2. Insert into 'order_items' table
        for item in cart_items:
            db.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price) 
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['product_id'], item['quantity'], item['price']))

        # 3. DEDUCT STOCK FROM PRODUCTS
        for item in cart_items:
            product_id = item['product_id']
            ordered_qty = item['quantity']
            current_stock = item['stock']

            if ordered_qty > current_stock:
                raise Exception(f"Not enough stock for product ID {product_id}")

            db.execute("""
                UPDATE products 
                SET quantity = quantity - %s 
                WHERE id = %s
            """, (ordered_qty, product_id))

        # 4. Clear the User's Selected Cart Items
        db.execute(f"DELETE FROM carts WHERE id IN ({placeholders}) AND user_id = %s", 
                   tuple(item_ids + [uid]))

        flash("Order placed successfully! Stock has been updated.", "success")

    except Exception as e:
        # Rollback cleanup
        if payment_rel_path and payment_rel_path != 'none':
            file_disk = os.path.join(current_app.root_path, 'static', payment_rel_path.lstrip('/'))
            if os.path.exists(file_disk):
                os.remove(file_disk)
        
        error_msg = str(e)
        if "Not enough stock" in error_msg:
            flash("Sorry, one or more items no longer have enough stock.", "danger")
        else:
            flash("An error occurred while placing your order. Please try again.", "danger")
        
        print(f"ORDER ERROR: {e}")
        return redirect(url_for('user.home'))

    return redirect(url_for('user.home'))

@user.route('/orders', methods=['GET'])
def order_history():
    uid = session.get('user_id')
    if not uid:
        return redirect(url_for('user.show_user_login'))

    status_filter = request.args.get('status', 'all')

    query = """
        SELECT o.*, o.decline_reason
        FROM orders o
        WHERE o.user_id = %s
    """
    params = [uid]

    if status_filter != 'all':
        query += " AND o.status = %s"
        params.append(status_filter)

    query += " ORDER BY o.created_at DESC"
    orders = db.query_all(query, tuple(params))

    from datetime import datetime
    for order in orders:
        # Format date
        if order['created_at']:
            if isinstance(order['created_at'], str):
                try:
                    dt = datetime.strptime(order['created_at'][:19], '%Y-%m-%d %H:%M:%S')
                except:
                    dt = datetime.strptime(order['created_at'][:10], '%Y-%m-%d')
            else:
                dt = order['created_at']
            order['formatted_date'] = dt.strftime('%B %d, %Y')
        else:
            order['formatted_date'] = 'Unknown'

        # Fetch order items
        order['products_list'] = db.query_all("""
            SELECT oi.quantity, oi.price, p.name, p.image
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order['id'],))

        order['extra_items'] = max(0, len(order['products_list']) - 1)

        # Ensure decline_reason is available
        if order.get('decline_reason') is None:
            order['decline_reason'] = None

    return render_template('user/orders.html', orders=orders)

@user.route('/orders/stream')
def order_stream():
    uid = session.get('user_id')
    if not uid:
        return "", 404

    def event_stream():
        last_seen = {}
        while True:
            orders = db.query_all("""
                SELECT id, status, decline_reason, total_price, created_at 
                FROM orders 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            """, (uid,))

            for order in orders:
                key = order['id']
                current = (order['status'], order['decline_reason'] or '')
                if last_seen.get(key) != current:
                    data = {
                        'id': order['id'],
                        'status': order['status'],
                        'decline_reason': order['decline_reason'],
                        'total_price': float(order['total_price']),
                        'created_at': order['created_at'].strftime('%B %d, %Y') if order['created_at'] else ''
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    last_seen[key] = current

            time.sleep(3)

    return Response(event_stream(), mimetype="text/event-stream")

@user.route('/search')
def search():
    query_text = request.args.get('q', '').strip()
    uid = session.get('user_id')

    if query_text:

        sql = """
            SELECT p.*, 
            CASE WHEN %s IS NOT NULL AND w.id IS NOT NULL THEN 1 ELSE 0 END as is_wishlisted 
            FROM products p 
            LEFT JOIN wishlists w ON p.id = w.product_id AND w.user_id = %s
            WHERE (p.name LIKE %s OR p.category LIKE %s OR p.description LIKE %s) AND p.is_active = 1
        """
        search_term = f"%{query_text}%"
        results = db.query_all(sql, (uid, uid, search_term, search_term, search_term))
    else:
        results = []

    return render_template('user/search.html', products=results, query=query_text)