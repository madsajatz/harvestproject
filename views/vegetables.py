#!/usr/bin/env python3
from flask import Blueprint, render_template, request, url_for, redirect
from flask import jsonify, flash, g, abort
#from sqlalchemy.engine import reflection
#from . import engine  #views/__init__.py
from models import VegetablesConceptionModel
from models import VegetablesImplementationModel

from models import FractionModel 
from models import ProductModel
from models import DiversityModel
from models import CultivationModel
from models import GrowKindModel
from models import SeedModel
from models import ContactsModel
#from app.models import AreaModel
from models import TransactionModel
from forms import VegetablesConceptionForm
from forms import VegetablesImplementationForm
from helper import is_safe_url, get_redirect_target
import time

vegetables = Blueprint('vegetables',__name__)
""" vegetables growing simple"""
conception_model = VegetablesConceptionModel()
implementation_model = VegetablesImplementationModel()
#

#---------------------------------------------------------------------------#
@vegetables.route('/conception/<int:fraction_id>/<int:year_of_growth>')
def conception_index(fraction_id, year_of_growth):
    """collects overview of all products with succsesions(Sätze)
    of one fraction in one year_of_growth
    """
    fraction = FractionModel(fraction_id)
    product_list = fraction.get_product_list()
    productlist = fraction.cheata_menue() #implement list2nested!!!
    entries = conception_model.get_overview(fraction_id, year_of_growth)
    summary = conception_model.get_overview_summary(fraction_id, year_of_growth)
    ts = conception_model.last_modified(fraction_id, year_of_growth)
    area_info = conception_model.get_involved_areas(fraction_id, year_of_growth)
    if not entries:
        return redirect( url_for('.conception_create', fraction_id=fraction_id,
                          year_of_growth=year_of_growth))

    else:
        return render_template('vegetables/conception_index.html',
                           entries=entries,
                           productlist=productlist,
                           summary=summary,
                           ts=ts,
                           area_info=area_info,
                           fraction=fraction,
                           year_of_growth=year_of_growth)

#---------------------------------------------------------------------------#                           
@vegetables.route('/conception/create/<int:fraction_id>/<int:year_of_growth>')
def conception_create(fraction_id, year_of_growth):
    """creates a veggie Plan for a fraction at one year
    make the farmland right and hack manualy
    import a pre existing plan [1997] acording with croprotation and/or
    croprotate manualy....
    """
    
    fraction = FractionModel(fraction_id)
    
    return 'Begin planing on'+str(fraction.name)+' anno '+str(year_of_growth)

#---------------------------------------------------------------------------#
@vegetables.route('/conception/<int:fraction_id>/<int:year_of_growth>/<int:product_id>')
def conception_by_product_id(fraction_id, year_of_growth, product_id):
    """render all sets (Sätze) of one product"""
    start = time.time() #performence time start
    if request.args.get('pivot'):
        pivot = int(request.args.get('pivot'))#or_test (trinity operator)
    else:
        pivot = 0
        
    fraction = FractionModel(fraction_id)
    product = ProductModel(product_id, fraction_id)
    transact = TransactionModel(fraction_id)
    
    #productlist = fraction.get_product_list()
    productlist = fraction.cheata_menue() #implement list2nested!!!
    the_product = product.get_data()#:one dict
    
    area_info = conception_model.get_involved_areas(fraction_id, year_of_growth)
    
    #t=transact.get_transactions(product_id)
    #print('Transactions:'+str(t))
    
    #and the_product[0]['has_data'] == fraction_id 
    
    if  the_product['has_data'] == fraction_id:
        
        entries = conception_model.get_product_by_id(fraction_id, year_of_growth, product_id)
        summary = conception_model.get_summary_by_id(fraction_id, year_of_growth, product_id)
        end = time.time() #performence time end
        print('Performence conception.by_product_id:'+str(end-start)+'sec.')
        return render_template('vegetables/conception_one.html',
                               entries=entries,
                               summary=summary,
                               productlist=productlist,
                               fraction=fraction,
                               the_product=the_product,
                               area_info=area_info,
                               year_of_growth=year_of_growth,
                               pivot=pivot)
    
    elif the_product['tree_diff'] != 1 or the_product['has_data'] < 0 :
        return str(the_product)

#---------------------------------------------------------------------------#
@vegetables.route('/conception/table/<int:fraction_id>/<int:year_of_growth>')
def conception_table(fraction_id, year_of_growth):
    """ Table of it all """
    
    if request.values.get('pivot'):
        pivot = int(request.values.get('pivot'))#or_test (trinity operator)
    else:
        pivot = 0 
        
    fraction = FractionModel(fraction_id)
    entries = conception_model.ex_plan(fraction_id, year_of_growth)
    ts = conception_model.last_modified(fraction_id, year_of_growth)
    
    
    return render_template('vegetables/conception_plan.html', 
                           entries=entries,
                           year_of_growth=year_of_growth,
                           fraction=fraction,
                           ts=ts,
                           pivot=pivot)

