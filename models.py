#!/usr/bin/env python
# app/models.py
""" "Your Postgres Database to know, you must!"
SQLAlchemie-Reflection
the implicit Mapper is WTForm.field.name = DatabaseTable.columnName
flash messages from model?...hmm(5 updates,1 delete,2 inserts)
?implement Read-Write user_permission (AS postgres_role) here?
connect(*,attr.attr...) star?
"""

from flask import flash 
from flask_sqlalchemy import sqlalchemy
from sqlalchemy import create_engine, MetaData, text
import time
import decimal
engine = create_engine('postgresql://operator:theword@localhost/harvestpro', convert_unicode = True)#, echo = True)
metadata = MetaData(engine, reflect=True)

NO_CHOICE_VALUE = -1 #:int! HTML-SelectField-dummy-Value for: not chosen yet
NO_CHOICE_STRING = ''#:str! HTML-SelectField-dummy-String (placeholder for: 'please make your choice')

#-------------------------------------------------------------------#
# global helperfunction    
#-------------------------------------------------------------------#
def proxy2list(result_proxy):
    """returns all rows as list[ of dict{columnName:Value}, ]
    from a sqlalchemy row proxy (engine.execute('select....'))
    BEWARE: result_proxy will close after (fetchall)
    """
    print('>>>>>>>>>>>>>>>>>>>call proxy2list')
    z = [dict(zip(row.keys(), row))
            for row in result_proxy.fetchall()]
    
    #print(z)
    
    return z

def proxy2tab(result_proxy):
    """returns {dict of {columnName:[Value,]
    """
    print('>>>>>>>>>>>>>>>>>>>call proxy2tab')
    
    h = {key:[] for key in result_proxy.keys()}
    
    print(h)
    
    z = [dict(row)
            for row in result_proxy.fetchall()]
    print('------------------------z')
    print(z)
    
    return z





def wtform2sql_insert(wtform):
    """creates a insert.values dict 
    WTForm.field.data -> SQLAlchemie.MetaData.Table.insert().values(dict)
    we presume that crf-token is always the last wtform.Field
    useflow: htmlform submit -> WTForm.validate -> this. -> DB Insert
    returns dict of tupel(columnName, Value) 
    TODO: better
    """
    name_list = []
    value_list = []
    for field in wtform:
        #print( str(field.name)+"    "+str(field.data) +"     "+ str(type(field.data)))
        
        if field.data:
            name_list.append(field.name)
            value_list.append(field.data)
            
    result = dict (zip(name_list[:-1],value_list[:-1]))#crf_token is last
       
    #print(name_list[:-1])
    #print(value_list[:-1])
    #print('wtform2sql_insert>'+str(result)) 
    return result

def wtform2sql_update(wtform):
    """creates a update.values dict
    WTForm.field.data -> MetaData.Table.update().values(dict)
    we presume that crf-token is always the last wtform.Field
    returns dict of tupel(columnName, Value)
    """
    name_list = []
    value_list = []
    
    for field in wtform:
        if field.object_data != field.data:  #only values that have changed
            #print('>>>>>>>>>>>>>>>>>>>>>>')
            #print('obj '+field.name+':'+str(field.object_data)+'  data:'+str(field.data) )
            #print('<<<<<<<<<<<<<<<<<<<<<<')
            name_list.append(field.name)
            value_list.append(field.data)
            
    result = dict (zip(name_list[:-1],value_list[:-1]))#crf_token is last
    
    #print('wtform2sql_update>'+str(result)) 
    return result


def list2nested(data_list, new_list=None, lft=0, rgt=0):
    """data: list_of_dict a sql nested set DUMP with lft,rgt
    make me a(recursive) function to use later Jinja2 recursive <LI> loop.
    inside of dict is children: list of dicts
    (maybe compute inside the model where the user lives output JSON)

    first create datastructure
    then let data flow into it
    """
            

    
    

    
#-------------------------------------------------------------------#
# Planing the vegetables gardening actions
#-------------------------------------------------------------------#

