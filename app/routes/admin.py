from flask import render_template, session, redirect, flash, url_for, request, Blueprint, app, current_app
from app import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os, uuid
from app.utils.auth import require_role
from app.utils.save_upload import save_upload
from app.routes.user import show_user_login
from datetime import datetime

admin = Blueprint('admin', __name__)

def validate(str, msg, path):
    if not str:
        flash(msg,'warning')
        return 

@admin.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    if session.get('role') == 'admin':
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = db.query_one("SELECT * FROM users WHERE username=%s AND role='admin' AND is_active=1", (username,))
        if admin and admin['password'] == password:
            session['user_id'] = admin['id']
            session['username'] = admin['username']
            session['role'] = admin['role']
            flash('Admin logged in successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials. Please try again.', 'danger')
            return redirect(url_for('admin.admin_login'))

    return render_template('auth/admin-login.html')

@admin.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin.admin_login'))

@admin.route('/admin/dashboard')
def dashboard():
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check

    total_users = (db.query_one(
        "SELECT COUNT(*) as count FROM users WHERE role='user' AND is_active=1"
    ) or {'count': 0})['count']

    inactive_users = (db.query_one(
        "SELECT COUNT(*) as count FROM users WHERE role='user' AND is_active=0"
    ) or {'count': 0})['count']

    total_products = (db.query_one(
        "SELECT COUNT(*) as count FROM products WHERE is_active=1"
    ) or {'count': 0})['count']

    pending_orders = (db.query_one(
        "SELECT COUNT(*) as count FROM orders WHERE status='Pending'"
    ) or {'count': 0})['count']

    return render_template('admin/dashboard.html', 
                         total_users=total_users, 
                         inactive_users=inactive_users,
                         total_products=total_products,
                         pending_orders=pending_orders)


@admin.route('/admin/users', methods=['GET'])
def show_users():
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check
    
    current_admin_id = session.get('user_id')
    users = db.query_all("""
        SELECT id, name, username, email, is_active, created_at 
        FROM users 
        WHERE role='user' AND id != %s 
        ORDER BY created_at DESC
    """, (current_admin_id,))

    for user in users:
        if user['created_at']:
            if isinstance(user['created_at'], str):

                try:
                    dt = datetime.strptime(user['created_at'][:19], '%Y-%m-%d %H:%M:%S')
                except:
                    dt = datetime.strptime(user['created_at'][:10], '%Y-%m-%d')
            else:
                dt = user['created_at']
            user['joined_date'] = dt.strftime('%b %d, %Y')  # e.g., Jan 07, 2026
        else:
            user['joined_date'] = 'Unknown'

    now = datetime.now()
    last_updated = now.strftime('%b %d, %Y %I:%M %p')

    return render_template('admin/users/index.html', users=users, last_updated=last_updated)

@admin.route('/admin/users/<int:id>/reset-password', methods=['POST'])
def reset_user_password(id):
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check
    
    user = db.query_one("SELECT * FROM users WHERE id=%s AND role='user'", (id,))
    if not user:
        flash('User not found.', 'warning')
        return redirect(url_for('admin.show_users'))
    
    # Ginawa lang naming simple, para mas maalala ng users. Possible output is = Password123_LOW (username = lowes). 
    
    default_password = f"Password123_{user['username'][:3].upper()}"
    
    try:
        hashed_password = generate_password_hash(default_password)
        db.execute("UPDATE users SET password=%s, updated_at=NOW() WHERE id=%s", 
                  (hashed_password, id))
        
        flash(f'Password reset successfully for {user["name"]}. New password: {default_password}', 'success')
        
    except Exception as e:
        flash(f'Error resetting password: {str(e)}', 'danger')
    
    return redirect(url_for('admin.show_users'))

@admin.route('/admin/users/<int:id>/toggle-status', methods=['POST'])
def toggle_user_status(id):
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check
    
    user = db.query_one("SELECT * FROM users WHERE id=%s AND role='user'", (id,))
    if not user:
        flash('User not found.', 'warning')
        return redirect(url_for('admin.show_users'))
    
    # if status ni user is 1 then user is activated, if 0 deactivated.

    current_status = user['is_active']
    new_status = 0 if current_status == 1 else 1
    status_text = 'activated' if new_status == 1 else 'deactivated'
    
    try:
        db.execute("UPDATE users SET is_active=%s, updated_at=NOW() WHERE id=%s", 
                  (new_status, id))
        
        flash(f'User {user["name"]} ({user["username"]}) has been {status_text} successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating user status: {str(e)}', 'danger')
    
    return redirect(url_for('admin.show_users'))

