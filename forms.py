#!/usr/bin/env python
"""Splitt up Forms to Blueprints?
"""
from flask_wtf import FlaskForm
from wtforms import TextField
from wtforms import IntegerField
from wtforms import StringField
from wtforms import BooleanField
from wtforms import DecimalField
from wtforms import SelectField
from wtforms import HiddenField
from wtforms import TextAreaField
from wtforms import SelectField
from wtforms import SelectMultipleField
from wtforms.widgets import HiddenInput
from wtforms import widgets

#from wtforms.meta import DefaultMeta
from wtforms.fields.html5 import DateField
#from wtforms.fields.html5 import WeekField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange
from wtforms.validators import Optional
from datetime import date

class FlexibleDecimalField(DecimalField):
    """accept decimal separation comma"""
    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", ".")
        return super(FlexibleDecimalField, self).process_formdata(valuelist)

def my_select_validator(form,field):
    """WTF? see model.NO_CHOICE_VALUE
    SelectField can't have boolean(None) in choises with coerce=int!
    -If we 'coerce=str' the None is returned as str('None').
    -A Filter like filters=[lambda x: x if type(x)==int and x >= 0 else None]
    applies before validation and do wrong again.
    So I validate  -1 as "not chosen yet" to be boolean(None) -> database: NULL!
    """
    if field.data < 0:
        print('my_select_validator!!!!!!!!')
        field.data = None
        



class VegetablesConceptionForm(FlaskForm):
    """Input and edit a plan on veggie growing
    chromiums standart output for Input-Date is %Y-%m-%d formatet 
    """
    #filters=[lambda x: x if type(x)==int and x >= 0 else None],
    
    #:id optional, in case of insert id is not present
    id = IntegerField(widget=HiddenInput(), validators=[Optional()])
    fraction_id = IntegerField(widget=HiddenInput())
    product_id = IntegerField(widget=HiddenInput())
    year_of_growth = IntegerField(widget=HiddenInput())

    name = StringField(u'Benennung', validators=[DataRequired(), Length(max=128)], render_kw={"placeholder": "Namen"})
    diversity_id = SelectField(u'Sorte', choices=[], coerce=int, validators=[my_select_validator])
    area_id = SelectField(u'Schlag', choices=[], coerce=int, validators=[my_select_validator])

    date_of_plan_seed = DateField(label=u'Datum Aussaat', format="%Y-%m-%d", validators=[Optional()], render_kw={"placeholder": "Datum Aussaat"})
    week_of_plan_seed = IntegerField(u'KW', validators=[NumberRange(min=1, max=53, message='KW muss zwischen 1 und 53 liegen'), Optional() ] )

    date_of_plan_plant = DateField(label=u'Datum Pflanzung', format="%Y-%m-%d", validators=[Optional()])
    week_of_plan_plant = IntegerField(u'KW', validators=[NumberRange(min=1, max=53, message='KW muss zwischen 1 und 53 liegen'), Optional()])#, render_kw={'size': '3','type':'week'})

    date_of_plan_crop = DateField(label=u'Datum Ernte', format='%Y-%m-%d', validators=[Optional()])
    week_of_plan_crop = IntegerField(u'KW', validators=[NumberRange(min=1, max=53, message='KW muss zwischen 1 und 53 liegen'), Optional()])
    
    art_of_cultivation = SelectField(label=None, choices=[], validators=[Optional()])
    amount_of_plants = IntegerField(u'Pflanzenanzahl', validators=[Optional()])
    planting_interval = FlexibleDecimalField(u'Pflanzenabstand', validators=[Optional()])
    plants_per_square = DecimalField(u'Pfl./qm', validators=[Optional()])
    
    amount_of_grow_kind_units = IntegerField(u'x-mal', validators=[Optional()])
    grow_kind_id = SelectField(u'in der Anbauform', choices=[], coerce=int, validators=[my_select_validator])
    length_of_field = DecimalField(u'mit der Länge', validators=[Optional()])
    square_of_field = DecimalField(u'Fläche', validators=[Optional()])

    amount_of_seed = FlexibleDecimalField(u'Saatgutmenge', validators=[Optional()]) 

    unit_of_seed = SelectField(u'Saatguteinheit', choices=[], coerce=int, validators=[my_select_validator])
    hint = StringField(u'Überschrift', validators=[Length(max=256)])
    #geoinfo_plan = StringField(u'Geo Information'
    
    #seed_spec  = StringField()
    note = TextAreaField(u'Notiz',render_kw={'rows': 4})
    
    
class VegetablesCreateFromConceptionForm(FlaskForm):
    """out of one conception entry, several implementations can be generated 
    @vegetables.route('/implementation/fromconcept/<int:conception_id>',methods=['GET','POST'])
    is part of the tool box
    from one concept of 20000 Tomatos make me 12 implementations
    in 1,20 beeds-2lanes_7' fitting my greenhouse2 southwing with its 12 beeds
    the new implementations could be inserted with a is_hovering tag for one hour till... or
    be deleted now to Post this a few times with different parameters for best result.
    
    """
    #count
    #amount_of_plans
    #grow_kind_id
    #areas
    #length_of_field
    
    
    
    
