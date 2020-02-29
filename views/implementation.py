#deprecated see vegetables.py
# app/views/implementation

from flask import Blueprint, render_template, request, abort, flash, url_for, redirect, g
#from sqlalchemy.engine import reflection
#from . import engine  #views/__init__.py
from app.models import VegetablesImplementationModel
from app.models import FractionModel
from app.models import ProductModel
from app.models import DiversityModel
from app.models import GrowKindModel
from app.models import ContactsModel

from app.forms import VegetablesImplementationForm


implementation = Blueprint('implementation',__name__)

vegetables_implement_model = VegetablesImplementationModel()

#---------------------------------------------------------------------------#
@implementation.route('/<int:fraction_id>/<int:year_of_growth>')
def imp_index(fraction_id, year_of_growth):
    fraction = FractionModel(fraction_id)
    #productlist = fraction.get_first_product_list()
    productlist = fraction.cheata_menue()
    entries = vegetables_implement_model.get(fraction_id, year_of_growth)
    print(fraction.name)
    print(fraction.fraction_id)
    return render_template('implementation/implementation_index.html',
                           entries=entries,
                           productlist=productlist,
                           fraction=fraction,
                           year_of_growth=year_of_growth)
#---------------------------------------------------------------------------#
@implementation.route('/<int:fraction_id>/<int:year_of_growth>/<int:product_id>')
def imp_by_product_id(fraction_id, year_of_growth, product_id):
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
    
    productlist = fraction.get_first_product_list()

    the_product = product.get_data() #one dict
    
    if the_product['tree_diff'] == 1: # is leaf node
        entries = vegetables_implement_model.get_by_product_id(fraction_id, year_of_growth, product_id)
        return render_template('implementation/implementation_one.html',
                               entries=entries,
                               productlist=productlist,
                               fraction=fraction,
                               the_product=the_product,
                               year_of_growth=year_of_growth,
                               pivot=pivot)
    else:
        return str(the_product)
        #return render_template('implementation/layout_by_id.html', entries=entries)


#---------------------------------------------------------------------------#
@implementation.route('/new/<int:fraction_id>/<int:year_of_growth>/<int:product_id>',
                      methods=['GET','POST'])
def imp_new(fraction_id, year_of_growth, product_id):
    """formular to enter a new vegetables growing action """
    fraction = FractionModel(fraction_id)
    product = ProductModel(product_id, fraction_id)
    diversity = DiversityModel(product_id, fraction_id)
    growkind = GrowKindModel()
    contacts = ContactsModel()
    
    the_product = product.get_data()
    #productlist = fraction.get_productlist()
    productlist = fraction.get_first_product_list()
    the_diversity = diversity.get()
    
    form = VegetablesImplementationForm(request.form)

    #before validating choises must be given
    form.diversity_id.choices = diversity.get_wtform_choices()
    form.area_id.choices = fraction.area.get_wtform_choices()
    form.grow_kind_id.choices = growkind.get_wtform_choices()
    form.company_id.choices = contacts.get_wtform_choices()

    if form.validate_on_submit():
        
        new_id = vegetables_implement_model.insert(form)
        print(">>>>>>>>> new_id: "+ str(new_id))
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

    return render_template('implementation/implementation_input_form.html',
                           form=form,
                           fraction=fraction,
                           productlist=productlist,
                           the_product=the_product,
                           the_diversity=the_diversity,
                           year_of_growth=year_of_growth)

#---------------------------------------------------------------------------#
@implementation.route('edit/<int:implementation_id>',methods=['GET','POST'])
def imp_edit(implementation_id):
    """update"""
    data = vegetables_implement_model.get_by_id(implementation_id)
    
    fraction_id = data['fraction_id']
    product_id = data['product_id']
    year_of_growth = data['year_of_growth']
    
    fraction = FractionModel(fraction_id)
    product = ProductModel(product_id, fraction_id)
    diversity = DiversityModel(product_id, fraction_id)
    growkind = GrowKindModel()
    
    the_product = product.get_data()
    #productlist = fraction.get_first_product_list()
    productlist = fraction.cheata_menue() #implement list2nested!!!
    
    the_diversity = diversity.get()
    form = VegetablesImplementationForm(request.form, data=data) #obj=data
    #before validating choises must be given
    form.diversity_id.choices = diversity.get_wtform_choices()
    form.area_id.choices = fraction.area.get_wtform_choices()
    form.grow_kind_id.choices = growkind.get_wtform_choices()
    
    if form.validate_on_submit():
        
        check = vegetables_implement_model.update(form,implementation_id)
        
        if check == 1:
            flash(u'Erfolgreich geändert', 'success')
        if check == 0:
            flash(u'nichts verändert', 'primary')
        return redirect(url_for('.imp_by_product_id',
                                fraction_id=fraction.fraction_id,
                                year_of_growth=year_of_growth,
                                product_id=product.product_id,
                                pivot=conception_id))
    return render_template('implementation/implementation_input_form.html',
                           form=form,
                           fraction=fraction,
                           productlist=productlist,
                           the_product=the_product,
                           the_diversity=the_diversity,
                           year_of_growth=year_of_growth)

    
    
#---------------------------------------------------------------------------#
@implementation.route('/table/<int:fraction_id>/<int:year_of_growth>')
def imp_table(fraction_id, year_of_growth):
    """overview to be renderd in e.g. html table"""
    entries = vegetables_implement_model.get(fraction_id, year_of_growth)
    
    return render_template('implementation/implementation_table.html',entries=entries)

#---------------------------------------------------------------------------#
@implementation.route('/year')
def imp_year():

    #call model
    vegetables_implement_model_res = vegetables_implement_model.year()
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

                     

                        )for row in vegetables_implement_model_res.fetchall()]
    
    return render_template('implementation/implementation_index.html',entries=entries) 

#---------------------------------------------------------------------------#