#---------------------------------------------------------------------------#
#---------------------------------------------------------------------------#
@vegetables.route('/conception/table_print/<int:fraction_id>/<int:year_of_growth>')
def conception_table_print(fraction_id, year_of_growth):
    """ Table of it all 
    for printing """
        
    fraction = FractionModel(fraction_id)
    entries = conception_model.ex_plan(fraction_id, year_of_growth)
    ts = conception_model.last_modified(fraction_id, year_of_growth)
    
    return render_template('vegetables/conception_plan_print.html', 
                           entries=entries,
                           year_of_growth=year_of_growth,
                           fraction=fraction,
                           ts=ts)
                           

#---------------------------------------------------------------------------#
@vegetables.route('/conception/culture/<int:fraction_id>/<int:year_of_growth>')
def conception_culture(fraction_id, year_of_growth):
    """Flächenbelegung/Kulturen auf Flächen """
    fraction = FractionModel(fraction_id)
    
    entries = conception_model.conception_culture(fraction_id, year_of_growth)
    
    return render_template('vegetables/conception_culture.html',
                           fraction=fraction,
                           year_of_growth=year_of_growth,
                           entries=entries)



#---------------------------------------------------------------------------#
#POST#
@vegetables.route('/conception/new/<int:fraction_id>/<int:year_of_growth>/<int:product_id>',
                  methods=['GET', 'POST'])
def conception_new(fraction_id, year_of_growth, product_id):
    """create one new entrie for one product (fraction,year)
       and do an insert 
    """
    fraction = FractionModel(fraction_id)
    product = ProductModel(product_id, fraction_id)
    diversity = DiversityModel(product_id, fraction_id)
    cultivation = CultivationModel()
    growkind = GrowKindModel()
    seed = SeedModel()
    productlist = fraction.cheata_menue() #implement list2nested!!!
    #productlist = fraction.get_first_product_list() 
    
    the_product = product.get_data()
    the_diversity = diversity.get()
    summary = conception_model.get_summary_by_id(fraction_id, year_of_growth, product_id)
    #aside
    conceptions_micro = conception_model.get_micro_by_product_id(fraction_id, year_of_growth, product_id)
    
    form = VegetablesConceptionForm(request.form)
    
    #before validating wtf choices (<option>) must be given
    form.diversity_id.choices = diversity.get_wtform_choices()
    form.area_id.choices = fraction.area.get_wtform_choices()
    form.grow_kind_id.choices = growkind.get_wtform_choices()
    form.art_of_cultivation.choices = cultivation.get_wtform_choices()
    form.unit_of_seed.choices = seed.get_wtform_unit_choices()
    if form.validate_on_submit():
        
        new_id = conception_model.insert(form)
        #print(">>>>>>>>> new_id: "+ str(new_id))
        if new_id:
            flash(u'Erfolgreich angelegt:#'+str(new_id), 'success')
            
            return redirect(url_for('.conception_by_product_id',
                                    fraction_id=fraction.fraction_id,
                                    year_of_growth=year_of_growth,
                                    product_id=product.product_id,
                                    pivot=new_id))
        else:
            abort(500)

    #manualy poke initial form.values with the_product specs
    form.name.data = the_product['item_name']
    form.fraction_id.data = fraction.fraction_id
    form.year_of_growth.data =  year_of_growth
    form.product_id.data = the_product['product_id']
    
    form.grow_kind_id.data = (the_product['grow_kind_id'])
    
    form.planting_interval.data = the_product['planting_interval']
    
    
    return render_template('vegetables/conception_input_form.html',
                           form=form,
                           fraction=fraction,
                           summary=summary,
                           productlist=productlist,
                           the_product=the_product,
                           the_diversity=the_diversity,
                           year_of_growth=year_of_growth,
                           conceptions_micro=conceptions_micro,
                           edit=False)

