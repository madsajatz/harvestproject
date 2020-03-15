#!/usr/bin/env python
# app/views/transaction

from datetime import date
from datetime import datetime
from flask import Blueprint, render_template, g, session, url_for, redirect, request, flash, abort
from flask import jsonify
from forms import Acquisition_Retraction_Form
#from sqlalchemy.engine import reflection
#from . import engine  #views/__init__.py
from models import FractionModel
from models import ProductModel
from models import UnitModel
from models import BoxModel
from models import VehicleModel
from models import TransactionModel

transaction = Blueprint('transaction',__name__)
"""Amounts of products are moved between fractions
   amount is the result of am implementation_id of a fraction
   postgres foreign key constraint to array(bigint)
   Array of Permalink  eg. [site/fraction/77/imp_id/2431,site/fraction/77/imp_id/2437]
   although fraction goes subdomain specifc, maybe a fraction_key and a key
   on a nameconvention  predict_implementation(fraction_key,product_id,date)
                    OR  predict_implementation(fraction_key,unreferred_FK)
   is stronger then a permalink.                         
---
session:
session['acquiredate'] a postgres.date string(%Y-%m-%d) eg. '2017-12-20'
(go's with browserdatepicker,WTForms, and Postgres)
"""


@transaction.route('/')
def index():  
    """ """
    tr= TransactionModel()
    sqldump = tr.index('100')
    #print(sqldump)
    das = {'item_name': 'Blumenkohl', 'unit_name': 'kg', 'fraction_id': 3, 'source_fraction_id': 2, 'product_id': 131000, 'unit_id': 1, 'netto': 36, 'retour': 9}
    avgs = das
    #avgs = (zip(*sqldump))
    #print(avgs)
    return jsonify(avgs)
    
    #return render_template('transaction/index.html', avgs=avgs)


@transaction.route('/<int:fraction_id>/productgroup/<int:productgroup>')
def set_group(fraction_id, productgroup):
    session['productgroup'] = productgroup
    return redirect(url_for('.index', fraction_id = fraction_id)) 

@transaction.route('/<int:fraction_id>/product/<int:product_id>')
def product(fraction_id, product_id):
    
    fraction = FractionModel(fraction_id)
    transactions = TransactionModel(fraction_id)
    
    return render_template('transtest.html',fraction=fraction,
                           transactions=transactions,
                           product_id=product_id)
  
#################################################################
#
#ACQUISITION Part
#
#################################################################
@transaction.route('/acquire/',methods=["GET"])
def acquire_index():
    return render_template('transaction/acquire_index.html')

#---------------------------------------------------------------------------#
@transaction.route('/acquire/<int:fraction_id>')
def acquire_onepack(fraction_id):
    
    fraction = FractionModel(fraction_id)
    
    if request.args.get('productgroup',''):
        session['productgroup']= request.args.get('productgroup','')
    
    print(str('calling acquire_onepack'))
    return render_template('transaction/acquisition.html', fraction=fraction)
#---------------------------------------------------------------------------#
@transaction.route('/acquire/<int:fraction_id>/source/<int:source_fraction_id>',methods=["GET"])
def acquire_twopack(fraction_id, source_fraction_id):
    #print('acquire_twopack'+str(fraction_id)+'/'+str(source_fraction_id))
    fraction = FractionModel(fraction_id)
    source_fraction = FractionModel(source_fraction_id)
    transactions = TransactionModel(fraction_id,source_fraction_id)
    
    #get all transactions for the actuall date
    if 'acquiredate' in session:
        #print('ACQIREacquiredateInSession:',(session.get('acquiredate')))
        trdata = transactions.get_simple(date=session.get('acquiredate'))
        #trdata = False
    else:
        trdata = False
    #get last inputs    
    history_entries = transactions.acqusitions_get_last_inserts(12)
        
    # track productgroup
    if request.args.get('productgroup',''):
        session['productgroup']= request.args.get('productgroup','')

    
    
    return render_template('transaction/acquisition.html',
                           fraction=fraction,
                           source_fraction=source_fraction,
                           history_entries=history_entries,
                           transactions= trdata)

#---------------------------------------------------------------------------#
@transaction.route('/acquire/<int:fraction_id>/source/<int:source_fraction_id>/product/<int:product_id>',
                   methods=['GET','POST'])
