#!/usr/bin/env python
# hvpapp/views/extra.py

from flask import Blueprint, render_template, url_for
from sqlalchemy import inspect, MetaData,Table
from sqlalchemy.engine import reflection
from app.models import engine  #views/__init__.py

extra = Blueprint('extra',__name__)

@extra.route('/tables')
def tables():
    #
    #insp = reflection.Inspector.from_engine(engine)
    metadata = MetaData()
    #metadata.reflect(bind=engine)
    ponderato_table = Table('hvp_movimentos_ponderato', metadata,
                            autoload=True, autoload_with=engine)
    
    #insp = reflection.Inspector.from_engine(engine)
    #insp.reflecttable(ponderato_table, None)
    print( inspect(ponderato_table))
    return str(ponderato_table.metadata)
    
    
@extra.route('/views')
def views():
    #
    insp = reflection.Inspector.from_engine(engine)
    
    return  ', '.join(insp.get_view_names()) 
