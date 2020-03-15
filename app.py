#!/usr/bin/env python
#
from datetime import date
from datetime import datetime

from flask import Flask, g, session, request, url_for

from flask_session import Session

#from flask_debugtoolbar import DebugToolbarExtension

#from flask_sqlalchemy import SQLAlchemy

#from SQLAlchemy import create_engine, MetaData, text

from views.home import home
#from views.extra import extra
#from .views.conception import conception
#from .views.implementation import implementation
from views.vegetables import vegetables
#from views.acquisition import acquisition
from views.transaction import transaction
from helper import helper
from momentjs import momentjs


app = Flask(__name__, instance_relative_config = True)
#app.config.from_object('config')
app.config.from_pyfile('config.py')
app.secret_key = 'verysecret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['TEMPLATE_DATE_FORMAT '] = 'dd.mm.YY'
#toolbar = DebugToolbarExtension(app)


app.register_blueprint(home)

app.register_blueprint(helper)

#app.register_blueprint(extra, url_prefix='/extra')

#app.register_blueprint(conception, url_prefix='/conception')

#app.register_blueprint(implementation, url_prefix='/implementation')


app.register_blueprint(vegetables, url_prefix='/veggie')


#app.register_blueprint(acquisition, url_prefix='/acquisition')

app.register_blueprint(transaction, url_prefix='/transaction')


@app.route('/halloworld')
def hello_world():
    return 'Hallo, World!'


#JINJA2 FILTER
def pg_date(date_string):
    """ formates a raw postgres date string to show in templates
    pg_format default is:'YY-mm-dd' / date.isoformat()
    TODO using a glogal TEMPLATE_DATE_FORMAT eg:['dd.mm.Y']
    if u know the format at app creation time then u like :D
    ps. there is a better solution
    (regex)
    """
    #l = [int(s) for s in date_string.split('-')]
    
    d = date(*[int(s) for s in date_string.split('-')])
    
    return d.strftime('%d.%m.%Y')

app.jinja_env.filters['pgdate'] = pg_date

#miguelgrinberg
app.jinja_env.globals['momentjs'] = momentjs


"""
############################################################
@app.before_request
def before_request():
    g.db = db.create_engine

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

############################################################
# url_prefix generell http://fraction_id/cultivation_year


@app.url_defaults
def add_fraction_id(endpoint, values):
    if 'fraction_id' in values  or  not g.fraction_id:
        return
    if app.url_map.is_endpoint_expecting(endpoint, 'fraction_id'):
        values['fraction_id'] = g.fraction_id

@app.url_value_preprocessor
def pull_fraction_id(endpoint, values):
    g.fraction_id = values.pop('fraction_id', 2)
    
@app.url_defaults
def add_cultivation_year(endpoint, values):
    if 'cultivation_year' in values  or  not g.cultivation_year:
        return
    if app.url_map.is_endpoint_expecting(endpoint, 'cultivation_year'):
        values['cultivation_year'] = g.cultivation_year

@app.url_value_preprocessor
def pull_cultivation_year(endpoint, values):
    g.cultivation_year = values.pop('cultivation_year', 2015)
"""
# g.cultivation_year = 2015   
# g.fraction_id = 2
############################################################
