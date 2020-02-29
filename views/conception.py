#deprecated see vegetables.py
# app/views/vegetable_farming_blueprint.py

from flask import Blueprint, render_template, request, url_for, redirect
from flask import jsonify, flash, g, abort
#from sqlalchemy.engine import reflection
#from . import engine  #views/__init__.py
from app.models import VegetablesConceptionModel

from app.models import FractionModel 
from app.models import ProductModel
from app.models import DiversityModel
from app.models import GrowKindModel
#from app.models import AreaModel
from app.models import TransactionModel
from app.forms import VegetablesConceptionForm

import time

#vegetable_farming = Blueprint('vegetable_farming',__name__)

conception = Blueprint('conception',__name__)
vegetables_concept_model = VegetablesConceptionModel()

#---------------------------------------------------------------------------#
@conception.route('/<int:fraction_id>/<int:year_of_growth>')
def index(fraction_id, year_of_growth):
    """collects overview of all products with succsesions(Sätze)
    of one fraction in one year_of_growth
    """
    fraction = FractionModel(fraction_id)
    #productlist = fraction.get_product_list()
    productlist = fraction.cheata_menue() #implement list2nested!!!
    entries = vegetables_concept_model.get_overview(fraction_id, year_of_growth)
    summary = vegetables_concept_model.get_overview_summary(fraction_id, year_of_growth)
    area_info = vegetables_concept_model.get_involved_areas(fraction_id, year_of_growth)
    if not entries:
        return redirect( url_for('.create', fraction_id=fraction_id,
                          year_of_growth=year_of_growth))

    else:
        return render_template('conception/conception_index.html',
                           entries=entries,
                           productlist=productlist,
                           summary=summary,
                           area_info=area_info,
                           fraction=fraction,
                           year_of_growth=year_of_growth)

#---------------------------------------------------------------------------#                           
@conception.route('/create/<int:fraction_id>/<int:year_of_growth>')
def create(fraction_id, year_of_growth):
    """make the farmland right and hack manualy
    import a pre existing plan [1997] acording with croprotation and/or
    croprotate manualy....
    """
    
    fraction = FractionModel(fraction_id)
    
    return 'Begin planing on'+str(fraction.name)+' anno '+str(year_of_growth)

#---------------------------------------------------------------------------#
@conception.route('/<int:fraction_id>/<int:year_of_growth>/<int:product_id>')
def by_product_id(fraction_id, year_of_growth, product_id):
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
    
    area_info = vegetables_concept_model.get_involved_areas(fraction_id, year_of_growth)
    
    #t=transact.get_transactions(product_id)
    #print('Transactions:'+str(t))
    
    if the_product['tree_diff'] == 1:
        entries = vegetables_concept_model.get_product_by_id(fraction_id, year_of_growth, product_id)
        summary = vegetables_concept_model.get_summary_by_id(fraction_id, year_of_growth, product_id)
        end = time.time() #performence time end
        print('Performence conception.by_product_id:'+str(end-start)+'sec.')
        return render_template('conception/conception_one.html',
                               entries=entries,
                               summary=summary,
                               productlist=productlist,
                               fraction=fraction,
                               the_product=the_product,
                               area_info=area_info,
                               year_of_growth=year_of_growth,
                               pivot=pivot)
    else:
        return str(the_product)

#---------------------------------------------------------------------------#
@conception.route('/table/<int:fraction_id>/<int:year_of_growth>')
def table(fraction_id, year_of_growth):
  
    fraction = FractionModel(fraction_id)
    
    entries = vegetables_concept_model.ex_plan(fraction_id, year_of_growth)
    
    return render_template('conception/plan.html', entries=entries,
                           year_of_growth=year_of_growth,
                           fraction=fraction)

#---------------------------------------------------------------------------#
@conception.route('/new/<int:fraction_id>/<int:year_of_growth>/<int:product_id>',
                  methods=['GET', 'POST'])
