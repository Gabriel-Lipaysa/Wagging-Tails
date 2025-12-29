from flask import session, redirect, url_for, flash

def require_role(expected_role, login_endpoint, role_endpoint):
    if not session.get('user_id'):
        flash("Please log in first.", "warning")
        return redirect(url_for(login_endpoint))

    if session.get('role') != expected_role:
        flash("Access denied. {} only.".format(expected_role.title()), "danger")
        return redirect(url_for(role_endpoint))

    return None