#---------------------------------------------------------------------------#
#PUT#
@vegetables.route('/conception/edit/<int:conception_id>',methods=['GET', 'POST'])
def conception_edit(conception_id):
    """update an entrie by id"""
    #next = get_redirect_target()
    
    data = conception_model.get_by_id(conception_id) 
    
    fraction_id = data['fraction_id']
    product_id = data['product_id']
    year_of_growth = data['year_of_growth']
    
    fraction = FractionModel(fraction_id)
    product = ProductModel(product_id, fraction_id)
    diversity = DiversityModel(product_id, fraction_id)
    cultivation = CultivationModel()
    growkind = GrowKindModel()
    seed = SeedModel()
    #area = AreaModel()    
    productlist = fraction.cheata_menue() #implement list2nested!!!
    #productlist = fraction.get_product_list()    

    the_product = product.get_data()
    the_diversity = diversity.get()
    summary = conception_model.get_summary_by_id(fraction_id, year_of_growth, product_id)
    #aside
    conceptions_micro = conception_model.get_micro_by_product_id(fraction_id, year_of_growth, product_id)    
    
    
    form = VegetablesConceptionForm(request.form, data=data) #obj=data
    #before validating choices must be given
    form.diversity_id.choices = diversity.get_wtform_choices()
    form.area_id.choices = fraction.area.get_wtform_choices()
    form.grow_kind_id.choices = growkind.get_wtform_choices()
    form.art_of_cultivation.choices = cultivation.get_wtform_choices()
    form.unit_of_seed.choices = seed.get_wtform_unit_choices()
    
    #print('>>>>>>>>>>>>>diversity_ID:'+str(form.diversity_id.data))
    if form.validate_on_submit():
        next = get_redirect_target()
        
        check = conception_model.update(form, conception_id)
        
        if check == 1:
            flash(u'Erfolgreich geändert', 'success')
        if check == 0:
            flash(u'Nichts verändert', 'primary')
        #print('ValidOnSubmit>>>>>>>>>>>>>>>'+str(next))    
        #redirect to next here or default to here 
        #TODO use redirect_back()
        
        if next:
            #redirect(next+'?pivot='+str(conception_id))
            print('NExT conc_edit##>'+str(next))
            return redirect(next)
        else:
            return redirect(url_for('.conception_by_product_id',
                                fraction_id=fraction.fraction_id,
                                year_of_growth=year_of_growth,
                                product_id=product.product_id,
                                pivot=conception_id))        

    next = get_redirect_target()
    if next == request.base_url:
             return redirect(url_for('.conception_by_product_id',
                                fraction_id=fraction.fraction_id,
                                year_of_growth=year_of_growth,
                                product_id=product.product_id,
                                pivot=conception_id))   
    
    
    else:
    #print('req.base_url'+str(request.base_url))
        print('NExT before render conception_input_form:'+str(next))
        return render_template('vegetables/conception_input_form.html',
                           form=form,
                           fraction=fraction,
                           summary=summary,
                           productlist=productlist,
                           the_product=the_product,
                           the_diversity=the_diversity,
                           year_of_growth=year_of_growth,
                           conceptions_micro=conceptions_micro,
                           edit=True,
                           data=data,
                           next=next
                           )


#---------------------------------------------------------------------------#
#DELETE#
@vegetables.route('/conception/delete/<int:conception_id>')
def conception_delete(conception_id):
    """ calls a model delete and reroutes to ?next url 
    TODO is_safe_url
    """
    res = conception_model.delete(conception_id)
    if res == 1:
        flash(u'Erfolgreich gelöscht', 'success')
    else:
        abort(500)
        
    target = request.args.get('next')
    
    if is_safe_url(target):
        print('next: ',target)
        return redirect(target)
    else:
        return redirect(url_for('index'))

#---------------------------------------------------------------------------#
@vegetables.route('/conception/area/<int:fraction_id>/<int:year_of_growth>/<int:area_id>')
def conception_area(fraction_id, year_of_growth, area_id=None):
    """ plan on one area can go to conception_index
    and route "area" is to prepare area
    """
    fraction = FractionModel(fraction_id)
    #productlist = fraction.get_product_list()
    productlist = fraction.cheata_menue() #implement list2nested!!!    
    entries = conception_model.get_overview(fraction_id, year_of_growth, area_id)
    area = fraction.area.get_by_id(area_id)
    area_info = conception_model.get_involved_areas(fraction_id, year_of_growth)
    
    return render_template('vegetables/conception_area.html',
                           entries=entries,
                           fraction=fraction,
                           year_of_growth=year_of_growth,
                           productlist=productlist,
                           area=area,
                           area_info=area_info)
#---------------------------------------------------------------------------#
@vegetables.route('/conception/arealess/<int:fraction_id>/<int:year_of_growth>')
def unbound_area(fraction_id, year_of_growth):
    
    return('sorry')




#---------------------------------------------------------------------------#
@vegetables.route('/conception/wtf/<int:fraction_id>/<int:year_of_growth>')
def conception_ponderato(fraction_id, year_of_growth):
    
    entries = conception_model.get(fraction_id, year_of_growth)
    

    return render_template('vegetables/conception_show.html',entries=entries)
    
