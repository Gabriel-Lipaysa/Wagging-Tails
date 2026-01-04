from flask import render_template, session, redirect, flash, url_for, request, Blueprint, app, current_app
from app import db
from werkzeug.utils import secure_filename
import os, uuid
from app.utils.auth import require_role
from app.utils.save_upload import save_upload
from app.routes.user import show_user_login

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
        
        admin = db.query_one("SELECT * FROM users WHERE username=%s AND role='admin'", (username,))
        if admin and admin['password'] == password:
            session['user_id'] = admin['id']
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

    return render_template('admin/dashboard.html')

@admin.route('/admin/products', methods=['GET'])
def show_products():
    check = require_role('admin', 'admin.admin_login', 'user.show_user_login')
    if check:
        return check
    
    # Fetch only active products and show the "Low Stock" status for relevant products
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
        db.execute("INSERT INTO products (name, brand ,description, price, quantity, image, category) VALUES (%s,%s,%s,%s,%s,%s,%s)", params=(name, brand, description, price, quantity, rel_path, category))
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

    product = db.query_one("SELECT * FROM products WHERE id=%s", params=(id,))

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
        return redirect(url_for('admin.show_edit_form'))

    if not description:
        flash('Description is required.', 'warning')
        return redirect(url_for('admin.show_edit_form'))
    
    if not brand:
        flash('Brand is required.', 'warning')
        return redirect(url_for('admin.show_edit_form'))
    
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
        db.execute("UPDATE products SET name=%s, brand=%s, description=%s, price=%s, quantity=%s, image=%s, category=%s WHERE id=%s", params=(name, brand, description, price_val, quantity_val, final_image, category, id))
    except Exception as e:
        if new_path:
            try:
                file_disk = os.path.join(current_app.root_path, 'static', new_path)
                if os.path.exists(file_disk):
                    os.remove(file_disk)
            except:
                pass
        flash(f'Could not save product: {e}', 'danger')
        return redirect(url_for('admin.show_edit_form'))
    
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
    
    product = db.query_one("SELECT * FROM products WHERE id=%s", params=(id,))

    if not product:
        flash('Product not found.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    db.execute('DELETE FROM products WHERE id=%s',params=(product['id'],))

    if product.get('image'):
        try:
            old_disk = os.path.join(current_app.root_path, 'static', product['image'])
            if os.path.exists(old_disk):
                os.remove(old_disk)
        except Exception:
            pass
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.show_products'))
