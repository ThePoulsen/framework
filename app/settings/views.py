## -*- coding: utf-8 -*-

from flask import Blueprint, render_template, url_for, g, request, redirect, session, json
from app.admin.services import requiredRole, loginRequired, errorMessage, successMessage
from app import db
from forms import companyForm, contactForm
from authAPI import authAPI
from app.crud.tenantCRUD import getCurrentTenant, putTenant
from app.crud.userCRUD import getUsers, getContactPerson, removeContactPerson, addContactPerson, putUser, getUser
from app.sijax.handler import SijaxHandler
import flask_sijax, sys

settingsBP = Blueprint('settingsBP', __name__, template_folder='templates')

@flask_sijax.route(settingsBP, '/company')
@requiredRole([u'Administrator'])
@loginRequired
def companyView():

    kwargs = {'title':'Company information',
              'formWidth':'350'}
    compForm = companyForm()

    if g.sijax.is_sijax_request:
        g.sijax.register_object(SijaxHandler)
        return g.sijax.process_request()

    tenant = getCurrentTenant()
    kwargs['tenant']=tenant
    contact = getContactPerson()
    if 'error' in contact:
        contact = {'uuid':'',
                   'contactName':None,
                   'email':None,
                   'phone':None}
        errorMessage('Please assign contact person')
    else:
        contact=contact['success']
    kwargs['contact']=contact

    compForm = companyForm(regNo=tenant[u'regNo'],
                       companyName=tenant[u'name'],
                       addr=tenant[u'addr'],
                       addr2=tenant[u'addr2'],
                       postcode=tenant[u'postcode'],
                       city=tenant[u'city'])

    contForm = contactForm(contactName= contact['uuid'],
                           email=contact['email'],
                           phone=contact['phone'])

    users = [(str(r['uuid']),str(r['name']+' - '+r['email'])) for r in getUsers()['users']]
    users.insert(0,('',''))
    contForm.contactName.choices = users
    return render_template('settings/newCompanyView.html', contactForm=contForm,
                                                           companyForm=compForm,
                                                           **kwargs)