#---------------------------------------------------------------------------#    
@vegetables.route('/conception/seed/<int:fraction_id>/<int:year_of_growth>')
def conception_seed(fraction_id, year_of_growth):
    fraction=FractionModel(fraction_id)
    entries = conception_model.seed(fraction_id, year_of_growth)
    
    return render_template('vegetables/conception_seed.html',
                           fraction=fraction,
                           year_of_growth=year_of_growth,
                           entries=entries)

#---------------------------------------------------------------------------#
@vegetables.route('/conception/implant/<int:fraction_id>/<int:year_of_growth>')
def conception_implant(fraction_id, year_of_growth):
    fraction=FractionModel(fraction_id)
    entries = conception_model.implant(fraction_id, year_of_growth)
    
    return render_template('vegetables/conception_implant.html',
                           fraction=fraction,
                           year_of_growth=year_of_growth,
                           entries=entries)

#---------------------------------------------------------------------------#
@vegetables.route('/conception/purchase/<int:fraction_id>/<int:year_of_growth>')
def conception_buy(fraction_id, year_of_growth):
    
    fraction = FractionModel(fraction_id)
    
    entries = conception_model.buy(fraction_id, year_of_growth)
    
    return render_template('vegetables/conception_purchase.html',
                           fraction=fraction,
                           year_of_growth=year_of_growth,
                           entries=entries)

#---------------------------------------------------------------------------#
#---------------------------------------------------------------------------#
@vegetables.route('/conception/purchase_print/<int:fraction_id>/<int:year_of_growth>')
def conception_buy_print(fraction_id, year_of_growth):
    
    fraction = FractionModel(fraction_id)
    
    entries = conception_model.buy(fraction_id, year_of_growth)
    
    return render_template('vegetables/conception_purchase_print.html',
                           fraction=fraction,
                           year_of_growth=year_of_growth,
                           entries=entries)

#---------------------------------------------------------------------------#

@vegetables.route('/conception/field/<int:fraction_id>/<int:year_of_growth>')
def conception_field(fraction_id, year_of_growth, area_id=None):
    """ demand on prepared soil per week"""
    fraction = FractionModel(fraction_id)
    entries = conception_model.conception_field(fraction_id,year_of_growth,area_id)
    
    return render_template('vegetables/conception_field.html',
                           fraction=fraction,
                           year_of_growth=year_of_growth,
                           entries=entries)


    
#---------------------------------------------------------------------------#
#---------------------------------------------------------------------------#
#AJAX -- AJAX -- AJAX -- AJAX -- AJAX -- AJAX -- AJAX -- AJAX -- AJAX -- AJAX
# in den folgenden routen gibt es immer wieder dieselbe
# Berechnung , wie out sourcen und wohin?
#f(amount_of_plants, planting_interval, growlines, amount_of_grow_kind_units, width)
# ->new_length_of_field, new_square_of_field, new_plants_per_square
# OK sind nich immer die selben...
# sind DOCH immer die selben
# am besten im model als _get_new_ajax...{message :"",force_plant_interval : true,...}
# dann erspart man sich ein grow_kind_Model
# führt aber möglicherweise unnötige conception_model hits durch (8ms Cubietruck)
#
# Only One ajaxRoute per 'micro_mechanic_frontendish' inside a form,
# make shure you hit a stored procedure, Postgres function.
# is_default_setting, last_update_micro=last_update_form_fieldset
# last_modifyed_by_user_id, is_valid/does_compute_somehow, is_Top10_most_used_geometry_for_product
# last_year_crop_per_square_of_field, spooky_expected_crop_amount
# use models.py NO_CHOICE_VALUE of -1 for please_no_computation_at_all_option
# 
# 
#---------------------------------------------------------------------------#