def new(fraction_id, year_of_growth, product_id):
    """ formular """
    fraction = FractionModel(fraction_id)
    product = ProductModel(product_id, fraction_id)
    diversity = DiversityModel(product_id, fraction_id)
    growkind = GrowKindModel()
    
    the_product = product.get_data()
    #productlist = fraction.get_productlist()
    productlist = fraction.get_first_product_list()
    the_diversity = diversity.get()
    summary = vegetables_concept_model.get_summary_by_id(fraction_id, year_of_growth, product_id)
    
    form = VegetablesConceptionForm(request.form)
    
    #before validating wtf choises (<option>) must be given
    form.diversity_id.choices = diversity.get_wtform_choices()
    form.area_id.choices = fraction.area.get_wtform_choices()
    form.grow_kind_id.choices = growkind.get_wtform_choices()
    
    if form.validate_on_submit():
        
        new_id = vegetables_concept_model.insert(form)
        #print(">>>>>>>>> new_id: "+ str(new_id))
        if new_id:
            flash(u'Erfolgreich angelegt:#'+str(new_id), 'success')
            
            return redirect(url_for('.by_product_id',
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
    
    
    return render_template('conception/conception_input_form.html',
                           form=form,
                           fraction=fraction,
                           summary=summary,
                           productlist=productlist,
                           the_product=the_product,
                           the_diversity=the_diversity,
                           year_of_growth=year_of_growth,
                           edit=False)

#---------------------------------------------------------------------------#
@conception.route('/edit/<int:conception_id>',methods=['GET', 'POST'])
def edit(conception_id):
    """update"""
    
    data = vegetables_concept_model.get_by_id(conception_id)
    
    fraction_id = data['fraction_id']
    product_id = data['product_id']
    year_of_growth = data['year_of_growth']
    
    fraction = FractionModel(fraction_id)
    product = ProductModel(product_id, fraction_id)
    diversity = DiversityModel(product_id, fraction_id)
    growkind = GrowKindModel()
    #area = AreaModel()    

    the_product = product.get_data()
    #productlist = fraction.get_productlist()
    productlist = fraction.get_first_product_list()
    the_diversity = diversity.get()
    summary = vegetables_concept_model.get_summary_by_id(fraction_id, year_of_growth, product_id)    
    
    
    form = VegetablesConceptionForm(request.form, data=data) #obj=data
    #before validating choises must be given
    form.diversity_id.choices = diversity.get_wtform_choices()
    form.area_id.choices = fraction.area.get_wtform_choices()
    form.grow_kind_id.choices = growkind.get_wtform_choices()
    #print('>>>>>>>>>>>>>diversity_ID:'+str(form.diversity_id.data))
    if form.validate_on_submit():
        
        check = vegetables_concept_model.update(form, conception_id)
        
        if check == 1:
            flash(u'Erfolgreich geändert', 'success')
        if check == 0:
            flash(u'nichts verändert', 'primary')
            
        return redirect(url_for('.by_product_id',
                                fraction_id=fraction.fraction_id,
                                year_of_growth=year_of_growth,
                                product_id=product.product_id,
                                pivot=conception_id))        

    
    return render_template('conception/conception_input_form.html',
                           form=form,
                           fraction=fraction,
                           summary=summary,
                           productlist=productlist,
                           the_product=the_product,
                           the_diversity=the_diversity,
                           year_of_growth=year_of_growth,
                           edit=True,data=data)


#---------------------------------------------------------------------------#
@conception.route('/wtf/<int:fraction_id>/<int:year_of_growth>')
def ponderato(fraction_id, year_of_growth):
    
    entries = vegetables_concept_model.get(fraction_id, year_of_growth)
    

    return render_template('conception/show.html',entries=entries)
    
    
@conception.route('/<int:fraction_id>/<int:year_of_growth>/seed')
def seed(fraction_id, year_of_growth):
    fraction=FractionModel(fraction_id)
    entries = vegetables_concept_model.seed(fraction_id, year_of_growth)
    
    return render_template('conception/seed.html',
                           fraction=fraction,
                           entries=entries)


@conception.route('/<int:fraction_id>/<int:year_of_growth>/buy')
def buy(fraction_id, year_of_growth):
    
    fraction = FractionModel(fraction_id)
    
    entries = vegetables_concept_model.buy(fraction_id, year_of_growth)
    
    return render_template('conception/buy.html',
                           fraction=fraction,
                           year_of_growth=year_of_growth,
                           entries=entries)

@conception.route('/culture')
def culture():

    entries = vegetables_concept_model.culture()
    
    return render_template('conception/culture.html',entries=entries)

@conception.route('/area')
def area():
    #call modell
    vegetables_concept_model_res = vegetables_concept_model.area()
    #map rows
    entries = [ dict(area_name=row['area_name'],
                     name=row['name'],
                     div_name=row['diversity_name']
                     )for row in vegetables_concept_model_res.fetchall()]
    
    return render_template('conception/area.html',entries=entries)

@conception.route('/test')
def test():
    #return 'this was the test!'
    return render_template('base.html')
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
# führt aber möglicherweise unnötige vegetables_concept_model hits durch (8ms Cubietruck)
#---------------------------------------------------------------------------#

@conception.route('/_amount_of_plants_change')
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
    
    #call vegetables_concept_model
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
@conception.route('/_planting_interval_change')
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
    #call vegetables_concept_model
    
    if not amount_of_plants or amount_of_plants ==0:
        return jsonify({"message" : "pflanzenanzahl?"})
    
    if not amount_of_grow_kind_units or amount_of_grow_kind_units == 0:
        amount_of_grow_kind_units = 1 #return this too    
    #call vegetables_concept_model   
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

@conception.route('/_amount_of_grow_kind_units_change')
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
        
    #call vegetables_concept_model
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

@conception.route('/_grow_kind_id_change')
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
    
    #call vegetables_concept_model
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