class VegetablesConceptionModel(object):
    """querys to display conceptions of Vegetable growing
    TODO:create_Type_with_sorting(Week_Year) in viename substitude sort_week with sort_week_year
        
    """
    def __init__(self):
        
        self._tablename_ = 'veg_conception'
        self._viewname_ = 'veg_conception_display'
        self._table = metadata.tables[self._tablename_]
        self._farmland_area_table_ ='hvp_farmland_and_areas'
        self._grow_kinds_table_='hvp_grow_kinds'
        self._diversity_table_='hvp_diversity_of_sorts'
                   
        ## select strings to be UNION ALL later  in FUNCTION.EX_PLAN
        ## with mutch formating suff like concat and add strings
        ## setting 'S','P','E' AS event TODO: remove anything with implementation
        

        #:selecting seed events
        self.plan_seed_sql= " SELECT id, hint, square_of_field, area_name,CONCAT(COALESCE(CAST(amount_of_grow_kind_units AS text),' '),' ', COALESCE(growkind_name,' ') )AS growkind, length_of_field, plants_per_square, CONCAT (COALESCE(CAST(amount_of_plants AS text),' '),'/',COALESCE(CAST(amount_of_seed AS text),' ')) AS count_seed, CAST('S' AS character) AS event, week_of_plan_seed AS week, COALESCE(CAST(date_of_plan_seed AS text),'') AS diem, name,  CONCAT(COALESCE(diversity_name,''),' ',COALESCE(diversity_ident,'')) AS diversity, note, implementation_seeding_date AS imp_date, implementation_id AS imp_id FROM "+self._viewname_+" WHERE week_of_plan_seed IS NOT NULL AND fraction_id IN (SELECT * FROM ext_fraction( :fraction)) AND year_of_growth = :cultivation_year "
        
        #:SELECTing implant events
        self.plan_plant_sql=" SELECT id, hint, square_of_field, area_name,CONCAT(COALESCE(CAST(amount_of_grow_kind_units AS text),' '),' ', COALESCE(growkind_name,' '),' | ',COALESCE(CAST(planting_interval AS text),'')) AS growkind, length_of_field, plants_per_square, CONCAT (COALESCE(CAST(amount_of_plants AS text),' '),'/',COALESCE(CAST(amount_of_seed AS text),' ')) AS count_seed, CAST('P' AS character) AS event, week_of_plan_plant AS week, COALESCE(CAST(date_of_plan_plant AS text),'') AS diem, name,  CONCAT(COALESCE(diversity_name,''),' ',COALESCE(diversity_ident,'')) AS diversity , note, implementation_planting_date AS imp_date, implementation_id AS imp_id FROM "+self._viewname_+" WHERE week_of_plan_plant IS NOT NULL AND fraction_id IN (SELECT * FROM ext_fraction( :fraction)) AND year_of_growth = :cultivation_year "

        #:SELECTing harvest events
        self.plan_crop_sql= " SELECT id, hint, square_of_field, area_name,CONCAT(COALESCE(CAST(amount_of_grow_kind_units AS text),' '),' ', COALESCE(growkind_name,' ')) AS growkind, length_of_field, plants_per_square, CONCAT (COALESCE(CAST(amount_of_plants AS text),' '),'/',COALESCE(CAST(amount_of_seed AS text),' ')) AS count_seed, CAST('E' as character) AS event, week_of_plan_crop AS week, COALESCE(CAST(date_of_plan_crop AS text),'') AS diem, name,  CONCAT(COALESCE(diversity_name,''),' ',COALESCE(diversity_ident,'')) AS diversity , ' ', implementation_yilding_date AS imp_date, implementation_id AS imp_id  FROM "+self._viewname_+" WHERE week_of_plan_crop IS NOT NULL AND fraction_id IN (SELECT * FROM ext_fraction( :fraction)) AND year_of_growth = :cultivation_year "

    def insert(self,wtform):
        """insert WTForm.data into reflected table
        using the SQL-Alchemy Core Syntax
        """
        
        sql_insert_string = self._table.insert().values(wtform2sql_insert(wtform))
        
        self._table.insert().values(wtform2sql_insert(wtform))
        #print ('insertstring:'+str(sql_insert_string))
        data = engine.execute(sql_insert_string)
        new_id = data.inserted_primary_key[0]
        
        return new_id
    
    def update(self, wtform, at_id):
        """update reflected table where id=at_id with WTForm.data
        using the SQL-Alchemy Core Syntax
        """
        values = wtform2sql_update(wtform)
        if len(values) == 0: #WTForm.data has not changed
            return 0
        else:
            sql_update_string = self._table.update().where(self._table.c.id==at_id).values(values)
            data = engine.execute(sql_update_string)
            return data.rowcount
        
    def get(self, fraction_id, cultivation_year):
        """list of all planned conceptions"""
        sql = "SELECT * FROM "+self._viewname_+" "\
              "WHERE year_of_growth = :cultivation_year "\
              "AND fraction_id= :fraction "\
              "ORDER BY sort_week, item_name;"

        data =  engine.execute(text(sql), cultivation_year = cultivation_year, 
                                      fraction = fraction_id)
        return proxy2list(data)

    def delete(self, at_id):
        """ remove one row at at_id
        success by returnvalue=1
        """
        sql_delete_string = self._table.delete().where(self._table.c.id==at_id)
        data = engine.execute(sql_delete_string)
        return data.rowcount
    
    def last_modified(self, fraction_id, year_of_growth):
        """max(last_modified) from what set (roles)
        ext_fraction(), only Table inheritance can do this
        the common ground on any conceptum
        return one row as a dict
        """
        sql = "SELECT MAX(last_modified) AS last_modified \
            FROM "+self._tablename_+" \
            WHERE fraction_id=:fraction_id \
            AND year_of_growth=:year_of_growth;"
        data = engine.execute(text(sql), fraction_id=fraction_id,
                              year_of_growth=year_of_growth)
        
        return proxy2list(data)[0]
    
    def get_overview(self, fraction_id, year_of_growth, area_id=None):
        """get plan-info group by products.
        for every product a sum_up of planing facts,
        used in index Card element
        """
        sql = "SELECT product_id,\
        item_name,\
        fraction_id,\
        year_of_growth,\
        count(product_id) AS count_of_sets,\
        sum(square_of_field) AS qm,\
        min(sort_week) AS min_week,\
        max(sort_week) AS max_week,\
        sum(amount_of_plants) AS count_of_plants\
        FROM "+self._viewname_+" \
        WHERE fraction_id=:fraction_id \
        AND year_of_growth=:year_of_growth "
        if area_id:
            sql += " AND area_id=:area_id "
        
        sql += " GROUP BY product_id,item_name,fraction_id,year_of_growth \
        ORDER BY item_name;"
        data = engine.execute(text(sql), fraction_id=fraction_id,
                              year_of_growth=year_of_growth,area_id=area_id)
        return proxy2list(data)
        
    def get_overview_summary(self, fraction_id, year_of_growth):
        """generall infos about planing per fraction per year
        returns one row
        """
        sql = "SELECT COUNT(DISTINCT(product_id)) AS count_products, \
        COUNT(DISTINCT(diversity_id)) AS count_diversitys, \
        SUM(square_of_field) AS sum_square \
        FROM "+self._tablename_+" \
        WHERE fraction_id=:fraction_id \
        AND year_of_growth=:year_of_growth;"
        data = engine.execute(text(sql), fraction_id=fraction_id,
                              year_of_growth=year_of_growth)
        return proxy2list(data)[0]
        
    
    def get_by_id(self, conception_id):
        """table data of one set"""
        sql = "SELECT * FROM "+self._tablename_+" WHERE id=:conception_id;"
        data = engine.execute(text(sql), conception_id = conception_id)
        return proxy2list(data)[0]
            
    def make_empty_new(self,fraction_id, year_of_growth, product_id):
        """inserts count new entries into conception Table
        formular count, min_week, max_week
        write a postgres procedure!
        select already_count 
        select already product name
        set name = productnameX, X=already_count+1 , ...,already_count+count  
        set step_weeks = count modulo (max_week-min_week)?
        """
        pass


    def get_product_by_id(self, fraction_id, year_of_growth, product_id):
        """ get almost any information about all conceptions (Sätze) of ONE product
        of one fraction's of one year
        TODO ext_fraction
        """
        sql = "SELECT * FROM "+self._viewname_+" WHERE fraction_id=:fraction_id AND year_of_growth=:year_of_growth AND product_id=:product_id ORDER by sort_week;"
        data = engine.execute(text(sql), fraction_id=fraction_id,
                             year_of_growth=year_of_growth,
                             product_id=product_id)
        return proxy2list(data)
    
    def get_micro_by_product_id(self, fraction_id, year_of_growth, product_id):
        """ retrieve some basic data about all conceptions (Sätze) of ONE
        product per fraction and year
        HARDCODED Table name
        fast table query
        ORDER same  as veg_conception_display definition but with different results
        """
        starttime=time.time()
        sql = "SELECT VI.id AS imp_id, \
                VC.name,\
                FA.our_name,\
                VC.id,\
                VC.amount_of_plants,\
                VC.hint, \
                VC.week_of_plan_seed, VC.week_of_plan_plant,vc.square_of_field, \
                DS.name AS diversity_name, DS.ident \
                FROM "+self._tablename_+"  AS VC\
                LEFT JOIN "+self._diversity_table_+" AS DS ON diversity_id = DS.id \
                LEFT JOIN "+self._farmland_area_table_+" AS FA ON area_id = FA.id \
                LEFT JOIN veg_implementation AS VI  ON VC.id = VI.conception_id \
                WHERE VC.fraction_id=:fraction_id \
                AND VC.year_of_growth=:year_of_growth \
                AND VC.product_id=:product_id \
                ORDER by  CASE \
                    WHEN week_of_plan_seed IS NULL THEN week_of_plan_plant \
                    WHEN week_of_plan_plant IS NULL THEN week_of_plan_seed \
                    ELSE week_of_plan_seed \
                END"
        
        data = engine.execute(text(sql), fraction_id=fraction_id,
                             year_of_growth=year_of_growth,
                             product_id=product_id)
        endtime = time.time() #performence time end
        print('Performence VegetablesConceptionModel.get_micro_by_product_id:'+str(endtime-starttime)+'sec.')
        return proxy2list(data)
    
      
      
    def ex_plan(self, fraction_id, cultivation_year, ):
        """select for exel, very table style"""
        sql = "WITH union_weeks AS( "
        sql += self.plan_seed_sql
        sql += " UNION ALL "
        sql += self.plan_plant_sql
        sql += " UNION ALL "
        sql += self.plan_crop_sql
        sql += " )SELECT * FROM union_weeks ORDER BY week, area_name, name "
        
        data = engine.execute(text(sql), cultivation_year=cultivation_year,
                             fraction=fraction_id)
                             
        return proxy2list(data)
    
    def get_summary_by_id(self, fraction_id, year_of_growth, product_id):
        """ runing some sum() avg() over all growingSet's (Sätze) of one year and product
        
        """
        sql =  'SELECT COUNT(vg.id) AS count_of_sets,\
               SUM (vg.square_of_field) AS sum_square_of_field,\
               SUM (vg.amount_of_plants) AS sum_amount_of_plants, \
               SUM (vg.amount_of_grow_kind_units * gk.growlines * vg.length_of_field) AS sum_length_of_growlines \
               FROM '+self._tablename_+' AS vg \
               LEFT JOIN '+self._grow_kinds_table_+' AS gk ON vg.grow_kind_id= gk.id \
               WHERE vg.fraction_id=:fraction_id \
               AND vg.year_of_growth=:year_of_growth \
               AND vg.product_id=:product_id ;'
               
        data = engine.execute(text(sql), fraction_id=fraction_id,
                              year_of_growth=year_of_growth,
                              product_id=product_id)
        return proxy2list(data)[0]#one row
    
    
      
    def get_involved_areas(self, fraction_id, year_of_growth):
        """areas involved in the planing
        select distinct veg_conception.area_id,
veg_conception.fraction_id,
veg_conception.year_of_growth,
sum(veg_conception.square_of_field),
hvp_farmland_and_areas.squarunits,
hvp_farmland_and_areas.our_name
 from veg_conception
left join hvp_farmland_and_areas on(veg_conception.area_id = hvp_farmland_and_areas.id)
 where veg_conception.fraction_id=2 and veg_conception.year_of_growth=2015
group by area_id,veg_conception.fraction_id,veg_conception.year_of_growth,hvp_farmland_and_areas.squarunits,hvp_farmland_and_areas.our_name
        """
        starttime=time.time()
        sql='SELECT DISTINCT '+self._tablename_+'.area_id,\
            '+self._tablename_+'.fraction_id, \
            '+self._tablename_+'.year_of_growth, \
            SUM('+self._tablename_+'.square_of_field) AS square_of_field, \
            '+self._farmland_area_table_+'.squarunits, \
            '+self._farmland_area_table_+'.our_name \
            FROM '+self._tablename_+' \
            LEFT JOIN '+self._farmland_area_table_+' \
            ON('+self._tablename_+'.area_id = '+self._farmland_area_table_+'.id) \
            WHERE '+self._tablename_+'.fraction_id=:fraction_id \
            AND '+self._tablename_+'.year_of_growth=:year_of_growth \
            GROUP BY area_id, \
            '+self._tablename_+'.fraction_id, \
            '+self._tablename_+'.year_of_growth, \
            '+self._farmland_area_table_+'.squarunits, \
            '+self._farmland_area_table_+'.our_name \
            ORDER BY '+self._farmland_area_table_+'.our_name;'
        
        data = engine.execute(text(sql), fraction_id=fraction_id,
                              year_of_growth=year_of_growth)
        endtime = time.time() #performence time end
        print('Performence VegetablesConceptionModel.get_involved_areas:'+str(endtime-starttime)+'sec.')
        return proxy2list(data)
      

    #def area(self, fraction_id, year_of_growth, area_id=None):
        
        
    def lock_entrie(self, at_id):
        """ set archived flag: is_locked=true"""
        sql = 'UPDATE '+self._tablename_+ ' SET \
        is_locked=True, lock_date=now() WHERE id=:at_id;'
        
        data= engine.execute(text(sql),at_id=at_id)
        return data.rowcount
      
    def conception_culture(self, fraction_id, year_of_growth):
        """Zusammenfassung aller Kulturen auf Flächen
        tabellarische Form
        """
        sql = 'SELECT product_id,item_name,growkind_name,area_name,SUM(square_of_field) AS qm,SUM(amount_of_plants) AS sumplants, SUM( amount_of_grow_kind_units * length_of_field) AS length from veg_conception_display WHERE fraction_id=:fraction_id AND year_of_growth =:year_of_growth GROUP BY product_id,item_name,growkind_name,area_name order by area_name'
        
        data = engine.execute(text(sql), fraction_id=fraction_id,
                              year_of_growth=year_of_growth)
        return proxy2list(data)
      
    def conception_field(self, fraction_id, year_of_growth, area_id=None):
        """demand on prepared ground per week and field"""
        sql = 'SELECT area_id, grow_kind_id, area_name, growkind_name, sort_week, \
        SUM(square_of_field) AS qm, SUM((amount_of_grow_kind_units * length_of_field)) AS length \
        FROM veg_conception_display \
        WHERE fraction_id =:fraction_id \
        AND year_of_growth =:year_of_growth '
        if area_id != None :
            sql += ' AND area_id =:area_id '
        sql += ' GROUP BY sort_week, area_id, grow_kind_id, area_name, growkind_name \
        ORDER BY sort_week, area_name '
        
        data = engine.execute(text(sql), fraction_id=fraction_id,
                              year_of_growth=year_of_growth,
                              area_id=area_id)
        return proxy2list(data)


    def buy(self, fraction_id, cultivation_year):
        """only  plant_purchase  no seedig or HARDCODED art_of_cultivation=plant_purchase"""
        sql = "SELECT id,name,hint,week_of_plan_plant,item_name,diversity_name,diversity_ident,amount_of_plants FROM "+self._viewname_+" WHERE fraction_id IN (SELECT * FROM ext_fraction(:fraction)) AND year_of_growth= :year AND ((date_of_plan_seed is NULL AND week_of_plan_seed is NULL) OR (art_of_cultivation='plant_purchase')) Order by sort_week, item_name"
        data = engine.execute(text(sql), year=cultivation_year,
                             fraction=fraction_id)
        return proxy2list(data)
    
    def seed(self, fraction_id, cultivation_year):
        """ all seedings """
        sql = "SELECT * FROM "+self._viewname_+" WHERE fraction_id IN (SELECT * FROM ext_fraction( :fraction)) AND year_of_growth= :year AND (date_of_plan_seed is NOT NULL OR week_of_plan_seed is NOT NULL) Order by sort_week, item_name"
        
        data = engine.execute(text(sql), year=cultivation_year,
                             fraction=fraction_id)
        
        return proxy2list(data)
    
    def implant(self, fraction_id, cultivation_year):
        """ all implantings TODO ext_fraction"""
        sql = "SELECT * FROM "+self._viewname_+" WHERE fraction_id=:fraction_id AND year_of_growth=:cultivation_year AND week_of_plan_plant IS NOT NULL ORDER BY week_of_plan_plant, name "
        data = engine.execute(text(sql), fraction_id=fraction_id,
                              cultivation_year=cultivation_year)
        return proxy2list(data)

    