@vegetables.route('/_amount_of_plants_change')
def amount_of_plants_change():
    """ajax in VegetablesConceptionForm
    
    """
    grow_kind_model=GrowKindModel()
    #GET parameters
    amount_of_plants = request.args.get('amount_of_plants', type=int)
    grow_kind_id = request.args.get('grow_kind_id', type=int)
    planting_interval = request.args.get('planting_interval',type=float)
    amount_of_grow_kind_units = request.args.get('amount_of_grow_kind_units',type=int)
    
    if not grow_kind_id:
        return jsonify({"message" : "anbauform?"})
    if not planting_interval:
        return jsonify({"message" : "pflanzabstand?"})
    
    #call conception_model
    data = grow_kind_model.get_short_by_id(grow_kind_id)
    #print(data)
    
    if data['force_plant_interval']: # will prob. never be
        planting_interval = data['planting_interval'] #return that
        
        print('FORCE_PLANT_INTERVAL: '+str(data['planting_interval']))
        
    if not amount_of_grow_kind_units or amount_of_grow_kind_units == 0:
        amount_of_grow_kind_units = 1 #return this too
    
    
        
    #print('amount_of_plants: '+ str(amount_of_plants))
    #print('planting_interval: '+ str(planting_interval))
    #print(type(data['width']))
    
    new_length_of_field = round(((amount_of_plants * planting_interval) /
                                 data['growlines']) / amount_of_grow_kind_units ,2)
    new_square_of_field = round(new_length_of_field *
                                amount_of_grow_kind_units * data['width'] ,2)
    new_plants_per_square = round(amount_of_plants / new_square_of_field ,2)
    
    
    js = {"plants_per_square" : new_plants_per_square,
           "amount_of_grow_kind_units" : amount_of_grow_kind_units,
           "length_of_field" : new_length_of_field,
           "square_of_field" : new_square_of_field,
           "planting_interval" : planting_interval
           }
    print('RESPONSE: '+str(js))
    #return Response(jsonify(js),  mimetype='application/json')   
    return jsonify(js)
#---------------------------------------------------------------------------#
@vegetables.route('/_planting_interval_change')
def planting_interval_change():
    """ajax in VegetablesConceptionForm
    
    """
    grow_kind_model=GrowKindModel()
    
    #GET parameters
    amount_of_plants = request.args.get('amount_of_plants', type=int)
    grow_kind_id = request.args.get('grow_kind_id', type=int)
    planting_interval = request.args.get('planting_interval')
    planting_interval = float(planting_interval.replace(",", "."))
    
    amount_of_grow_kind_units = request.args.get('amount_of_grow_kind_units',type=int)
    #call conception_model
    
    if not amount_of_plants or amount_of_plants ==0:
        return jsonify({"message" : "pflanzenanzahl?"})
    
    if not amount_of_grow_kind_units or amount_of_grow_kind_units == 0:
        amount_of_grow_kind_units = 1 #return this too    
    #call conception_model   
    data = grow_kind_model.get_short_by_id(grow_kind_id)
    #print(data)
    new_length_of_field = round(((amount_of_plants * planting_interval) /
                                 data['growlines']) / amount_of_grow_kind_units ,2)
    new_square_of_field = round(new_length_of_field *
                                amount_of_grow_kind_units * data['width'] ,2)
    new_plants_per_square = round(amount_of_plants / new_square_of_field ,2)

    js = {"plants_per_square" : new_plants_per_square,
           "amount_of_grow_kind_units" : amount_of_grow_kind_units,
           "length_of_field" : new_length_of_field,
           "square_of_field" : new_square_of_field
           }
    print('RESPONSE: '+str(js))
    #return Response(jsonify(js),  mimetype='application/json')   
    return jsonify(js)

#---------------------------------------------------------------------------#

@vegetables.route('/_amount_of_grow_kind_units_change')
def amount_of_grow_kind_units_change():
    """ajax in VegetablesConceptionForm
    
    """
    grow_kind_model=GrowKindModel()
    #print('f:amount_of_plants_change; as been called on the FLASK SIDE of THE HUHN!!!')
    #GET parameters
    amount_of_plants = request.args.get('amount_of_plants', type=int)
    grow_kind_id = request.args.get('grow_kind_id', type=int)
    planting_interval = request.args.get('planting_interval',type=float)
    amount_of_grow_kind_units = request.args.get('amount_of_grow_kind_units',type=int)
    
    if not amount_of_plants or amount_of_plants ==0:
        abort(418)
    if not amount_of_grow_kind_units or amount_of_grow_kind_units == 0:
        abort(418)
        
    #call conception_model
    data = grow_kind_model.get_short_by_id(grow_kind_id)
    #print(data)
    new_length_of_field = round(((amount_of_plants * planting_interval) /
                                 data['growlines']) / amount_of_grow_kind_units ,2)
    new_square_of_field = round(new_length_of_field *
                                amount_of_grow_kind_units * data['width'] ,2)
    new_plants_per_square = round(amount_of_plants / new_square_of_field ,2)
    
    js = {"plants_per_square" : new_plants_per_square,
           "length_of_field" : new_length_of_field,
           "square_of_field" : new_square_of_field
        }
    print('RESPONSE: '+str(js))
    #return Response(jsonify(js),  mimetype='application/json')   
    return jsonify(js)

#---------------------------------------------------------------------------#