class VegetablesImplementationForm(FlaskForm):
    """Input the data of an actual Veggi Growing action"""
    #:id optional, in case of insert id is not present
    
    id = IntegerField(widget=HiddenInput(), validators=[Optional()])
    conception_id = IntegerField(widget=HiddenInput(), validators=[Optional()])
    fraction_id = IntegerField(widget=HiddenInput())
    product_id = IntegerField(widget=HiddenInput())
    year_of_growth = IntegerField(widget=HiddenInput())
    
    name = StringField(u'Benamung', validators=[DataRequired(), Length(max=128)])
    diversity_id = SelectField(u'Sorte', choices=[], coerce=int, validators=[my_select_validator])
    area_id = SelectField(u'Schlag', choices=[], coerce=int, validators=[my_select_validator])
    company_id = SelectField('Adresse',choices=[], coerce=int, validators=[my_select_validator])
    
    art_of_cultivation = SelectField(label=None, choices=[], validators=[Optional()])
    grow_kind_id = SelectField(u'in der Anbauform', choices=[], coerce=int, validators=[my_select_validator])
    amount_of_grow_kind_units = IntegerField(u'x-mal', validators=[Optional()])
    
    hint = StringField(u'Bemerkung', validators=[Length(max=256)])
    #geoinfo_act = StringField()
    
    date_of_act_order = DateField(label=u'Bestellung Datum', format='%Y-%m-%d', render_kw={'size':'12'}, validators=[Optional()])
    date_of_act_deliver = DateField(label=u'Lieferung Datum', format='%Y-%m-%d', render_kw={'size':'12'}, validators=[Optional()])
    date_of_act_seeding = DateField(label=u'Aussaat Datum', format='%Y-%m-%d', render_kw={'size':'12'}, validators=[Optional()])
    date_of_act_germing = DateField(label=u'Auflaufen Datum', format='%Y-%m-%d', render_kw={'size':'12'}, validators=[Optional()])
    date_of_act_prickout = DateField(label=u'Pikieren Datum', format='%Y-%m-%d', render_kw={'size':'12'}, validators=[Optional()])
    date_of_act_planting = DateField(label=u'Pflanzung Datum', format='%Y-%m-%d', render_kw={'size':'12'}, validators=[Optional()])
    date_of_act_yilding = DateField(label=u'Erntebeginn Datum', format='%Y-%m-%d', render_kw={'size':'12'}, validators=[Optional()])
    date_of_act_removal = DateField(label=u'Räumung Datum', format='%Y-%m-%d', render_kw={'size':'12'}, validators=[Optional()])
    
    amount_of_plants = IntegerField(u'Pflanzenanzahl', validators=[Optional()])
    planting_interval = DecimalField(u'Pflanzabstand m', validators=[Optional()])
    length_of_field = DecimalField(u'Länge m', validators=[Optional()])
    square_of_field = FlexibleDecimalField(u'Fläche m²', validators=[Optional()])
    plants_per_square = DecimalField(u'Pfl./m²', validators=[Optional()])
    amount_of_seed = FlexibleDecimalField(u'Saatgutmenge', validators=[Optional()])
    unit_of_seed = SelectField(u'Saatguteinheit', choices=[], coerce=int, validators=[Optional()])
    #seed_spec  = StringField()
    note = TextAreaField(u'Notiz',render_kw={"rows": 4})


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()




class Acquisition_Retraction_Form(FlaskForm):
    """Eine Menge Product wird von einer Fraction zu einer anderen geschoben
    implementation_id should be a multiselect rendered as multiradio
    vehicle_id & vehicle_count validators=[Optional()] :because jquery can disable input, 
    but a by jquery disabled input do not validate in Wtforms thus bad optional() 
    """
    
    fraction_id = IntegerField('fractionID', validators=[DataRequired()])
    source_fraction_id = IntegerField('SourceFractionID', validators=[DataRequired()])
    
    aq_date = DateField(label=u'Datum', format="%Y-%m-%d", default=date.today, validators=[DataRequired()])
    product_id =  IntegerField('ProductID', validators=[DataRequired()])
    implementation_id = IntegerField('implementationID', validators=[Optional()])
    
    roughly_amount = BooleanField(label=u'ca.',default=False)
    amount = FlexibleDecimalField(label=u'Menge', validators=[DataRequired()])
    unit_id = SelectField(label=u'Mengeneinheit', coerce=int)
    
    no_tara = BooleanField(label=u'Tara',default=False,render_kw={'onchange':'tara_or_not()'})
    
    box_count = SelectField(label=u'Kistenanzahl', choices=[(i, i) for i in range(0,43)], coerce=int)
    box_id = SelectField(label=u'Kistenart',  choices=[], coerce=int) #can we css-style the options with render_kw/widget/subclass?
    
    vehicle_count = SelectField(label=u'Anzahl Vehikel', choices=[(i, i) for i in range(0,13)], coerce=int, validators=[Optional()])
    vehicle_id = SelectField(label=u'Vehikel',  choices=[], coerce=int ,validators=[Optional()])

    #implementation = MultiCheckboxField(u'Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
    
    alternate_amount = FlexibleDecimalField(label=u'alternative Mengenangabe', validators=[Optional()])
    alternate_unit_id = SelectField(label=u'alternative Mengeneinheit',  choices=[], coerce=int)
    
    additional_tara = FlexibleDecimalField(label=u'händisches Tara in Kg', validators=[Optional()])
    hint = StringField(u'Notiz', validators=[Optional(), Length(max=255)])

    #ticket = HiddenField('Ticket')
    
    #extend Form Validator TRUE for alternate_unit_id <> unit_id if alternate_amount > 0
    def validate(self):
        if not super().validate():
            return False
        result= True
        if self.alternate_amount.data :
            if self.alternate_unit_id.data == self.unit_id.data:
                self.unit_id.errors.append('Alternative Einheit muss verschieden sein.')
                self.alternate_unit_id.errors.append('Alternative Einheit muss verschieden sein.')
                result = False
        return result
    
    
    

