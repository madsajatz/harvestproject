#!/usr/bin/env python
# app/views/acquisition
"""
DEPRECATED see transaction.py
this.blueprint 
"""
from datetime import date
from datetime import datetime
from flask import Blueprint, render_template, g, session, url_for, redirect, request, flash, abort
from app.forms import Acquisition_Retraction_Form
#from sqlalchemy.engine import reflection
#from . import engine  #views/__init__.py
from app.models import FractionModel
from app.models import ProductModel
from app.models import UnitModel
from app.models import BoxModel
from app.models import VehicleModel
from app.models import TransactionModel

acquisition = Blueprint('acquisition',__name__)



@acquisition.route('/<int:fraction_id>')
def onepack(fraction_id):
    
    fraction = FractionModel(fraction_id)
    
    if request.args.get('productgroup',''):
        session['productgroup']= request.args.get('productgroup','')
    
    
    return render_template('acquisition/acquisition.html', fraction=fraction)

@acquisition.route('/<int:fraction_id>/source/<int:source_fraction_id>',methods=["GET"])
def twopack(fraction_id, source_fraction_id):
    # init fractions
    fraction = FractionModel(fraction_id)
    source_fraction = FractionModel(source_fraction_id)
    transactions = TransactionModel(fraction_id,source_fraction_id)
    
    #get all transactions for the actuall date
    if 'acquiredate' in session:
        print('acquiredateInSession:',session['acquiredate'][0])
        trdata = transactions.get_simple(date=session['acquiredate'][0])
        #trdata = False
    else:
        trdata = False
    #get last inputs    
    history_entries = transactions.acqusitions_get_last(12)
        
    # track productgroup
    if request.args.get('productgroup',''):
        session['productgroup']= request.args.get('productgroup','')

    
    
    return render_template('acquisition/acquisition.html',
                           fraction=fraction,
                           source_fraction=source_fraction,
                           history_entries=history_entries,
                           transactions= trdata)


@acquisition.route('/<int:fraction_id>/source/<int:source_fraction_id>/product/<int:product_id>',
                   methods=['GET','POST'])
def getsome(fraction_id, source_fraction_id, product_id):
    """ GET ready to fire a POST to the acquisitions table
    the flow is: from source_fraction to fraction
    WHAT happens IF fraction_id is to drive the boxes and units,
    like DEPOT wants to have 264' boxes in Pounds of a product???
    
    """
    #init destination fractions
    fraction = FractionModel(fraction_id)
    #init source fraction
    source_fraction = FractionModel(source_fraction_id)
    #init one product
    product = ProductModel(product_id, source_fraction_id)
    #dict of product spec data (one db row)
    product_entries = product.get_data()
    #init units
    unit = UnitModel(product_entries['unit_set_id'])
    #init boxes
    box = BoxModel(product_entries['boxes_set_id'])
    #init vehicles
    vehicle = VehicleModel()
    #transactionmodel
    transactions = TransactionModel(fraction_id,source_fraction_id)
    #the latest entries in acquisitions table
    #TODO variable count
    history_entries = transactions.acqusitions_get_last(12)    
    
    form = Acquisition_Retraction_Form()
    if 'acquiredate' in session:
        form.aq_date.raw_data = session['acquiredate']    
    #before validating wtf choises (<option>) must be given 
    
    form.unit_id.choices = unit.get_wtform_choices()
    
    form.vehicle_id.choices = vehicle.get_wtform_choices()
    
    form.box_id.choices = box.get_wtform_choices()
    
    #with boxes we css-style <options> in the template (render_kw?)
    boxset = box.get_set_by_id(product_entries['boxes_set_id'])

    form.alternate_unit_id.choices = unit.get_wtform_choices()
    
    if form.validate_on_submit():
        session['acquiredate'] = form.aq_date.raw_data
        
        res = transactions.acqusition_insert(form)
        print(">>>>>>>>>aqcuisition_insert_result: "+ str(res))
        if res:
            flash(u'Die Angaben und Werte wurden erfolgreich übernommen und gespeichert.','success')
        
            
            
            return redirect(url_for('.getsome', fraction_id=fraction_id,
                     source_fraction_id=source_fraction_id,
                     product_id=product_id))
        else:
            abort(500)

    
    
    #manualy set wtform.data preselected

    
    form.fraction_id.data = fraction.fraction_id
    form.source_fraction_id.data = source_fraction.fraction_id
    form.product_id.data = product_entries['product_id']
    form.unit_id.data = product_entries['unit_pivot_id']
    form.box_id.data = product_entries['box_pivot_id']
    form.box_count.data = 0
    form.vehicle_count.data =0
    

    return render_template('acquisition/acquisition.html',
                           fraction=fraction,
                           source_fraction=source_fraction,
                           product_entries=product_entries,
                           boxset=boxset,
                           history_entries=history_entries,
                           form=form)
    

@acquisition.route('/',methods=["GET"])
def index():
    return render_template('acquisition/index.html')

@acquisition.route('/delete/<int:fraction_id>/<string:timestamp>/next/<path:next_url>',methods=["GET"])
def delete(fraction_id,timestamp,next_url):
    
    tmodel = TransactionModel(fraction_id)
    
    if tmodel.acqusitions_delete(timestamp):
        flash('Eintrag erfolgreich gelöscht','success')
    else:
        flash('Konnte nicht gelöscht werden','alert')
    return redirect(next_url)
        