@vegetables.route('/_grow_kind_id_change')
def grow_kind_id_change():
    """ajax in VegetablesConceptionForm
    
    """
    grow_kind_model=GrowKindModel()
    #GET parameters
    amount_of_plants = request.args.get('amount_of_plants', type=int)
    grow_kind_id = request.args.get('grow_kind_id', type=int)
    planting_interval = request.args.get('planting_interval',type=float)
    amount_of_grow_kind_units = request.args.get('amount_of_grow_kind_units',type=int)

    if not amount_of_plants or amount_of_plants ==0:
        return jsonify({"message":"Pflanzenanzahl?"})

    if not grow_kind_id:
        return jsonify({"message":"Anbauform?"})

    if not amount_of_grow_kind_units or amount_of_grow_kind_units == 0:
        amount_of_grow_kind_units = 1 #return this
    
    #call conception_model
    data = grow_kind_model.get_short_by_id(grow_kind_id)
    #print(data)
    if data['force_plant_interval']:
        planting_interval = data['planting_interval']
    
    new_length_of_field = round(((amount_of_plants * planting_interval) /
                                 data['growlines']) / amount_of_grow_kind_units ,2)
    new_square_of_field = round(new_length_of_field *
                                amount_of_grow_kind_units * data['width'] ,2)
    new_plants_per_square = round(amount_of_plants / new_square_of_field ,2)
    
    js = {"planting_interval" : planting_interval,
          "plants_per_square" : new_plants_per_square,
          "amount_of_grow_kind_units" : amount_of_grow_kind_units,
          "length_of_field" : new_length_of_field,
          "square_of_field" : new_square_of_field
        }
    return jsonify(js)
#---------------------------------------------------------------------------#
#
#
##
#                           IPLEMENTATION PART
##
#
#
# AJAX make a route
# in case of transactions run in a different app
# predict_implementation_id(source_fraction_id, product_id, date) 
#                           returns list(of_ implementation_id) OR emty
#
#---------------------------------------------------------------------------#


#---------------------------------------------------------------------------#
@vegetables.route('/implementation/<int:fraction_id>/<int:year_of_growth>')
def implementation_index(fraction_id, year_of_growth):
    fraction = FractionModel(fraction_id)
    #productlist = fraction.get_first_product_list()
    productlist = fraction.cheata_menue()
    entries = implementation_model.get_overview(fraction_id, year_of_growth)
    print(fraction.name)
    print(fraction.fraction_id)
    return render_template('vegetables/implementation_index.html',
                           entries=entries,
                           productlist=productlist,
                           fraction=fraction,
                           year_of_growth=year_of_growth)
#---------------------------------------------------------------------------#
@vegetables.route('/implementation/<int:fraction_id>/<int:year_of_growth>/<int:product_id>')
def implementation_by_product_id(fraction_id, year_of_growth, product_id):
    """render all sets (Sätze) of one procuct that were realised
    by one fraction in a year
    """
    #is one element of entries pivot?
    if request.args.get('pivot'):
        pivot = int(request.args.get('pivot'))
    else:
        pivot = 0    
    
    fraction = FractionModel(fraction_id)
    product = ProductModel(product_id, fraction_id)
    
    productlist = fraction.cheata_menue() #implement list2nested!!!
    #productlist = fraction.get_product_list()

    the_product = product.get_data() #one dict
    
    #if the_product['tree_diff'] == 1: # is leaf node
    if the_product['has_data'] == fraction_id:
        
        imp_entries = implementation_model.get_product_by_id(fraction_id,year_of_growth,product_id)
        con_entries = conception_model.get_product_by_id(fraction_id,year_of_growth,product_id)
        imp_summary = implementation_model.get_summary_by_id(fraction_id,year_of_growth,product_id)
        con_summary = conception_model.get_summary_by_id(fraction_id,year_of_growth,product_id)
        return render_template('vegetables/implementation_one.html',
                               con_entries=con_entries,
                               imp_entries=imp_entries,
                               con_summary=con_summary,
                               imp_summary=imp_summary,
                               productlist=productlist,
                               fraction=fraction,
                               the_product=the_product,
                               year_of_growth=year_of_growth,
                               pivot=pivot)
    elif the_product['tree_diff'] != 1 or the_product['has_data'] < 0 :
        return str(the_product)
    
        #return render_template('implementation/layout_by_id.html', entries=entries)


#---------------------------------------------------------------------------#
@vegetables.route('/implementation/new/<int:fraction_id>/<int:year_of_growth>/<int:product_id>',
                      methods=['GET','POST'])
