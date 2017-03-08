## -*- coding: utf-8 -*-

from app import app, mail
from flask import g, flash, session, redirect, url_for, abort, render_template
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
import requests, json, re, sqlalchemy
from wtforms import widgets, validators, DecimalField
from functools import wraps
from authAPI import authAPI

def errorMessage(msg):
    return flash(str(msg), ('error','Error'))

def successMessage(msg):
    return flash(str(msg), ('success','Success'))

def apiMessage(msg):
    if 'error' in msg:
        return flash(str(msg['error']), ('error','error'))
    if 'success' in msg:
        return flash(str(msg['success']), ('success','success'))

# SendMail
def sendMail(subject, sender, recipients, text_body, html_body):
    mesg = Message(subject, sender=sender, recipients=recipients)
    mesg.body = text_body
    mesg.html = html_body
    mail.send(mesg)

# Select2 widget
class select2Widget(widgets.Select):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', u'select2')

        allow_blank = getattr(field, 'allow_blank', False)
        if allow_blank and not self.multiple:
            kwargs['data-allow-blank'] = u'1'

        return super(select2Widget, self).__call__(field, **kwargs)

# Select2 multiple widget
class select2MultipleWidget(widgets.Select):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', u'select2')
        allow_blank = getattr(field, 'allow_blank', False)
        if allow_blank and not self.multiple:
            kwargs['data-allow-blank'] = u'1'

        return super(select2MultipleWidget, self).__call__(field, multiple = True, **kwargs)

#def getRoles():
#    req = authAPI(endpoint='getRoles', method='post', token=session['token'])
#    if 'error' in req:
#        return False
#    else:
#        return req['roles']

# flask view decorators
def requiredRole(*roleList):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not 'token' in session:
                errorMessage('Please log in to view content')
                return redirect(url_for('authBP.loginView'))
            roles = session['roles']
            if roles:
                if not any([i in roleList[0] for i in roles]):
                    errorMessage('You are not authorized to access this content')
                    return redirect(url_for('indexView'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def loginRequired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'token' in session:
            errorMessage('Please log in to view content')
            return redirect(url_for('authBP.loginView'))
        req = authAPI(endpoint='checkPassword', method='post', token=session['token'])
        if 'error' in req:
            errorMessage('Please log in to view content')
            return redirect(url_for('authBP.loginView'))
        return f(*args, **kwargs)
    return decorated_function

class FlexibleDecimalField(DecimalField):
    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", ".")
        return super(FlexibleDecimalField, self).process_formdata(valuelist)
