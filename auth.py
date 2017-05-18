from flask_httpauth import HTTPBasicAuth
from models import User

login_manager = HTTPBasicAuth()
login_required = login_manager.login_required


@login_manager.verify_password
def verify_pw(email, password):
    try:
        user = User.get(User.email == email)
    except User.DoesNotExist:
        return False

    return user.verify_password(password)