def implementation_new(fraction_id, year_of_growth, product_id):
    """formular to enter a new vegetables growing action """
    fraction = FractionModel(fraction_id)
    product = ProductModel(product_id, fraction_id)
    diversity = DiversityModel(product_id, fraction_id)
    cultivation = CultivationModel()
    growkind = GrowKindModel()
    seed = SeedModel()
    contacts = ContactsModel()
    
    #productlist = fraction.get_productlist()
    productlist = fraction.cheata_menue() #implement list2nested!!!    
    
    the_product = product.get_data()
    the_diversity = diversity.get()
    
    form = VegetablesImplementationForm(request.form)

    #before validating choices must be given
    form.diversity_id.choices = diversity.get_wtform_choices()
    form.area_id.choices = fraction.area.get_wtform_choices()
    form.grow_kind_id.choices = growkind.get_wtform_choices()
    form.unit_of_seed.choices = seed.get_wtform_unit_choices()
    form.art_of_cultivation.choices = cultivation.get_wtform_choices()
    form.company_id.choices = contacts.get_wtform_choices()

    if form.validate_on_submit():
        
        new_id = implementation_model.insert(form)
        print(">>>>>>>>> new_id: "+ str(new_id))
        if new_id:
            flash(u'Erfolgreich angelegt:#'+str(new_id), 'success')
            
            return redirect(url_for('.implementation_by_product_id',
                                    fraction_id=fraction.fraction_id,
                                    year_of_growth=year_of_growth,
                                    product_id=product.product_id,
                                    pivot=new_id))
        else:
            abort(500)
    

    #manualy poke initial form.values with the_product specs
    form.name.data = the_product['item_name']
    form.fraction_id.data = fraction.fraction_id
    form.year_of_growth.data =  year_of_growth
    form.product_id.data = the_product['product_id']
    
    form.grow_kind_id.data = (the_product['grow_kind_id'])
    
    form.planting_interval.data = the_product['planting_interval']

    return render_template('vegetables/implementation_input_form.html',
                           form=form,
                           fraction=fraction,
                           productlist=productlist,
                           the_product=the_product,
                           the_diversity=the_diversity,
                           year_of_growth=year_of_growth,
                           flag='new')

#---------------------------------------------------------------------------#
@vegetables.route('/implementation/edit/<int:implementation_id>',methods=['GET','POST'])
def implementation_edit(implementation_id):
    """update"""
    data = implementation_model.get_by_id(implementation_id)
    
    fraction_id = data['fraction_id']
    product_id = data['product_id']
    year_of_growth = data['year_of_growth']
    
    fraction = FractionModel(fraction_id)
    product = ProductModel(product_id, fraction_id)
    diversity = DiversityModel(product_id, fraction_id)
    cultivation = CultivationModel()
    growkind = GrowKindModel()
    seed = SeedModel()
    contacts = ContactsModel()
    
    the_product = product.get_data()
    #productlist = fraction.get_first_product_list()
    productlist = fraction.cheata_menue() #implement list2nested!!!
    
    the_diversity = diversity.get()
    form = VegetablesImplementationForm(request.form, data=data) #obj=data
    #before validating choices must be given
    form.diversity_id.choices = diversity.get_wtform_choices()
    form.area_id.choices = fraction.area.get_wtform_choices()
    form.art_of_cultivation.choices = cultivation.get_wtform_choices()
    form.grow_kind_id.choices = growkind.get_wtform_choices()
    form.unit_of_seed.choices = seed.get_wtform_unit_choices()
    form.company_id.choices = contacts.get_wtform_choices()
    
    if form.validate_on_submit():
        
        check = implementation_model.update(form,implementation_id)
        
        if check == 1:
            flash(u'Erfolgreich geändert', 'success')
        if check == 0:
            flash(u'nichts verändert', 'primary')
        return redirect(url_for('.implementation_by_product_id',
                                fraction_id=fraction.fraction_id,
                                year_of_growth=year_of_growth,
                                product_id=product.product_id,
                                pivot=implementation_id))
    return render_template('vegetables/implementation_input_form.html',
                           form=form,
                           fraction=fraction,
                           productlist=productlist,
                           the_product=the_product,
                           the_diversity=the_diversity,
                           year_of_growth=year_of_growth,
                           data=data,
                           flag='edit')