@admin.route('/admin/products', methods=['GET'])
def show_products():
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check

    dogFoods = db.query_all("SELECT * FROM products WHERE category='Dog Food' AND is_active=1")
    catFoods = db.query_all("SELECT * FROM products WHERE category='Cat Food' AND is_active=1")

    return render_template('admin/products/index.html', dogFoods=dogFoods, catFoods=catFoods)

@admin.route('/admin/products/create', methods=['GET'])
def show_create_form():
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check

    return render_template('admin/products/create.html')

@admin.route('/admin/products/store', methods=['POST'])
def store_product():
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check
    
    category = request.form.get('category')
    name = request.form.get('name').strip()
    brand = request.form.get('brand').strip()
    description = request.form.get('description').strip()
    price = request.form.get('price')
    quantity = request.form.get('quantity')

    if not name:
        flash('Name is required.', 'warning')
        return redirect(url_for('admin.show_create_form'))

    if not description:
        flash('Description is required.', 'warning')
        return redirect(url_for('admin.show_create_form'))
    
    if not brand:
        flash('Brand is required.', 'warning')
        return redirect(url_for('admin.show_create_form'))
    
    image = request.files.get('image')
    rel_path = None
    if image and image.filename:
        rel_path = save_upload(image)
        if not rel_path:
            flash('Invalid image file', 'danger')
            return redirect(url_for('admin.show_create_form'))
    
    try:
        db.execute("INSERT INTO products (name, brand ,description, price, quantity, image, category, is_active) VALUES (%s,%s,%s,%s,%s,%s,%s,1)", 
                  (name, brand, description, price, quantity, rel_path, category))
        db.session.commit()
        
    except Exception as e:
        if rel_path:
            try:
                file_disk = os.path.join(current_app.root_path, 'static', rel_path)
                if os.path.exists(file_disk):
                    os.remove(file_disk)
            except:
                pass
        flash(f'Could not save product: {e}', 'danger')
        return redirect(url_for('admin.show_create_form'))
    
    flash('Product added successfully.', 'success')
    return redirect(url_for('admin.show_products'))

@admin.route('/admin/products/edit/<int:id>', methods=['GET'])
def show_edit_form(id):
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check

    product = db.query_one("SELECT * FROM products WHERE id=%s", (id,))

    if not product:
        flash('Product not found.', 'warning')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/products/edit.html', product=product)

@admin.route('/admin/products/update/<int:id>', methods=['POST'])
def update_product(id):
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check
    
    product = db.query_one("SELECT * FROM products WHERE id=%s", (id,))
    if not product:
        flash('Product not found.', 'warning')
        return redirect(url_for('admin.show_products'))
    
    category = request.form.get('category')
    name = request.form.get('name').strip()
    brand = request.form.get('brand').strip()
    description = request.form.get('description').strip()
    price = request.form.get('price')
    quantity = request.form.get('quantity')

    if not name:
        flash('Name is required.', 'warning')
        return redirect(url_for('admin.show_edit_form', id=id))

    if not description:
        flash('Description is required.', 'warning')
        return redirect(url_for('admin.show_edit_form', id=id))
    
    if not brand:
        flash('Brand is required.', 'warning')
        return redirect(url_for('admin.show_edit_form', id=id))
    
    try:
        price_val = round(float(price), 2)
        quantity_val = int(quantity)
        if price_val <= 0 or quantity_val < 0:
            raise ValueError
    except Exception:
        flash('Invalid price or quantity.', 'danger')
        return redirect(url_for('admin.show_edit_form', id=id))
    
    image = request.files.get('image')
    new_path = None
    replace = False
    try:
        if image and image.filename:
            new_path = save_upload(image)
            if not new_path:
                flash('Invalid image file', 'danger')
                return redirect(url_for('admin.show_edit_form', id=id))
            replace = True
    except Exception as e:
        flash(f'Error saving uploaded image: {e}', 'danger')
        return redirect(url_for('admin.show_edit_form', id=id))

    final_image = new_path if new_path else product.get('image')

    try:
        db.execute("UPDATE products SET name=%s, brand=%s, description=%s, price=%s, quantity=%s, image=%s, category=%s, updated_at=NOW() WHERE id=%s", 
                  (name, brand, description, price_val, quantity_val, final_image, category, id))
        db.session.commit()
        
    except Exception as e:
        if new_path:
            try:
                file_disk = os.path.join(current_app.root_path, 'static', new_path)
                if os.path.exists(file_disk):
                    os.remove(file_disk)
            except:
                pass
        flash(f'Could not save product: {e}', 'danger')
        return redirect(url_for('admin.show_edit_form', id=id))
    
    if replace and product.get('image'):
        try:
            old_disk = os.path.join(current_app.root_path, 'static', product['image'])
            if os.path.exists(old_disk):
                os.remove(old_disk)
        except Exception:
            pass

    flash('Product updated successfully.', 'success')
    return redirect(url_for('admin.show_products'))