#-------------------------------------------------------------------#
# Implementation: actual veggie gardening facts
#-------------------------------------------------------------------#

class VegetablesImplementationModel(object):
    """
    Veggigardening actualy growings
    self.events('S','P','E','R') from 'veg_implementation_display'
    """
    def __init__(self):
        self._tablename_ = 'veg_implementation'
        self._viewname_ = 'veg_implementation_display'
        self._table = metadata.tables[self._tablename_]
        self._farmland_area_table_ ='hvp_farmland_and_areas'
        self._grow_kinds_table_='hvp_grow_kinds'
        
    def get(self, fraction_id, year_of_growth):
        #
        sql = "SELECT * FROM "+self._viewname_+"  WHERE fraction_id=:fraction_id AND year_of_growth=:year_of_growth ORDER by sort_date"
        print(sql)
        data = engine.execute(text(sql), fraction_id=fraction_id,
                             year_of_growth=year_of_growth)
        
        return proxy2list(data)
    
    def insert(self,wtform):
        """insert WTForm.data into reflected table
        using SQL-Alchemie Core syntax
        """
        sql_insert_string = self._table.insert().values(wtform2sql_insert(wtform))
        data = engine.execute(sql_insert_string)
        new_id = data.inserted_primary_key[0]
        
        return new_id
    
    def update(self, wtform, at_id):
        """update reflected table where id=at_id with WTForm.data
        using the SQL-Alchemy Core Syntax
        """        
        values = wtform2sql_update(wtform)
        if len(values) == 0: #WTForm.data has not changed
            return 0
        else:
            sql_update_string = self._table.update().where(self._table.c.id==at_id).values(values)
            data = engine.execute(sql_update_string)
            return data.rowcount
        
        
        
    def get_by_id(self, implementation_id):
        """table data of one set"""
        sql = "SELECT * FROM "+self._tablename_+" WHERE id=:implementation_id;"
        data = engine.execute(text(sql), implementation_id = implementation_id)
        return proxy2list(data)[0]    
    
    def year(self):
        #displayView = Table('ponderato_display',metadata,autoload=True)
        #con = engine.connect()
        data = engine.execute("SELECT * FROM "+self._viewname_+" where fraction_id=2 AND  year_of_growth=2016 ORDER by sort_date")
        return data 
    
    def get_product_by_id(self, fraction_id, year_of_growth, product_id):
        sql ="SELECT * FROM "+self._viewname_+" WHERE fraction_id=:fraction_id AND year_of_growth=:year_of_growth AND product_id=:product ORDER by sort_date"
        data = engine.execute(text(sql), fraction_id=fraction_id,
                              year_of_growth=year_of_growth,
                              product=product_id)
        
        return proxy2list(data)
    
    def get_overview(self, fraction_id, year_of_growth, area_id=None):
        """get realisation-facts group by products.
        used in index.html card element"""
        sql = "SELECT product_id,\
        item_name,\
        fraction_id,\
        year_of_growth,\
        count(product_id) AS count_of_sets,\
        sum(square_of_field) AS qm,\
        min(sort_date) AS min_date,\
        max(sort_date) AS max_date,\
        sum(amount_of_plants) AS count_of_plants\
        FROM "+self._viewname_+" \
        WHERE fraction_id=:fraction_id \
        AND year_of_growth=:year_of_growth "
        if area_id:
            sql += " AND area_id=:area_id "
        
        sql += " GROUP BY product_id,item_name,fraction_id,year_of_growth \
        ORDER BY item_name;"   
        print(sql)
        data = engine.execute(text(sql), fraction_id=fraction_id,
                              year_of_growth=year_of_growth,area_id=area_id)
        return proxy2list(data)        

    def get_summary_by_id(self, fraction_id, year_of_growth, product_id):
        """ runing some sum() avg() over all growingSet's (Sätze) of one year and product
        
        """
        sql =  'SELECT COUNT(vg.id) AS count_of_sets,\
               SUM (vg.square_of_field) AS sum_square_of_field,\
               SUM (vg.amount_of_plants) AS sum_amount_of_plants, \
               SUM (vg.amount_of_grow_kind_units * gk.growlines * vg.length_of_field) AS sum_length_of_growlines, \
               MAX (vg.last_modified) AS last_modified \
               FROM '+self._tablename_+' AS vg \
               LEFT JOIN '+self._grow_kinds_table_+' AS gk ON vg.grow_kind_id= gk.id \
               WHERE vg.fraction_id=:fraction_id \
               AND vg.year_of_growth=:year_of_growth \
               AND vg.product_id=:product_id ;'
               
        data = engine.execute(text(sql), fraction_id=fraction_id,
                              year_of_growth=year_of_growth,
                              product_id=product_id)
        return proxy2list(data)[0]#one row        
        