def acquire_getsome(fraction_id, source_fraction_id, product_id):
    """ GET ready to fire a POST to the acquisitions table
    the flow is: from source_fraction to fraction
    
    WHAT happens IF fraction_id is to drive the boxes and units,
    like DEPOT wants to have 264' boxes in Pounds of a product???
    
    """
    #init destination fractions
    fraction = FractionModel(fraction_id)
    #init source fraction
    source_fraction = FractionModel(source_fraction_id)

    product = ProductModel(product_id, source_fraction_id)
    #dict of product spec data (one db row)
    product_entries = product.get_data()
    unit = UnitModel(product_entries['unit_set_id'])
    box = BoxModel(product_entries['boxes_set_id'])
    vehicle = VehicleModel()
    transactions = TransactionModel(fraction_id, source_fraction_id)
    #the latest entries in acquisitions table
    #TODO variable count
    history_entries = transactions.acqusitions_get_last_inserts(12)    
    
    form = Acquisition_Retraction_Form()
    #print('dateFORMAT:'+str(form.aq_date.format))
    #print('Session::acquiredate:'+str(session.get('acquiredate')))
    
        
        #form.aq_date.data = session.get('acquiredate')
        
    #before validating wtf choises (<option>) must be given 
    form.unit_id.choices = unit.get_wtform_choices()
    form.vehicle_id.choices = vehicle.get_wtform_choices()
    form.box_id.choices = box.get_wtform_choices()

    #with boxes we css-style <options> in the template (render_kw?)
    boxset = box.get_set_by_id(product_entries['boxes_set_id'])

    form.alternate_unit_id.choices = unit.get_wtform_choices()
    
    if form.validate_on_submit():
        session['acquiredate'] = str(form.aq_date.data)
        
        #print('form-data:'+str(form.aq_date.data))
        #print('sessionACQUIREdate:'+str(session.get('acquiredate')))
        
        result = transactions.acqusition_insert(form)
        
        #print('>>>>>>>>>aqcuisition_insert_result: '+ str(result))
        if type(result) is str:
            flash(result, 'alert')
        elif result:
            flash(u'Die Angaben und Werte wurden erfolgreich übernommen und gespeichert.','success')
 
            return redirect(url_for('.acquire_getsome', fraction_id=fraction_id,
                     source_fraction_id=source_fraction_id,
                     product_id=product_id))
        else:
            abort(500)

    if form.csrf_token.errors:
        flash(u'Zeitüberschreitung. Das Formular wird nach einer Stunde warten ungültig. Nichts gespeichert. Gleich nochmal versuchen.','warning')
    
    #manualy set wtform.data initial_preselected
    if not form.is_submitted():
        #print("FORM SUBMIT!")
        if 'acquiredate' in session:
            set_date = datetime.strptime(session.get('acquiredate'),form.aq_date.format).date()
            form.aq_date.data = set_date
            
        form.fraction_id.data = fraction.fraction_id
        form.source_fraction_id.data = source_fraction.fraction_id
        form.product_id.data = product_entries['product_id']
        if  request.args.get('unit_id',''):
            #print('UNIT_ID!!!!'+str(request.args.get('unit_id',''))+str(type(request.args.get('unit_id',''))))
            if int(request.args.get('unit_id','')) in[item[0] for item in form.unit_id.choices]:
                form.unit_id.data=int(request.args.get('unit_id',''))
        else:
            form.unit_id.data = product_entries['unit_pivot_id']
        form.box_id.data = product_entries['box_pivot_id']
        form.box_count.data = 0
        form.vehicle_count.data = 0
    

    return render_template('transaction/acquisition.html',
                           fraction=fraction,
                           source_fraction=source_fraction,
                           product_entries=product_entries,
                           boxset=boxset,
                           history_entries=history_entries,
                           form=form)
    

#---------------------------------------------------------------------------#
@transaction.route('/acquire/delete/<int:fraction_id>/<string:timestamp>/next/<path:next_url>',methods=["GET"])
def acquire_delete(fraction_id,timestamp,next_url):
    
    tmodel = TransactionModel(fraction_id)
    
    if tmodel.acqusition_delete(timestamp):
        flash('Eintrag erfolgreich gelöscht','success')
    else:
        flash('Konnte nicht gelöscht werden','alert')
    return redirect(next_url)
#################################################################
#
#RETRACTION Part
#
#################################################################  