#---------------------------------------------------------------------------#    
@vegetables.route('/implementation/fromconcept/<int:conception_id>',methods=['GET','POST'])
def implementation_create_from_conception(conception_id):
    """provides a form with prefilled conception values"""
    conception_data = conception_model.get_by_id(conception_id)
    
    fraction_id = conception_data['fraction_id']
    product_id = conception_data['product_id']
    year_of_growth = conception_data['year_of_growth']
    
    fraction = FractionModel(fraction_id)
    the_product = ProductModel(product_id, fraction_id)
    productlist = fraction.cheata_menue() #implement list2nested!!!
    
    the_diversity = DiversityModel(product_id, fraction_id)
    cultivation = CultivationModel()
    growkind = GrowKindModel()  
    seed = SeedModel()
    contacts = ContactsModel()
    
    
    form = VegetablesImplementationForm(request.form)
    
    #before validating choices must be given
    form.diversity_id.choices = the_diversity.get_wtform_choices()
    form.area_id.choices = fraction.area.get_wtform_choices()
    form.grow_kind_id.choices = growkind.get_wtform_choices()
    form.unit_of_seed.choices = seed.get_wtform_unit_choices()
    form.art_of_cultivation.choices = cultivation.get_wtform_choices()
    form.company_id.choices = contacts.get_wtform_choices()

    if form.validate_on_submit():
        
        new_id = implementation_model.insert(form)
        print(">>>>>>>>> new_id: "+ str(new_id))
        if new_id:
            flash(u'Durchführung erfolgreich angelegt:#'+str(new_id), 'success')
            upd = conception_model.lock_entrie(conception_id)
            if upd ==1:
                flash(u'Planungseintrag archiviert','primary')
            
            return redirect(url_for('.implementation_by_product_id',
                                    fraction_id=fraction.fraction_id,
                                    year_of_growth=year_of_growth,
                                    product_id=the_product.product_id,
                                    pivot=new_id))
        else:
            abort(500)
    #manualy poke form.field.data with conception_data
    #rule number one: NEVER map manualy
    #just data=conception_data
    form.conception_id.data = conception_data['id']
    form.fraction_id.data = conception_data['fraction_id']
    form.product_id.data = conception_data['product_id']
    form.year_of_growth.data = conception_data['year_of_growth']
    form.name.data = conception_data['name']
    form.diversity_id.data = conception_data['diversity_id']
    form.area_id.data = conception_data['area_id']
    form.grow_kind_id.data = conception_data['grow_kind_id']
    form.art_of_cultivation.data = conception_data['art_of_cultivation']
    form.amount_of_grow_kind_units.data = conception_data['amount_of_grow_kind_units']
    form.hint.data = conception_data['hint']
    form.amount_of_plants.data = conception_data['amount_of_plants']
    form.planting_interval.data = conception_data['planting_interval']
    form.length_of_field.data = conception_data['length_of_field']
    form.square_of_field.data = conception_data['square_of_field']
    form.plants_per_square.data = conception_data['plants_per_square']
    
    return render_template('vegetables/implementation_input_form.html',
                           form=form,
                           fraction=fraction,
                           productlist=productlist,
                           the_product=the_product,
                           the_diversity=the_diversity,
                           year_of_growth=year_of_growth,
                           conception_data=conception_data,
                           flag='cfc')    
    
#---------------------------------------------------------------------------#
@vegetables.route('/implementation/table/<int:fraction_id>/<int:year_of_growth>')
def implementation_table(fraction_id, year_of_growth):
    """overview to be renderd in e.g. html table"""
    entries = implementation_model.get(fraction_id, year_of_growth)
    
    return render_template('vegetables/implementation_table.html',entries=entries)

#---------------------------------------------------------------------------#
@vegetables.route('/implementation/year')
def implementation_year():

    #call model
    implementation_model_res = implementation_model.year()
    #map rows
    entries = [ dict(hint=row['hint'],
                     square_of_field=row['square_of_field'],
                     area_name=row['area_name'],
                     growkind_name=row['growkind_name'],
                     length_of_field=row['length_of_field'],
                     amount_of_plants=row['amount_of_plants'],
                     plants_per_square=row['plants_per_square'],
                     plant_interval=row['plant_interval'],
                     date_of_act_seeding=row['date_of_act_seeding'],
                     week_of_act_seeding=row['week_of_act_seeding'],
                     date_of_act_germing=row['date_of_act_germing'],
                     week_of_act_germing=row['week_of_act_germing'],
                     date_of_act_planting=row['date_of_act_planting'],
                     week_of_act_planting=row['week_of_act_planting'],
                     date_of_act_prickout=row['date_of_act_prickout'],
                     week_of_act_prickout=row['week_of_act_prickout'],
                     date_of_act_yilding=row['date_of_act_yilding'],
                     week_of_act_yilding=row['week_of_act_yilding'],
                     date_of_act_removal=row['date_of_act_removal'],
                     week_of_act_removal=row['week_of_act_removal'],
                     act_duration=row['act_duration'],
                     name=row['name'],
                     diversity_name=row['diversity_name'],
                     note=row['note'],
                     ago=row['ago']

                     

                        )for row in implementation_model_res.fetchall()]
    
    return render_template('vegetables/implementation_index.html',entries=entries) 

#---------------------------------------------------------------------------#



