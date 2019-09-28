from functools import wraps
from flask import session, request, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print('user id is: ')
        print(session.get('user_id'))
        if session.get('user_id') is None:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function