@transaction.route('/retract/',methods=["GET"])
def retract_index():
    return render_template('transaction/retract_index.html')
#---------------------------------------------------------------------------#
@transaction.route('/retract/<int:fraction_id>/source/<int:source_fraction_id>')
def retract_twopack(fraction_id, source_fraction_id):
    """ two fractions are defined
    """
    if request.args.get('acquiredate'):
        session['acquiredate']= request.args.get('acquiredate')
        
    fraction = FractionModel(fraction_id)
    source_fraction = FractionModel(source_fraction_id)
    transaction_model = TransactionModel(fraction_id,source_fraction_id)
    

        #print('req.arg:'+request.args.get('acquiredate'))
    if 'acquiredate' in session:
        #print('RETRACTacquiredateInSession:',session.get('acquiredate'))
        transactions = transaction_model.get_simple(date=str(session.get('acquiredate')))
    else:
        transactions = None
        
    #print(str(transactions))  
    
    nav_dates = transaction_model.acqusitions_get_last_dates()
    
    return render_template('transaction/retraction.html',
                            fraction=fraction,
                            source_fraction=source_fraction,
                            nav_dates=nav_dates,
                            transactions=transactions
                            )

#---------------------------------------------------------------------------#
@transaction.route('/retract/<int:fraction_id>/source/<int:source_fraction_id>/product/<int:product_id>/unit/<int:unit_id>',methods=['GET','POST'])
def retract_getsome(fraction_id,source_fraction_id,product_id,unit_id):
    """Hit the retraction Table
    date is handled over session-cookie
    first get the entrie in the acquire data from that retour what you want
    we could restrict boxes ID  to acquire data but the user could retour in
    boxes of another date, years ago.
    """
    fraction = FractionModel(fraction_id)
    source_fraction = FractionModel(source_fraction_id)
    product = ProductModel(product_id, source_fraction_id)
    product_entries = product.get_data()
    unit = UnitModel(product_entries['unit_set_id'])
    box = BoxModel(product_entries['boxes_set_id'])
    vehicle = VehicleModel()
    transaction_model = TransactionModel(fraction_id,source_fraction_id)
    #Do I repeat myself?
    
    if request.args.get('acquiredate'):
        session['acquiredate']= request.args.get('acquiredate')
        
    if 'acquiredate' in session:
        the_date = str(session.get('acquiredate'))
    #
    acquire_data = transaction_model.acquisitions_get_summary_by_date_product_unit(the_date,product_id,unit_id)

    form = Acquisition_Retraction_Form()
    
    form.unit_id.choices = unit.get_wtform_choices()
    form.vehicle_id.choices = vehicle.get_wtform_choices()
    form.box_id.choices = box.get_wtform_choices()
    form.alternate_unit_id.choices = unit.get_wtform_choices()
    
    #prefill formdata
    form.aq_date.data = datetime.strptime(the_date,form.aq_date.format).date()
    form.product_id.data = product_id
    form.fraction_id.data = fraction_id
    form.source_fraction_id.data = source_fraction_id
    form.unit_id.data = acquire_data['unit_id']
    form.unit_id.render_kw={"disabled":"disabled"}
    
    form.box_id.data = acquire_data['box_id']
    #form.box_id.render_kw={"disabled":"disabled"}
    
    if acquire_data['alternatesum'] and acquire_data['alternate_unit_id'] in [item[0] for item in form.alternate_unit_id.choices] :
        form.alternate_unit_id.data = acquire_data['alternate_unit_id']
    else:
        form.alternate_unit_id.data = 1 #defaults to KG (Datenmüll)
    
    if form.validate_on_submit():
        
        result = transaction_model.retraction_insert(form)
        if type(result) is str:
            flash(result, 'alert')
        elif result:
            flash(u'Übernommen!','success')
            
            return redirect(url_for('.retract_twopack', fraction_id=fraction_id,
                                    source_fraction_id=source_fraction_id))
        else:
            abort(500)
            
    if form.csrf_token.errors:
        flash(u'Zeitüberschreitung. Das Formular wird nach einer Stunde warten ungültig. Nichts gespeichert. Gleich nochmal versuchen.','warning')
        
        
    return render_template('transaction/retraction.html',
                            fraction=fraction,
                            source_fraction=source_fraction,
                            product_entries=product_entries,
                            acquire_data=acquire_data,
                            form=form
                            )


