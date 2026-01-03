from flask import current_app
from werkzeug.utils import secure_filename
import os, uuid

def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def save_upload(file_storage, subfolder='products'):
    if file_storage and allowed(file_storage.filename):
        # Reset the file pointer to the start
        file_storage.seek(0) 
        
        filename = secure_filename(file_storage.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        new_name = f"{uuid.uuid4().hex}.{ext}"
        
        physical_path = os.path.join(current_app.root_path, 'static', 'uploads', subfolder)
        os.makedirs(physical_path, exist_ok=True)
        
        full_save_path = os.path.join(physical_path, new_name)
        
        # Save the file
        file_storage.save(full_save_path)
        
        # Double-check if file exists on disk immediately after saving
        if not os.path.exists(full_save_path):
            print(f"CRITICAL: File was NOT saved to {full_save_path}")
            return None
        
        print(full_save_path)
        db_path = os.path.join('uploads', subfolder, new_name).replace('\\', '/')
        return db_path
    return None