from flask_httpauth import HTTPBasicAuth
from models import User
from flask import g


login_manager = HTTPBasicAuth()
login_required = login_manager.login_required


@login_manager.verify_password
def verify_pw(email, password):
    try:
        user = User.get(User.email == email)
    except User.DoesNotExist:
        return False

    if user.verify_password(password):
        g.current_user = user
        return True

    return False