#-------------------------------------------------------------------#
# FRACTION or the Department
# 
# (hvp_fractions, Fraktionen, faction, fractus, fractum mundi)
#
#-------------------------------------------------------------------#
class FractionModel(object):
    """ departments of stuff, this is the key point
    everything is organized in fractions: people,(trans)actions
    the root fraction's PKid is (the autoinkrement) 0 (Zero)
    
    attributes: fraction_id: integer primary key
                name: string
                product_tree_id: points to a nested set of product_id as default(hvp_const_base)
                area_tree_id: points to a nested set of farmland_and_areas.id as default(hvp_const_base)
                children: list[] of dict(fraction_id, name, product_tree_id)
                parent: one dict(fraction_id, name, product_tree_id)
    tablename is a adjacency list
    """
    def __init__(self, fraction_id):
        
        self._tablename_ = 'hvp_fractions'
        
        #query self basic attributes
        sql = "SELECT id, name, product_tree_id, area_tree_id \
        FROM "+self._tablename_+" \
        WHERE id=%s ;" %(fraction_id)
                
        row = engine.execute(sql).first()
        
        if row:
            print('fractionInit.FractionAreaTreeId:'+ str(row['area_tree_id']))
            self.area = AreaModel(row['area_tree_id']) #should i do this? bind a 'object here'
            
            self.fraction_id = row["id"]
            
            self.name = row['name']
            
            self.product_tree_id = row['product_tree_id']
            
            #self.product_list = self.get_productlist(self.product_tree_id, product_id='NULL')
            #print('self:productlist') 
            
            #query the parent
            sql = "WITH parentid AS( SELECT parent_id \
            FROM "+self._tablename_+" \
            WHERE id=:fraction_id ) \
            SELECT id, name, product_tree_id  \
            FROM "+self._tablename_+" \
            WHERE id= (select parent_id from parentid);"
            
            data = engine.execute(text(sql), fraction_id=self.fraction_id)
            
            row = data.first()
            if row:
                #: fraction's parent if any
                self.parent ={'fraction_id':row['id'],
                              'name':row['name'],
                              'product_tree_id':row['product_tree_id']}
            else:
                self.parent = False

            
            
            
            # query the immediate children
            sql = "SELECT id, name, product_tree_id \
            FROM "+self._tablename_+" \
            WHERE parent_id=%s ;" %(self.fraction_id)
            
            data = engine.execute(sql)
            
            self.children = [ dict(fraction_id=row['id'],
                                   name=row['name'],
                                   product_tree_id=row['product_tree_id'])
                             for row in data.fetchall() ]
            
            #asdf = listwrl2nested(self.get_product_list())
            #for item in asdf:
                #print(str(item['lft'])+'/'+str(item['rgt']))
            

        
        
    def get_product_list(self, product_tree_id=None, product_id='NULL'):
        """the producttree as nestet set dump (.lft,.rgt) order by left
        calling the postgres ptree function
        
        
        TODO:@user_product_tree-decorator(?)    
        TODO:the user's very special fraction product treeId
        """
        if product_tree_id:
            #very special product_tree_id, if not exist 
            #the postgres function falls back to fraction default product_tree_id
            print(" IF product_tree_id !")
            sql = "SELECT * FROM ptree('%s',%s,%s);"%(product_tree_id,
                                                      self.fraction_id,
                                                      product_id)
        else:
            #fraction default product_tree_id
            print(" ELSE product_tree_id ")
            sql = "SELECT * FROM ptree('%s',%s,%s);"%(self.product_tree_id,
                                                      self.fraction_id,
                                                      product_id)
        print(sql)    
        data = engine.execute(sql)
        
        # print(proxy2list(data))#print() kills the proxy
        
        #l = proxy2list(data)
        #d = l[0]
        #res = list2nested(l)
        #TODO implement list2nested()
        #res = cheetamenue()
        
        #return res
        return proxy2list(data)

    
    def get_first_product_list(self):
        """get only the first level of the product_tree
        products level == 1 of the producttree,
        call the postgres ptree() function
        
        TODO:@user_product_tree-decorator(?)()the user's very special fraction product treeId
        
        """

        sql = "SELECT * FROM ptree('%s',%s,NULL) WHERE levl=1;"%(self.product_tree_id,self.fraction_id)
        data = engine.execute(sql)
        #print ("get_first_product_list ok")
        #print(proxy2list(data)) #print() kills the proxy
        return proxy2list(data)
   
    
    def map_ptree_results(self, db_result):
        """helperfunction to map select*ptree() function results
        result set (return table as) is constant
        (but never map manualy!)
        """
        pass
        return 

    def cheata_menue(self): 
        """ das ist cheat für die funktion list2nested()
        """
    
        d = [{'item_name': 'Baldriangewächse', 'name_lat': 'Valerianoideae', 'product_id': 1000, 'lft': 2, 'rgt': 5, 'i_size': 1, 'levl': 1, 'has_data': -1, 'children': [
{'item_name': 'Feldsalat', 'name_lat': 'Valerianella locusta', 'product_id': 104000, 'lft': 3, 'rgt': 4, 'i_size': 0, 'levl': 2, 'has_data': 2}] 
 }, {'item_name': 'Doldenblütler', 'name_lat': 'Apiaceae', 'product_id': 2000, 'lft': 6, 'rgt': 23, 'i_size': 8, 'levl': 1, 'has_data': -1, 'children':[
{'item_name': 'Sellerie-Knolle', 'name_lat': 'Apium graveolens L. var. rapaceum', 'product_id': 102000, 'lft': 7, 'rgt': 8, 'i_size': 0, 'levl': 2, 'has_data': 2},
{'item_name': 'Knollenfenchel', 'name_lat': 'Foeniculum vulgare Mill. var. azoricum', 'product_id': 103000, 'lft': 9, 'rgt': 10, 'i_size': 0, 'levl': 2, 'has_data': 2},
{'item_name': 'Sellerie mit Grün', 'name_lat': '', 'product_id': 126000, 'lft': 11, 'rgt': 12, 'i_size': 0, 'levl': 2, 'has_data': 2},
{'item_name': 'Möhre', 'name_lat': 'Daucus carota L.', 'product_id': 135000, 'lft': 13, 'rgt': 14, 'i_size': 0, 'levl': 2, 'has_data': 2},
{'item_name': 'Pastinake', 'name_lat': 'Pastinaca sativa L.', 'product_id': 136000, 'lft': 15, 'rgt': 16, 'i_size': 0, 'levl': 2, 'has_data': 2},
{'item_name': 'Petersilie', 'name_lat': 'Petroselinum crispum', 'product_id': 147000, 'lft': 17, 'rgt': 18, 'i_size': 0, 'levl': 2, 'has_data': 2},
{'item_name': 'Wurzel-Petersilie', 'name_lat': 'Petroselinum crispum subsp. tuberosum', 'product_id': 148000, 'lft': 19, 'rgt': 20, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Dill', 'name_lat': 'Anethum graveolens', 'product_id': 174000, 'lft': 21, 'rgt': 22, 'i_size': 0, 'levl': 2, 'has_data': 2}]
}, {'item_name': 'Gänsefußgewächse', 'name_lat': 'Chenopodiaceae', 'product_id': 3000, 'lft': 24, 'rgt': 33, 'i_size': 4, 'levl': 1, 'has_data': -1, 'children': [
{'item_name': 'Mangold', 'name_lat': 'Beta vulgaris L. ssp. vulgaris', 'product_id': 122000, 'lft': 25, 'rgt': 26, 'i_size': 0, 'levl': 2, 'has_data': 2},
{'item_name': 'Mangold DO_NOT_USE', 'name_lat': 'Beta vulgaris L. ssp. vulgaris', 'product_id': 123000, 'lft': 27, 'rgt': 28, 'i_size': 0, 'levl': 2, 'has_data': 2},
{'item_name': 'Spinat', 'name_lat': 'Spinacia oleracea L.', 'product_id': 124000, 'lft': 29, 'rgt': 30, 'i_size': 0, 'levl': 2, 'has_data': 2},
{'item_name': 'Rote Rübe', 'name_lat': 'Beta vulgaris L. ssp. vulgaris var. conditiva Alef.', 'product_id': 125000, 'lft': 31, 'rgt': 32, 'i_size': 0, 'levl': 2, 'has_data': 2}]
}, {'item_name': 'Korbblütler', 'name_lat': 'Asteraceae', 'product_id': 4000, 'lft': 34, 'rgt': 63, 'i_size': 14, 'levl': 1, 'has_data': -1, 'children': [
{'item_name': 'Sommersalat', 'name_lat': 'Lactuca sativa', 'product_id': 4200, 'lft': 35, 'rgt': 50, 'i_size': 7, 'levl': 2, 'has_data': 2, 'children': [
{'item_name': 'BabyLeaf', 'name_lat': '(Lactuca sativa)', 'product_id': 127000, 'lft': 36, 'rgt': 37, 'i_size': 0, 'levl': 3, 'has_data': 2},
{'item_name': 'Eichblatt', 'name_lat': 'Lactuca sativa L. var. crispa', 'product_id': 128000, 'lft': 38, 'rgt': 39, 'i_size': 0, 'levl': 3, 'has_data': 2},
{'item_name': 'Eissalat', 'name_lat': 'Lactuca sativa L. var. capitata', 'product_id': 128100, 'lft': 40, 'rgt': 41, 'i_size': 0, 'levl': 3, 'has_data': 2},
{'item_name': 'Bataviasalat', 'name_lat': 'Lactuca sativa L. var. capitata', 'product_id': 128200, 'lft': 42, 'rgt': 43, 'i_size': 0, 'levl': 3, 'has_data': 2}, 
{'item_name': 'Romanasalat', 'name_lat': 'Lactuca sativa l. var. romana', 'product_id': 128300, 'lft': 44, 'rgt': 45, 'i_size': 0, 'levl': 3, 'has_data': 2},
{'item_name': 'Lollosalat', 'name_lat': 'Lactuca sativa L. var. crispa', 'product_id': 128400, 'lft': 46, 'rgt': 47, 'i_size': 0, 'levl': 3, 'has_data': 2},
{'item_name': 'Kopfsalat', 'name_lat': 'Lactuca sativa L. var. capitata', 'product_id': 129000, 'lft': 48, 'rgt': 49, 'i_size': 0, 'levl': 3, 'has_data': 2}]
}, {'item_name': 'Endivie', 'name_lat': 'cichorium endivia L.', 'product_id': 106000, 'lft': 51, 'rgt': 52, 'i_size': 0, 'levl': 2, 'has_data': 2},
{'item_name': 'Radicchio', 'name_lat': 'Cichorium intybus var. foliosum', 'product_id': 149000, 'lft': 53, 'rgt': 54, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Zuckerhut', 'name_lat': 'Cichorium intybus var. foliosum', 'product_id': 150000, 'lft': 55, 'rgt': 56, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Topinambur', 'name_lat': 'Helianthus tuberosus', 'product_id': 167000, 'lft': 57, 'rgt': 58, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Haferwurzel', 'name_lat': 'Tragopogon porrifolius L.', 'product_id': 101100, 'lft': 59, 'rgt': 60, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Schwarzwurzel', 'name_lat': 'Scorzonera hispanica L.', 'product_id': 101200, 'lft': 61, 'rgt': 62, 'i_size': 0, 'levl': 2, 'has_data': 2}] 
},{'item_name': 'Gräser', 'name_lat': '(Poaceae)', 'product_id': 5000, 'lft': 64, 'rgt': 69, 'i_size': 2, 'levl': 1, 'has_data': -1, 'children' :[ 
{'item_name': 'Zuckermais', 'name_lat': 'Zea Mays L. convar. saccharata Koern.', 'product_id': 105000, 'lft': 65, 'rgt': 66, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Polentamais', 'name_lat': 'Zea mays var. tortoreto JW.', 'product_id': 105100, 'lft': 67, 'rgt': 68, 'i_size': 0, 'levl': 2, 'has_data': 2}]
}, {'item_name': 'Kreuzblütler', 'name_lat': 'Cruciferae', 'product_id': 6000, 'lft': 70, 'rgt': 109, 'i_size': 19, 'levl': 1, 'has_data': -1, 'children' : [ 
{'item_name': 'Grünkohl', 'name_lat': 'Brassica oleracea L. var.sabellica', 'product_id': 101000, 'lft': 71, 'rgt': 72, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Kohlrabi', 'name_lat': 'Brassica oleracea L. var. gangylodes', 'product_id': 107000, 'lft': 73, 'rgt': 74, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Weißkohl', 'name_lat': 'Brassica oleracea L. var. capitata f. alba', 'product_id': 108000, 'lft': 75, 'rgt': 76, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Rotkohl', 'name_lat': 'Brassica oleracea L. var. capitata f. rubra', 'product_id': 109000, 'lft': 77, 'rgt': 78, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Wirsing', 'name_lat': 'Brassica oleracea L. var. capitata f. sabauda', 'product_id': 110000, 'lft': 79, 'rgt': 80, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Radischen', 'name_lat': 'Raphanus sativus', 'product_id': 111000, 'lft': 81, 'rgt': 82, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Rosenkohl', 'name_lat': 'Brassica oleracea L.var. gemmifera', 'product_id': 112000, 'lft': 83, 'rgt': 84, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Asia-Salat', 'name_lat': '', 'product_id': 130000, 'lft': 85, 'rgt': 86, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Blumenkohl', 'name_lat': 'Brassica oleracea L. var botrytis L.', 'product_id': 131000, 'lft': 87, 'rgt': 88, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Brokkoli', 'name_lat': 'Brassica oleracea L. var. italica Plenck', 'product_id': 132000, 'lft': 89, 'rgt': 90, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Chinakohl', 'name_lat': 'Brassica rapa L. spp. pekinensis(L.)HaneltRettich', 'product_id': 133000, 'lft': 91, 'rgt': 92, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Rettich', 'name_lat': 'Raphanus sativus var. niger L.', 'product_id': 134000, 'lft': 93, 'rgt': 94, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Superschmelz', 'name_lat': '', 'product_id': 143000, 'lft': 95, 'rgt': 96, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Steckrübe', 'name_lat': 'Brassica napus subsp. rapifera', 'product_id': 144000, 'lft': 97, 'rgt': 98, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Stielmuß', 'name_lat': 'Brassica rapa var. rapifera subvar. pabularia', 'product_id': 151000, 'lft': 99, 'rgt': 100, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Spitzkohl', 'name_lat': 'Brassica oleracea convar.capitata var. alba', 'product_id': 157000, 'lft': 101, 'rgt': 102, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Mairübchen', 'name_lat': 'Brassica rapa L. var. rapifera', 'product_id': 158000, 'lft': 103, 'rgt': 104, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Rettisch-weiß (Daikon)', 'name_lat': '', 'product_id': 166000, 'lft': 105, 'rgt': 106, 'i_size': 0, 'levl': 2, 'has_data': 0}, 
{'item_name': 'Rauke/Rucola', 'name_lat': 'Eruca sativa-vesicaria', 'product_id': 175000, 'lft': 107, 'rgt': 108, 'i_size': 0, 'levl': 2, 'has_data': 2}]
} , {'item_name': 'Kürbisgewächse', 'name_lat': 'Cucurbitaceae', 'product_id': 7000, 'lft': 110, 'rgt': 119, 'i_size': 4, 'levl': 1, 'has_data': -1, 'children': [ 
{'item_name': 'Kürbis', 'name_lat': 'Cucurbita maxima Duch.', 'product_id': 113000, 'lft': 111, 'rgt': 112, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Zucchini', 'name_lat': 'Cucurbita pepo L.', 'product_id': 114000, 'lft': 113, 'rgt': 114, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Gurke-Schlange', 'name_lat': 'Cucumis sativus L.', 'product_id': 140000, 'lft': 115, 'rgt': 116, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Gurke-Mini', 'name_lat': '', 'product_id': 155000, 'lft': 117, 'rgt': 118, 'i_size': 0, 'levl': 2, 'has_data': 2}]
}, {'item_name': 'Liliengewächse', 'name_lat': 'Liliaceae', 'product_id': 8000, 'lft': 120, 'rgt': 133, 'i_size': 6, 'levl': 1, 'has_data': -1, 'children': [ 
{'item_name': 'Lauch (Porree)', 'name_lat': 'Allium porrum L. var. porrum', 'product_id': 115000, 'lft': 121, 'rgt': 122, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Zwiebel Lager', 'name_lat': 'Allium cepa L.', 'product_id': 137000, 'lft': 123, 'rgt': 124, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Knoblauch', 'name_lat': 'Allium sativum L.', 'product_id': 141000, 'lft': 125, 'rgt': 126, 'i_size': 0, 'levl': 2, 'has_data': 0}, 
{'item_name': 'Spargel', 'name_lat': 'Aspargus officinalis L.', 'product_id': 142000, 'lft': 127, 'rgt': 128, 'i_size': 0, 'levl': 2, 'has_data': 0}, 
{'item_name': 'Schnittlauch', 'name_lat': 'Allium schoenoprasum', 'product_id': 152000, 'lft': 129, 'rgt': 130, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Zwiebel Lauch', 'name_lat': 'Allium fistulosum L.', 'product_id': 154000, 'lft': 131, 'rgt': 132, 'i_size': 0, 'levl': 2, 'has_data': 2}] 
} , {'item_name': 'Nachtschattengewächse', 'name_lat': 'Solanaceae', 'product_id': 9000, 'lft': 134, 'rgt': 153, 'i_size': 9, 'levl': 1, 'has_data': -1, 'children' : [ 
{'item_name': 'Paprika', 'name_lat': 'Capsicum annuum L.', 'product_id': 116000, 'lft': 135, 'rgt': 136, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Tomate-Salat', 'name_lat': 'Solanum lycopersicum L. / Lycopersicon esculentum Mill.', 'product_id': 117000, 'lft': 137, 'rgt': 138, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Tomate-Coctail', 'name_lat': 'Lycopersicon esculentum Mill.', 'product_id': 118000, 'lft': 139, 'rgt': 140, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Tomate-Cerry', 'name_lat': 'Lycopersicon esculentum Mill.', 'product_id': 119000, 'lft': 141, 'rgt': 142, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Aubergine', 'name_lat': 'Solanum melongena L.', 'product_id': 138000, 'lft': 143, 'rgt': 144, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Kartoffel-mehlig', 'name_lat': 'solanum tuberosum', 'product_id': 145000, 'lft': 145, 'rgt': 146, 'i_size': 0, 'levl': 2, 'has_data': 0}, 
{'item_name': 'Kartoffel-vfk', 'name_lat': 'solanum tuberosum', 'product_id': 146000, 'lft': 147, 'rgt': 148, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Kartoffeln-früh', 'name_lat': 'solanum tuberosum', 'product_id': 156000, 'lft': 149, 'rgt': 150, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Tomaten - grün', 'name_lat': '', 'product_id': 165000, 'lft': 151, 'rgt': 152, 'i_size': 0, 'levl': 2, 'has_data': 0}]
}, {'item_name': 'Schmetterlingsblütler', 'name_lat': 'Faboideae', 'product_id': 10000, 'lft': 154, 'rgt': 169, 'i_size': 7, 'levl': 1, 'has_data': -1, 'children' :[ 
{'item_name': 'Buschbohne', 'name_lat': 'Phaseolus vulgaris L. var. nanus', 'product_id': 120000, 'lft': 155, 'rgt': 156, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Stangenbohne', 'name_lat': 'Phaseolus vulgaris L. ssp. vulgaris var. vulgaris', 'product_id': 139000, 'lft': 157, 'rgt': 158, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Dicke Bohne', 'name_lat': 'Vicia faba L.', 'product_id': 159000, 'lft': 159, 'rgt': 160, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Erbse', 'name_lat': 'Pisum sativum L.', 'product_id': 171000, 'lft': 161, 'rgt': 168, 'i_size': 3, 'levl': 2, 'has_data': -1, 'children' :[ 
{'item_name': 'Schalerbse', 'name_lat': 'Pisum sativum L. convar. sativum', 'product_id': 171100, 'lft': 162, 'rgt': 163, 'i_size': 0, 'levl': 3, 'has_data': 2}, 
{'item_name': 'Markerbse', 'name_lat': 'Pisum sativum L. convar medullare', 'product_id': 171200, 'lft': 164, 'rgt': 165, 'i_size': 0, 'levl': 3, 'has_data': 2}, 
{'item_name': 'Zuckererbse', 'name_lat': 'Pisum sativum L. convar. axiphium', 'product_id': 171300, 'lft': 166, 'rgt': 167, 'i_size': 0, 'levl': 3, 'has_data': 2}]
}
]
}, {'item_name': 'Schnittkräuter', 'name_lat': 'Lorem ipsum', 'product_id': 11000, 'lft': 170, 'rgt': 179, 'i_size': 4, 'levl': 1, 'has_data': -1, 'children': [ 
{'item_name': 'Tabak- sand', 'name_lat': 'Nicotiana', 'product_id': 162000, 'lft': 171, 'rgt': 172, 'i_size': 0, 'levl': 2, 'has_data': 0}, 
{'item_name': 'Tabak-mittel', 'name_lat': 'Nicotiana', 'product_id': 163000, 'lft': 173, 'rgt': 174, 'i_size': 0, 'levl': 2, 'has_data': 0}, 
{'item_name': 'Tabak-fein', 'name_lat': 'Nicotiana', 'product_id': 164000, 'lft': 175, 'rgt': 176, 'i_size': 0, 'levl': 2, 'has_data': 0}, 
{'item_name': 'Postelein', 'name_lat': 'Claytonia perfoliata', 'product_id': 168000, 'lft': 177, 'rgt': 178, 'i_size': 0, 'levl': 2, 'has_data': 2} ] 
},{'item_name': 'Knöterichgewächse', 'name_lat': 'Polygonaceae', 'product_id': 12000, 'lft': 180, 'rgt': 183, 'i_size': 1, 'levl': 1, 'has_data': -1, 'children': [ 
{'item_name': 'Rhabarber', 'name_lat': 'Rheum rhabarbarum', 'product_id': 153000, 'lft': 181, 'rgt': 182, 'i_size': 0, 'levl': 2, 'has_data': 2}]
}, {'item_name': 'Malvengewächse', 'name_lat': 'Malvaceae', 'product_id': 13000, 'lft': 184, 'rgt': 187, 'i_size': 1, 'levl': 1, 'has_data': -1, 'children':[ 
{'item_name': 'Gemüsemalve', 'name_lat': 'Malva verticillata', 'product_id': 172000, 'lft': 185, 'rgt': 186, 'i_size': 0, 'levl': 2, 'has_data': 2}]
}, {'item_name': 'Lippenblütler', 'name_lat': 'Lamiaceae', 'product_id': 14000, 'lft': 188, 'rgt': 193, 'i_size': 2, 'levl': 1, 'has_data': -1, 'children':[ 
{'item_name': 'Basilikum', 'name_lat': 'Ocimum basilicum', 'product_id': 121000, 'lft': 189, 'rgt': 190, 'i_size': 0, 'levl': 2, 'has_data': 2}, 
{'item_name': 'Bohnenkraut', 'name_lat': 'Satureja(hortense/montana)', 'product_id': 173000, 'lft': 191, 'rgt': 192, 'i_size': 0, 'levl': 2, 'has_data': 2}]
}]

        return d
    
        

        
        
        
      

#-------------------------------------------------------------------#
# define one PRODUCT by fraction
#-------------------------------------------------------------------#
class ProductModel(object):
    
    def __init__(self, product_id, fraction_id=0):
        """please if you have the fraction_id then provide it
        is product eine Propertie von Fraction?
        warum hab ich hier die ptree() function benutzt?
        """
        self.product_id = product_id
        self.fraction_id = fraction_id
    
    def get_data(self):
        """get the data of one product
        returns list of dict
        """
        starttime=time.time()
        print('calling product.get_data() product_id:'+str(self.product_id)+' , fraction_id:'+str(self.fraction_id))

        sql = "SELECT ptree.product_id AS product_id,\
            ptree.item_name AS item_name,\
            ptree.name_lat AS name_lat,\
            ptree.has_data AS has_data,\
            (ptree.rgt-ptree.lft) AS tree_diff,\
            pdata.fraction_id AS fraction_id,\
            pdata.unit_pivot_id AS unit_pivot_id,\
            pdata.units_set_id AS unit_set_id,\
            pdata.box_pivot_id AS box_pivot_id,\
            pdata.boxes_set_id AS boxes_set_id,\
            pdata.grow_kind_id AS grow_kind_id,\
            pdata.planting_interval AS planting_interval,\
            pdata.avg_duration_growth AS avg_duration_growth,\
            pdata.avg_duration_storage AS avg_duration_storage,\
            pdata.specific_density AS specific_density,\
            pdata.likes_statistic AS likes_statistic,\
            pdata.icon_a AS icon_a,\
            pdata.icon_b AS icon_b,\
            pdata.note AS note,\
            pdata.creation_date AS creation_date,\
            pdata.last_modified AS last_modified\
            FROM ptree(null,:fraction_id, :product_id)\
            LEFT JOIN hvp_all_products_data AS pdata\
            ON (ptree.product_id= pdata.product_id)\
            WHERE pdata.fraction_id=:fraction_id;"
            
        data = engine.execute(text(sql), fraction_id=self.fraction_id,
                       product_id=self.product_id)
        #print(str(data.keys()))
        if data:
            print('>>>>>>>product.gat_data has data and row_count is:'+str(data.rowcount))
            
            if data.returns_rows == False:
                print('>>>>>>>Proxy returns NO rows.')
        #print(proxy2list(data)) #this will clear the resultproxy  
        endtime=time.time()
        print('Performence product.getdata:'+str(endtime-starttime) +'sec')
        return proxy2list(data)[0]
    
#-------------------------------------------------------------------#
# Diversity of Sorts, one Product's variety
#-------------------------------------------------------------------#
class DiversityModel(object):
    def __init__(self, product_id, fraction_id=0):
        self._tablename_ = "hvp_diversity_of_sorts"
        self.product_id = product_id
        self.fraction_id = fraction_id
    
    def get(self):
        """ a list of dict
        TODO all_fractions (UNION?)
        AND... OR 
        """
        sql = "SELECT * FROM "+self._tablename_+" \
            WHERE product_id=:product_id AND fraction_id=:fraction_id\
            OR all_fractions=True ORDER BY name;"
            
        data = engine.execute(text(sql), fraction_id=self.fraction_id,
                              product_id=self.product_id)
        return proxy2list(data)
    
    def get_wtform_choices(self):
        """returns WTForm.SelectField.choices[] list_of_tuple(id, string)"""
        sql = "SELECT id,name FROM "+self._tablename_+" \
            WHERE product_id=:product_id\
            AND (fraction_id=:fraction_id OR all_fractions=True) \
            ORDER BY name;"
        data = engine.execute(text(sql), fraction_id=self.fraction_id,
                              product_id=self.product_id)

        choices = list( (row.id, row.name) for row in data.fetchall())
        result = [(NO_CHOICE_VALUE,NO_CHOICE_STRING)] + choices #push dummy for no choise
        #print('diversity :'+str(result))
        return result
    
#-------------------------------------------------------------------#
# Units to measure a product
#-------------------------------------------------------------------#    
class UnitModel(object):
    """ is it wise to init the object with a set set of  units?
    No.
    same thing here split up in UnitSetModel(set_id) and UnitModel()
    primary key=1 refers to the IS Unit of Kg
    """
    def __init__(self,set_id=None):
        if set_id:
            self.set_id = set_id
        #all units
        self.__unit_tablename__ = "hvp_shipping_units"
        #sets of units
        self.__set_tablename__ = "hvp_shipping_unit_sets"
        #mapps units into sets (with todo order by useraccount...)
        self.__mapper_tablename__ = "hvp_shipping_unit_mapper"
        
    def get_unitset_by_id(self, set_id=None):
        """ passing a different set_id then in  __init__() joker_ish function
        rows of unit_tablename grouped by a set_id
        TODO: fractionspec maybe __init(fraction_id)
        but is the fraction_id even relevant?
        """
        sql ="SELECT id, name, hint, kg_factor,\
            kg_factor_tolerance, tareable  \
            FROM "+ self.__unit_tablename__+"\
            WHERE id IN (SELECT unit_id FROM "\
            +self.__mapper_tablename__+" WHERE \
            unit_set_id=:set_id);"
        
        if set_id :
            data = engine.execute(text(sql), set_id=set_id)
        else:
            data = engine.execute(text(sql), set_id=self.set_id)
        
        return proxy2list(data)
    
    def get_wtform_choices(self):
        """to populate a html select form elemant with options later
        ---
        """
        sql = "SELECT id, name FROM "+self.__unit_tablename__+" \
            WHERE id IN (SELECT unit_id FROM "+self.__mapper_tablename__+" \
            WHERE unit_set_id=:set_id) ORDER BY id;"
            
        data = engine.execute(text(sql), set_id=self.set_id)
        choices = list( (row.id, row.name) for row in data.fetchall())
        #no dummy (not chosen jet) entrie needed so:
        return choices
    
    def is_tareable(self, unit_id):
        """ a function for UnitModel()
        return boolean
        """
        
        sql = "SELECT tareable FROM "+self.__unit_tablename__+"\
        WHERE id=:unit_id"
        
        data = engine.execute(text(sql), unit_id=unit_id)
        
        b=data.fetchone()[0]
        
        #print("POSTGRES BOOLEAN CLEAN RETURN:"+str(b)) it returns a Boolean(yahoo!)
        
        return b

    def get_name_by_id(self, unit_id):
        
        pass


#-------------------------------------------------------------------#
# Boxes to transport and store products
#-------------------------------------------------------------------# 
class BoxModel(object):
    """ 4 tables 
    maybe split up the model to a BoxSetModel and a BoxModel?
    """
    def __init__(self, set_id=None):
        self.set_id = set_id
        #:all boxes with group reference
        self.__box_tablename__ = "hvp_shipping_boxes"
       
        #:industrial box groups
        self.__box_groups_tablename__ = "hvp_shipping_box_groups"
       
        #:individual sets of boxes
        self.__box_set_tablename__ = "hvp_shipping_box_sets"
       
        #:aux. mappertable maps boxes to boxgroups
        self.__box_mapper_tablename__ = "hvp_shipping_box_mapper"
       
        #:view
        self.__box_view__ = "boxes_view"

    def get_set_by_id(self, set_id):
        """ 
        rows of boxes belonging to one inividual SET referenced by set_id
        """
        sql ="SELECT * \
            FROM "+self.__box_view__+"\
            WHERE box_id IN (SELECT box_id FROM "\
            +self.__box_mapper_tablename__+" WHERE \
            box_set_id =:set_id)\
            ORDER BY name;"
        
        data = engine.execute(text(sql), set_id=set_id)
        
        return proxy2list(data)
    
    def get_boxdata_by_id(self, box_id):
        """return data for One Box stored in boxes_view referenced by box_id
        """
        sql = "SELECT * FROM "+self.__box_view__+"WHERE id=:box_id"
        
        data = engine.execute(text(sql), box_id=box_id)
        return proxy2list(data)
    
    def get_tara_by_id(self, box_id):
        """ return only the tara-weight of one box referenced by box_id
        """
        sql = "SELECT tara FROM " + self.__box_tablename__ +" WHERE id=:box_id"
        
        data = engine.execute(text(sql),box_id=box_id)
        
        return data.fetchone()[0]
    
    def get_wtform_choices(self,set_id=None):
        """ TODO IF box_groups.Name then concat caliber-name CASE gt.name NOT NULL"""
        sql = "SELECT bt.id AS id,(bt.caliber::text || '-'::text) || gt.name::text AS name \
            FROM " +self.__box_tablename__+" AS bt, " +self.__box_groups_tablename__+" AS gt \
            WHERE bt.id IN (SELECT box_id FROM "+self.__box_mapper_tablename__+" WHERE \
            box_set_id= :set_id)\
            AND bt.box_groups_id=gt.id"
            
        if set_id :
            data = engine.execute(text(sql),set_id=set_id)
        else :
            data = engine.execute(text(sql),set_id=self.set_id)
        
        choices = list( (row.id, row.name) for row in data.fetchall())
        return choices
    
#-------------------------------------------------------------------#
#Vehicles to may carry Boxes
#-------------------------------------------------------------------#
class VehicleModel(object):
    """Vehicles may carry boxes with products.
    during aqcuisition-transactions the tara weight of vehicle is of interest 
    """
    def __init__(self):
        self.__tablename__ = "hvp_transport_vehicles"
        
    def get_all(self):
        """ for wtform select"""
        sql = "SELECT id, name FROM "+self.__tablename__+" ORDER by id"
        data = engine.execute(sql)
        return proxy2list(data)
    
    def get_wtform_choices(self):
        """ for wtform select """
        sql =  "SELECT id, name FROM "+self.__tablename__+" ORDER by id"
        data = engine.execute(sql)
        choices = list( (row.id, row.name) for row in data.fetchall())
        #TODO @decorator choices: expand list of rows,fetchall,?stack dummychoice?
        
        return choices
    
    def get_tara_by_id(self, vehicle_id):
        
        sql = "SELECT tara FROM "+self.__tablename__+" WHERE id=:vehicle_id"
        data = engine.execute(text(sql),vehicle_id=vehicle_id)
        return data.fetchone()[0]
        
    
#-------------------------------------------------------------------#
#agricultural Areas
#-------------------------------------------------------------------#
class AreaModel(object):
    """kind a """
    def __init__(self, area_tree_id):
        self._tablename_ = "hvp_farmland_and_areas"
        self.area_tree_id=area_tree_id
        
    def get_wtform_choices(self):
        """returns list_of_tuple(id, string)"""
        sql = "SELECT id, our_name FROM "+self._tablename_+ ",hvp_forest_trees \
        WHERE id=data_id AND tree_id ='"+str(self.area_tree_id)+"' ORDER BY lft;"
        print(sql)
        data = engine.execute(sql)

        choices = list( (row.id, row.our_name) for row in data.fetchall())
        result = [(NO_CHOICE_VALUE,NO_CHOICE_STRING)] + choices #push dummy for no choise
        #print('areaChoises:'+str(choices)) 
        return result
    
    def get_by_id(self, area_id):
        """ retrieve area infos returns One dict"""
        sql = "SELECT * FROM "+self._tablename_+" WHERE id=:area_id;"
        data = engine.execute(text(sql),area_id=area_id)
        #print(proxy2list(data))
        return proxy2list(data)[0]
    
        
        
    
    
    def get_involved_areas(self, year_of_growth):
        
        sql="SELECT FROM>>" + str(year_of_growth)
        
        print(sql)
        return
    
        
#-------------------------------------------------------------------#
# GrowKind the geometrie one can put plants in the ground
#-------------------------------------------------------------------# 
class GrowKindModel(object):
    """ """
    def __init__(self):
        self._tablename_ ="hvp_grow_kinds"
        
    def get_short_by_id(self, grow_kind_id):
        """ used for ajax... return one dict(columnname:value)"""
        sql = " SELECT width, growlines, force_plant_interval, planting_interval \
                FROM "+self._tablename_ + " WHERE id=:grow_kind_id ;"
        data = engine.execute(text(sql),
                              grow_kind_id=grow_kind_id)
        
        return proxy2list(data)[0]
    
    def get_wtform_choices(self):
        """#"""
        sql = "SELECT id, name FROM "+self._tablename_+ " ORDER BY name;"
        data = engine.execute(sql)
        
        choices = list( (row.id, row.name) for row in data.fetchall())
        result = [(NO_CHOICE_VALUE,NO_CHOICE_STRING)] + choices #push dummy for no choise
        #print('growkindChoises:'+str(result))
        return result
    
    def do_veggie_conception_ajax():
        """ out of the model """
        pass

#-------------------------------------------------------------------#
# Seed
#-------------------------------------------------------------------#
class SeedModel(object):
    """how to describe  a seed entity
    
    comception FOREIGN_KEY
    diversity FOREIGN_KEY
    amount_of_seed
    amount_of_plants
    unit_of_seed
    tkweight 
    germinating ability
    quality enumtype:seed_spec_enum
    (seed_spec_true_in_seed,seed_spec_homegrown,seed_spec_F1_hybride,seed_spec_CMS_hybride,seed_spec_GVO)
    date
    partie
    
    
    """
    
    def get_wtform_unit_choices(self):
        """ references to hvp_shipping_units"""
        #TODO unhardcoding
        choices = [(2,'gramm'),(11,'Korn'),(12,'ETP'),(1,'kg')]

        #print(choices)
        return choices

#-------------------------------------------------------------------#
# Art_of_Cultivation
#-------------------------------------------------------------------#
class CultivationModel(object):
    """how do plants come alive and get into ground
    is a simple enumtype
    CREATE TYPE cultivation_enum AS ENUM ('direct_seeding', 'plant_purchase', 'sowing_transplant');
    
    direct_seeding
    sowing_transplant
    plant_purchase
    
    """
    def get_wtform_choices(self):
        
        choices = [('dummy',''),
                   ('direct_seeding','Direktsaat'),
                   ('plant_purchase','Pflanzenzukauf'),
                   ('sowing_transplant','Saat und Umpflanzung')
                   ]
        
        return choices
    
#select * from veg_conception where year_of_growth=2019 and art_of_cultivation is NULL    
#update veg_conception set art_of_cultivation= 'plant_purchase' where year_of_growth=2019 
#AND fraction_id=2  AND product_id= 131000
#-------------------------------------------------------------------#
# Transactions: Products moving between fractions
# the datastructur prohibits the use of green
# and yellow Boxes the same time, only one box_id per Insert/Update
#-------------------------------------------------------------------#
class TransactionModel(object):
    """ product movments between fractions
    table acquisition
    table retraction
    TODO handle all the implementation_id stuff
        wer hatte eigentlich diese Idee
    """
    
    def __init__(self, fraction_id="NULL", source_fraction_id="NULL"):
        
        self.fraction_id = fraction_id
        self.source_fraction_id = source_fraction_id
        self.boxmodel = BoxModel()
        self.unitmodel = UnitModel()
        self.vehiclemodel = VehicleModel()
        self._acquisition_table = 'hvp_acquisitions'
        self._retraction_table = 'hvp_retractions'
        
    def index(self, ago):
        """ avg, all fractions """
        ago += ' DAYS'
        
        sql = "select bp.item_name, su.name AS unit_name, fraction_id, source_fraction_id, product_id, unit_id, "
        sql += "cast( avg(netto) as integer ) AS netto , cast( avg(retour) as integer) AS retour "
        sql += "from get_transactions() "
        sql += "left join hvp_all_base_products AS bp ON bp.id = product_id "
        sql += "left join hvp_shipping_units AS su ON su.id = unit_id "
        sql += "where  date > (now() - interval :ago) "
        sql += "group by bp.item_name, su.name, fraction_id, source_fraction_id, product_id, unit_id "
        sql += "order by bp.item_name;"
        
        data = engine.execute(text(sql), ago=ago)
        return proxy2tab(data)
        

    def get_simple(self, product_id=None, date=None):
        """calls the stored procedure get_transactions() and add Names
        returns all fields of get_transactions() AS GT +...
        
        date is string 'YYYY-mm-dd'
        product_id is integer
        
        please make sure to call at least with one parameter
        
        TODO sql text() it
        """
        starttime=time.time()
        #print('GET_SIMPLE:')
        sql = "SELECT GT.*, ABP.item_name, SU1.name AS unit_name, SU2.name AS alternate_unit_name, FR1.name AS fraction_name, FR2.name AS source_fraction_name "
        sql += " FROM get_transactions(%s,%s) AS GT, "%(self.fraction_id,self.source_fraction_id)
        sql += " hvp_all_base_products AS ABP,"
        sql += " hvp_shipping_units AS SU1, "
        sql += " hvp_shipping_units AS SU2, "
        sql += " hvp_fractions AS FR1, "
        sql += " hvp_fractions AS FR2 "
        if product_id and date==None :
            sql += " WHERE product_id=%s"%(product_id)
            
        if product_id==None and date :
            sql += " WHERE date='%s'"%(date)
            
        if product_id and date :
            sql += "WHERE product_id=%s AND date='%s' "%(product_id,date)
            
        sql += " AND GT.unit_id=SU1.id AND GT.alternate_unit_id=SU2.id "
        sql += " AND GT.product_id= ABP.id "
        sql += " AND GT.fraction_id=FR1.id AND GT.source_fraction_id=FR2.id"
        sql += " ORDER BY ABP.item_name, SU1.name"
        
        #print(sql)
        #endtime = time.time() #performence time end
        print('->transfer.get_simple:'+str(time.time()-starttime)+'sec.')
        data = engine.execute(sql)
        
        return proxy2list(data)
        
        
    
    def map_get_transactions(self,db_result):
        """depricated helperfunction to map select*get_transactions function results"""
        entries = [ dict(date=row['date'],
                         year=row['year'],
                         week=row['week'],
                         product_id=row['product_id'],
                         implementation_id=row['implementation_id'],
                         fraction_id=row['fraction_id'],
                         source_fraction_id=row['source_fraction_id'],
                         unit_id=row['unit_id'],
                         brutto=row['brutto'],
                         retour=row['retour'],
                         netto=row['netto']
                         )for row in db_result.fetchall()
                   ]
        return entries
##
#
#    ACQUISITION Part of Transactions between Fractions
# there can be more then one entrie only differ in (ts,amount)
##
    def acqusition_insert(self, wtform):
        """takes a wtform-obj to insert into table acquisition
        weekest is tare management
        amount will be round(x,2) if not Integer
        TODO: text(sql) it, you can not debug the sql string after text()ing (sqlalchemy.echo=true)
        TODO:   add a mutiselect Field, populate it with possible implemantations
                create a unique ID for the selection, store this as implementation_id
                
        'if wtform.vehicle_count.data  and is_tareable' : should be '....data > 0 and ...'
        if jquery disables the input, wtform does not validate , so wtforms.validator.optional
        and effecting the model
        """
        
        #datum = wtform.aq_date.raw_data[0]
        
        datum = str(wtform.aq_date.data)
        #print('INSERTdatum:'+str(datum))
        amount = wtform.amount.data
        is_tareable =  self.unitmodel.is_tareable(wtform.unit_id.data)
        unit_name = self.unitmodel.get_name_by_id(wtform.unit_id.data)
        
        #print("raw_data:"+ str(datum))
        #print("data:"+ str(wtform.aq_date.data))
        
        #removing Tara from <input>amount
        if wtform.no_tara.data == True:
            print('NoTARA!')
            is_tareable = False
        
        if wtform.box_count.data > 0 and is_tareable:
            #boxtara in kg
            one_box_tara = self.boxmodel.get_tara_by_id(wtform.box_id.data)/1000
            amount = amount - decimal.Decimal(wtform.box_count.data * one_box_tara)
         
        if wtform.vehicle_count.data  and is_tareable:
            one_vehicle_tara = self.vehiclemodel.get_tara_by_id(wtform.vehicle_id.data)/1000
            amount = amount - decimal.Decimal(wtform.vehicle_count.data * one_vehicle_tara)
            
        #removing additional Tara in kg / create sql value of additional_tara
        if wtform.additional_tara.data and is_tareable and wtform.unit_id.data == 1: #kg's db PK is 1! 
            amount = amount - wtform.additional_tara.data 
            additional_tara = wtform.additional_tara.data 
        else:
            additional_tara = "NULL"

        if wtform.alternate_amount.data:
            alternate_amount = wtform.alternate_amount.data
        else:
            alternate_amount = "NULL"

        if not float(amount).is_integer():
            amount = round(amount,2)
        
        if amount < 0 :
            flash(str(wtform.amount.data),'primary')#original_amount
            return str(u'Nach Abzug der TAREN ist die Einwage  '+str(amount)+' ein negativer Wert. Nichts gespeichert.')

        #print("roughly_amount:"+ str(wtform.roughly_amount.data))
        
        sql="INSERT INTO "+self._acquisition_table+"  (date,year,week,product_id,implementation_id,fraction_id,source_fraction_id,roughly_amount,amount,unit_id,box_id,box_count,hint,ticket,original_amount,alternate_amount,alternate_unit_id,additional_tara,no_tara) "
        sql=sql+" VALUES('"+datum+"',EXTRACT(year FROM '"+datum+"'::date),EXTRACT(week FROM '"+datum+"'::date),"+str(wtform.product_id.data)+","
        sql=sql+" NULL,"+str(wtform.fraction_id.data)+","+str(wtform.source_fraction_id.data)+","+str(wtform.roughly_amount.data)+","+str(amount)+","+str(wtform.unit_id.data)+","+str(wtform.box_id.data)+","+str(wtform.box_count.data)+",'"+str(wtform.hint.data)+"',NULL,"+str(wtform.amount.data)+","+str(alternate_amount)+","+str(wtform.alternate_unit_id.data)+","+str(additional_tara)+","+str(wtform.no_tara.data)+");"
        
        #print(sql);
        some_return = engine.execute(sql)
        flash(str((wtform.amount.data)),'primary')#original_amount input
        return some_return
    
    def acqusition_delete(self, timestamp):
        """a timestamp as primary key is daring"""
        sql="DELETE FROM hvp_acquisitions WHERE fraction_id=:fraction_id AND ts=:timestamp"
        if engine.execute(text(sql), timestamp=timestamp, fraction_id=self.fraction_id):
            return True
        else:
            return False
        
    
    def acqusitions_get_last_inserts(self,limit=12,ext_fraction=False):
        """ returns the cronological last entrys in the acqusitions table
        TABLENAMES ARE HARDCODED  DATE DISPLAY FORMAT IS HARDCODED
        age is in Minutes after insert
        
        ago
        """
        sql="SELECT A.ts, EXTRACT (EPOCH FROM NOW()-A.ts)::int/60 AS minute_age, EXTRACT (EPOCH FROM NOW()-A.ts) AS ago, A.product_id, A.date, P.item_name, A.amount, A.roughly_amount, A.box_count, A.alternate_amount, A.additional_tara, A.no_tara, A.hint, U1.name AS unit_name, U2.name AS alternate_unit_name, B.caliber,  BG.name  FROM hvp_acquisitions AS A,hvp_shipping_units AS U1,hvp_shipping_units AS U2,hvp_shipping_boxes AS B,hvp_all_base_products AS P,hvp_shipping_box_groups AS BG WHERE A.product_id = P.id AND A.unit_id = U1.id AND A.alternate_unit_id = U2.id AND A.box_id = B.id AND B.box_groups_id = BG.id AND A.fraction_id =:fraction_id AND A.source_fraction_id =:source_fraction_id ORDER by A.ts DESC LIMIT :limit"
        
        data = engine.execute(text(sql), limit=limit,
                              fraction_id=self.fraction_id,
                              source_fraction_id=self.source_fraction_id)
        return proxy2list(data)
    
    def acqusitions_get_last_dates(self,limit=48,ext_fraction=False):
        """ return last calender dates where acquisition took place
        DATE DISPLAY FORMAT IS HARDCODED
        """
        sql="SELECT DISTINCT ((TO_CHAR(date,'dd.mm.YYYY'))) AS date_string, date FROM hvp_acquisitions WHERE fraction_id=:fraction_id AND source_fraction_id=:source_fraction_id ORDER BY date DESC LIMIT :limit"
        
        data = engine.execute(text(sql), limit=limit,
                              fraction_id=self.fraction_id,
                              source_fraction_id=self.source_fraction_id)
        return proxy2list(data)
    
    def acquisitions_get_summary_by_date_product_unit(self, date, product_id, unit_id):
        """get acquisitions summary of one product with that unit at that date
        returns one row
        TABLENAMES HARDCODED
        TODO implementation_id, ext_fraction
        TODO are there more then one box Types involved?
        for the start of a retour
        if we group by box_id too, we could select for possible box_id in select<options>
        but retour could be in a box from far yeeeears ago --> Box Management(product_id=zero????)
        """
        sql = "SELECT SUM(ACQ.amount) AS acquisum, "
        sql += "SUM(ACQ.alternate_amount) AS alternatesum, "
        sql += "ACQ.date, "
        sql += "ACQ.year, "
        sql += "ACQ.week, "
        sql += "ACQ.product_id, "
        sql += "MAX(ACQ.box_id) AS box_id, "
        sql += "string_agg(ACQ.hint, ' - ') AS hint, "
        sql += "ACQ.implementation_id, "
        sql += "ACQ.fraction_id, "
        sql += "ACQ.source_fraction_id, "
        sql += "ACQ.unit_id, "
        sql += "U1.name AS unit_name, "
        sql += "ACQ.alternate_unit_id, "
        sql += " U2.name AS alternate_unit_name "
        sql += " FROM "+self._acquisition_table+" AS ACQ, "
        sql += " hvp_shipping_units AS U1, "
        sql += " hvp_shipping_units AS U2 "
        sql += " WHERE ACQ.fraction_id= "+str(self.fraction_id)
        sql += " AND ACQ.source_fraction_id= "+str(self.source_fraction_id)
        sql += " AND ACQ.product_id= "+str(product_id) 
        sql += " AND date= '"+str(date)+"'"
        sql += " AND unit_id= "+str(unit_id)
        sql += " AND ACQ.unit_id=U1.id "
        sql += " AND ACQ.alternate_unit_id=U2.id "
        sql += " GROUP BY ACQ.date, ACQ.year, ACQ.week, ACQ.product_id, ACQ.implementation_id, ACQ.fraction_id, ACQ.source_fraction_id, ACQ.unit_id, ACQ.alternate_unit_id, U1.name, U2.name;"
        
        #data = engine.execute(text(sql),
                              #fraction_id=self.fraction_id,
                              #source_fraction_id=self.source_fraction_id,
                              #product_id=product_id,
                              #date=date,
                              #unit_id=unit_id)
        print(sql)
        data = engine.execute(sql)
        return proxy2list(data)[0] # one row
##
#
#    RETRACTION Part of Transactions between Fractions
#
##
    def retraction_insert(self, wtform):
        """insert data in retractions Table
        """
        datum = str(wtform.aq_date.data)
        amount = wtform.amount.data
        is_tareable =  self.unitmodel.is_tareable(wtform.unit_id.data)
        unit_name = self.unitmodel.get_name_by_id(wtform.unit_id.data)
        
        #print('AlternateAMOUNT:'+str(wtform.alternate_amount.data))
        
        #removing Tara from <input> amount
        if wtform.box_count.data >0 and is_tareable:
            #boxtara in kg
            one_box_tara = self.boxmodel.get_tara_by_id(wtform.box_id.data)/1000
            amount = amount - decimal.Decimal(wtform.box_count.data * one_box_tara)
        
        if wtform.vehicle_count.data > 0 and is_tareable:
            one_vehicle_tara = self.vehiclemodel.get_tara_by_id(wtform.vehicle_id.data)/1000
            amount = amount - decimal.Decimal(wtform.vehicle_count.data * one_vehicle_tara)
        #removing additional Tara in kg / create sql value of additional_tara 
        if wtform.additional_tara.data and wtform.unit_id.data == 1: #kg's db PK is 1! 
            amount = amount - wtform.additional_tara.data 
            additional_tara = wtform.additional_tara.data 
        else:
            additional_tara = "NULL"

        if wtform.alternate_amount.data:
            alternate_amount = wtform.alternate_amount.data
        else:
            alternate_amount = "NULL"
            
        if not float(amount).is_integer():
            amount = round(amount,2)
            
        if amount < 0 :
            flash(str(wtform.amount.data),'primary')
            return str(u'Nach Abzug der TAREN ist die Einwage  '+str(amount)+' ein negativer Wert. Nichts gespeichert.')
        
        
        acquire_data = self.acquisitions_get_summary_by_date_product_unit(datum,
                                                                          wtform.product_id.data,
                                                                          wtform.unit_id.data)
        #check if retraction is greater then aqcuisition
        acquisum = acquire_data['acquisum']
        alternatesum = acquire_data['alternatesum']
        #print('ACQISUM:'+str(acquisum))
        #print('ALTERNATESUM:'+str(alternatesum))
        
        if acquisum-amount < 0 :
            return str(u'Es kommt mehr zurück als zuvor hinzu kam. Nichts gespeichert!')
        
        if wtform.alternate_amount.data and alternatesum:
            if alternatesum-wtform.alternate_amount.data < 0 :
                return str(u'alternative Menge: mehr Rücklauf als Zulauf. Nichts gespeichert!')
        
        #implementation_id insert string is: '{x,y,z}' like date: 'YYYY-mm-dd'
        #print(str(acquire_data['implementation_id']))
        
        sql = "INSERT INTO "+self._retraction_table+" "
        sql+= "(acquisition_date,product_id,implementation_id,fraction_id,source_fraction_id,"
        sql+= "roughly_amount,amount,unit_id,box_id,box_count,alternate_amount,alternate_unit_id,"
        sql+= "original_amount,additional_tara,hint)"
        sql+= "VALUES('"+datum+"'," +str(wtform.product_id.data)+","+"NULL"+","+str(wtform.fraction_id.data)+","+str(wtform.source_fraction_id.data)+","
        sql+= str(wtform.roughly_amount.data)+","+str(amount)+","+str(wtform.unit_id.data)+","+str(wtform.box_id.data)+","+str(wtform.box_count.data)+","+str(alternate_amount)+","+str(wtform.alternate_unit_id.data)+","
        sql+= str(wtform.amount.data)+","+str(additional_tara)+",'"+str(wtform.hint.data)+"');"
        
        print(sql)
        
        some_return = engine.execute(sql)
        flash(str((wtform.amount.data)),'primary')#original_amount input
        
        return some_return
##
#
#    REPORT Part of Transactions between Fractions
#
##
    def report():
     pass



    
#-------------------------------------------------------------------#
#   Contacts
#-------------------------------------------------------------------#
class ContactsModel(object):
    """ adresses """
    def __init__(self):
        self._tablename_ = 'hvp_contacts'
    
    
    def get_wtform_choices(self):
        sql = "SELECT id,name FROM "+self._tablename_+" ORDER by name;"
        data = engine.execute(sql)
        
        choices = list( (row.id, row.name) for row in data.fetchall())
        result = [(NO_CHOICE_VALUE,NO_CHOICE_STRING)] + choices #push dummy for no choise
        return result
    