@admin.route('/admin/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check
    
    product = db.query_one("SELECT * FROM products WHERE id=%s", (id,))

    if not product:
        flash('Product not found.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    try:
        db.execute('UPDATE products SET is_active=0, updated_at=NOW() WHERE id=%s', (id,))
        db.session.commit()
        
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'danger')
    
    return redirect(url_for('admin.show_products'))

@admin.route('/admin/orders', methods=['GET'])
def show_orders():
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check
    
    status_filter = request.args.get('status', 'all')
    
    query = """
        SELECT 
            o.id, 
            o.user_id, 
            u.name AS customer_name, 
            u.username,
            u.email,
            o.total_price,
            o.payment_method,
            o.status, 
            o.shipping_address,
            o.payment_screenshot,
            o.decline_reason,
            o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.id
    """
    params = []
    
    if status_filter and status_filter != 'all':
        if status_filter == 'in_progress':
            query += " WHERE o.status IN ('Shipped', 'On Delivery')"
        elif status_filter == 'Declined':
            query += " WHERE o.status = 'Declined'"
        else:
            query += " WHERE o.status = %s"
            params.append(status_filter)
    
    query += " ORDER BY o.created_at DESC"
    orders = db.query_all(query, tuple(params) if params else ())
    
    for order in orders:
        if order['created_at']:
            if isinstance(order['created_at'], str):
                dt = datetime.strptime(order['created_at'][:19], '%Y-%m-%d %H:%M:%S')
            else:
                dt = order['created_at']
            order['formatted_date'] = dt.strftime('%B %d, %Y')
        else:
            order['formatted_date'] = 'Unknown'

        # Fetch order items (products_list) to match user side
        order['products_list'] = db.query_all("""
            SELECT oi.quantity, oi.price, p.name, p.image
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order['id'],))

        order['extra_items'] = max(0, len(order['products_list']) - 1)

    return render_template('admin/orders/index.html', orders=orders)


@admin.route('/admin/orders/<int:id>/update-status', methods=['POST'])
def update_order_status(id):
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check
    
    new_status = request.form.get('status')
    valid_statuses = ['Shipped', 'On Delivery', 'Delivered']
    
    if new_status not in valid_statuses:
        flash('Invalid status selected.', 'danger')
        return redirect(url_for('admin.show_orders'))
    
    try:
        db.execute(
            "UPDATE orders SET status=%s, updated_at=NOW() WHERE id=%s",
            (new_status, id)
        )
        
        flash(f'Order #{id} status updated to "{new_status}"', 'success')
        
        db.execute("""
            INSERT INTO admin_logs (admin_id, action, details, created_at) 
            VALUES (%s, 'update_order_status', %s, NOW())
        """, (session['user_id'], f'Order #{id} → {new_status}'))
        
    except Exception as e:
        flash(f'Error updating order status: {str(e)}', 'danger')
    
    return redirect(url_for('admin.show_orders'))


@admin.route('/admin/orders/<int:id>/decline', methods=['POST'])
def decline_order(id):
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check
    
    reason = request.form.get('decline_reason', '').strip()
    if not reason:
        flash('Please provide a reason for declining the order.', 'warning')
        return redirect(url_for('admin.show_orders'))
    
    try:
        db.execute("""
            UPDATE orders 
            SET status='Declined', updated_at=NOW(), decline_reason=%s 
            WHERE id=%s
        """, (reason, id))
        
        flash('Order declined successfully.', 'success')
        
        db.execute("""
            INSERT INTO admin_logs (admin_id, action, details, created_at) 
            VALUES (%s, 'decline_order', %s, NOW())
        """, (session['user_id'], f'Order #{id} declined: {reason}'))
        
    except Exception as e:
        flash(f'Error declining order: {str(e)}', 'danger')
    
    return redirect(url_for('admin.show_orders'))

@admin.route('/admin/orders/<int:id>', methods=['GET'])
def view_order(id):
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check

    order = db.query_one("""
        SELECT o.*, u.name AS customer_name, u.email 
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.id=%s
    """, (id,))
    
    if not order:
        flash('Order not found.', 'warning')
        return redirect(url_for('admin.show_orders'))
    
    items = db.query_all("""
        SELECT oi.*, p.name AS product_name, p.image
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id=%s
    """, (id,))
    

    if order['created_at']:
        dt = order['created_at'] if not isinstance(order['created_at'], str) else datetime.strptime(order['created_at'], '%Y-%m-%d %H:%M:%S')
        order['formatted_date'] = dt.strftime('%b %d, %Y %I:%M %p')
    
    return render_template('admin/orders/view.html', order=order, items=items)