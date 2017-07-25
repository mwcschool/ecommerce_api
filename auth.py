from flask_httpauth import HTTPBasicAuth
from models import User
from flask import g
from passlib.hash import pbkdf2_sha256


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

        if g.current_user.status != 'enable':
            return False

        return True

    return False


def crypt_password(password):
    crypt = pbkdf2_sha256.hash(password)

    return crypt
