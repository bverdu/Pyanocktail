# -*- encoding:utf-8 -*-
'''
Database utlity functions
'''
from __future__ import division
from sqlalchemy import create_engine, or_, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.pool import StaticPool
from sqlalchemy.engine import Engine

global db
db = None
global Base
Base = declarative_base()
    
class Cocktail(Base):
    __tablename__ = 'cocktails'
    
    cocktail_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(50))
    score1 = Column(Integer)
    score2 = Column(Integer)
    score3 = Column(Integer)
    available = Column(Boolean, default=True)
    
    def __init__(self,name,description='',score1=0,score2=0,score3=0,available=True):
        self.name = name
        self.description = description
        self.score1 = score1
        self.score2 = score2
        self.score3 = score3
        self.available = available
        
    def __repr__(self):
        return "<Cocktail('%s', \"%s\")>" % (self.name,self.description)
    
class Pump(Base):
    __tablename__ = 'pumps'
    
    pump = Column(Integer, primary_key=True, autoincrement=False)
    description = Column(String(50))
    type = Column(String)
    i2cbus = Column(String(10))
    i2caddr = Column(String(10))
    ratio = Column(Float)
    function = Column(String(10))
    available = Column(Boolean)
    
    def __init__(self, pump, description='', type_='fake_pwm', i2cbus='0x20', i2caddr='0', fct='None', ratio=1.0):
        self.pump = pump
        self.description = description
        self.type = type_
        self.i2cbus = i2cbus
        self.i2caddr = i2caddr
        self.function = fct
        self.ratio = ratio
        
    def __repr__(self):
        return "<Pump(%d, \"%s\")>" % (self.pump, self.description)
    
class Switch(Base):
    __tablename__ = 'switches'
    
    switch_id = Column(Integer, primary_key=True, autoincrement=False)
    description = Column(String(50))
    function = Column(String(10))
    param = Column(String(10))
    available = Column(Boolean)
    
    def __init__(self, gpionum, description='', fct='None'):
        self.switch_id = gpionum
        self.description = description
        self.function = fct
        
    def __repr__(self):
        return "<Switch(%d, \"%s\")>" % (self.switch_id, self.description)
    
class Ingredient(Base):
    __tablename__ = 'ingredients'
    
    ingredient_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    alcool = Column(Integer)
    pump = Column(Integer, ForeignKey('pumps.pump'))
    duration = Column(Integer)
    qty_avail = Column(Integer)

    
    def __init__(self,name,pump,alcool=1,duration=1000,qty_avail=100):
        self.name = name
        self.alcool = alcool
        self.pump = pump
        self.duration = duration
        self.qty_avail = qty_avail
        
    def __repr__(self):
        return "<Ingredient('%s', pump n° %d)>" % (self.name, self.pump)
    
    
class Recipe(Base):
    __tablename__ = 'recipes'
    
    cocktail_id = Column(Integer, primary_key=True, autoincrement=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.ingredient_id'))
    quantity = Column(Integer)
    order = Column(Integer, primary_key=True, autoincrement=False)
    __table_args__ = (ForeignKeyConstraint([cocktail_id],[Cocktail.cocktail_id]),{})
    cocktail = relationship(Cocktail, backref=backref('recipes', order_by=order, cascade='all, delete-orphan'))
    ingredient = relationship(Ingredient, backref=backref('recipes', order_by=cocktail_id, cascade='all, delete-orphan'))
    
    
    def __init__(self, cocktail, ingredient, order, quantity=1):
        self.cocktail_id = cocktail
        self.ingredient_id = ingredient
        self.quantity = quantity
        self.order = order
        
    def __repr__(self):
        return "<Recipe('%s' '%s' %d >" % (self.cocktail_id, self.ingredient_id, self.quantity)
    
    
    
def initdb(connect_string, dbtype, debug):
    '''
    Constructor
    '''
    #print('dbstring: %s' %connect_string)
    if dbtype == 'sqlite':
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        if len(connect_string) < 10 :
            db = create_engine(connect_string, 
                               connect_args={'check_same_thread':False},
                               poolclass=StaticPool, 
                               echo = debug)
        else:
            db = create_engine(connect_string, 
                               connect_args={'check_same_thread':False},
                               echo = debug) 
    else:
        db = create_engine(connect_string, echo = debug)
    Base.metadata.create_all(db)
    Session = sessionmaker(bind = db)
    return Session()
    
    
def getCocktails(session, alcool=True):
    
    if session.cocktails != None:
        if session.alcool == alcool:
            return session.cocktails
     
    cocktails= []
    discarded = []
    reason = []   
    if alcool == False:
        r = 0
        for cocktail, recipe, ingredient  in session.query(Cocktail, Recipe, Ingredient).\
                                filter(Cocktail.cocktail_id == Recipe.cocktail_id).\
                                filter(Recipe.ingredient_id == Ingredient.ingredient_id).\
                                filter(or_(Ingredient.qty_avail < Recipe.quantity,
                                            Ingredient.alcool > 0)).all():
            discarded.append(cocktail)
#             print(discarded)
            if ingredient.alcool > 0:
                r += 2
                if ingredient.qty_avail < recipe.quantity:
                    r+= 1
            else:
                r = 1
            reason.append(r)
#             print(reason)
    else:
        for cocktail, recipe, ingredient  in session.query(Cocktail, Recipe, Ingredient).\
                                filter(Cocktail.cocktail_id == Recipe.cocktail_id).\
                                filter(Recipe.ingredient_id == Ingredient.ingredient_id).\
                                filter(Ingredient.qty_avail < Recipe.quantity).all():
            discarded.append(cocktail)
            
    for cocktail in session.query(Cocktail).all():
        try:
            r = reason[discarded.index(cocktail)]
#             print(r)
            if r == 1:
                disp = 'Missing ingredient'
            elif r == 2:
                disp = 'Contains alcool'
            elif r == 3:
                disp = 'Missing ing + contains alcool'
            cocktails.append({'id' : cocktail.cocktail_id,
                              'name': cocktail.name, 
                              'description': cocktail.description, 
                              'score1': int(cocktail.score1),
                              'score2': int(cocktail.score2),
                              'score3': int(cocktail.score3), 
                              'available': disp})
        except:
            cocktails.append({'id' : cocktail.cocktail_id,
                              'name': cocktail.name, 
                              'description': cocktail.description, 
                              'score1': int(cocktail.score1),
                              'score2': int(cocktail.score2),
                              'score3': int(cocktail.score3), 
                              'available': 'OK'})
                
    session.alcool = alcool
    session.cocktails = cocktails
    return cocktails

def setCocktails(session, cocktail_list):
    
    for row in cocktail_list:
        if int(row['id']) == 0:
            p = Cocktail(row['name'],
                       description=row['description'],
                       score1=int(row['score1']),
                       score2=int(row['score2']),
                       score3=int(row['score3']))
        else:
            p = session.query(Cocktail).get(int(row['id']))
            p.description = row['description']
            p.score1 = int(row['score1'])
            p.score2 = int(row['score2'])
            p.score3 = int(row['score3'])
            
        session.add(p)
    session.cocktails = None

def delCocktails(session, cocktail_list):
    
    for row in cocktail_list:
        session.delete(session.query(Cocktail).get(int(row['id'])))
    session.cocktails = None

def getPumps(session):
    if session.pumps != None:
        return session.pumps
    pumps = []
    for pump in session.query(Pump).all():
        pumps.append({'num': int(pump.pump),
                      'type': str(pump.type),
                      'description': str(pump.description),
                      'bus': str(pump.i2cbus),
                      'channel': int(pump.i2caddr),
                      'ratio': float(pump.ratio),
                      'funct': str(pump.function),
                      'avail': bool(pump.available)})
    session.pumps = pumps
    return pumps

def getPump(session, num):
    pump = []
    try :
        p = session.query(Pump).filter(Pump.pump == num).one()
        pump = [p.type, int(p.i2cbus, 16),  int(p.i2caddr), p.ratio]
        
    except Exception, err:
        #print(err.message)
        pump = [err.message]
    
    return pump

def setPumps(session, pump_list):
    
    for row in pump_list:
        if session.query(Pump).filter(Pump.pump == row['pump']).count()==0:
            if str(row['bus']) == '-1':
                continue
            p = Pump(row['pump'],
                       description=row['description'],
                       type_=row['type'],
                       i2cbus=row['bus'],
                       i2caddr=str(row['chan']),
                       ratio=row['ratio'],
                       fct=row['fct'])
        else:
            p = session.query(Pump).filter(Pump.pump == row['pump']).one()
            if str(row['bus']) == '-1':
                session.delete(p)
                continue
            p.description = row['description']
            p.type = row['type']
            p.i2cbus = row['bus']
            p.i2caddr = str(row['chan'])
            p.ratio = row['ratio']
            p.function = row['fct']
        session.add(p)
    session.pumps = None
    session.sysIngs = None

def getIngredients(session):
    
    if session.ingredients != None:
        return session.ingredients 
    ingredients= []
    for ingredient  in session.query(Ingredient).all():
        ingredients.append({'id': int(ingredient.ingredient_id),
                            'name' : ingredient.name, 
                            'deg': int(ingredient.alcool), 
                            'pump': int(ingredient.pump), 
                            'time':int(ingredient.duration), 
                            'qty':int(ingredient.qty_avail)})
    session.ingredients = ingredients
    return ingredients

def getSysRecipes(session):
    
    if session.sysIngs != None:
        return session.sysIngs
    startIng = []
    endIng = []
    fct_list = []
    for sysIng, pump in session.query(Ingredient, Pump).filter(Ingredient.name.startswith("sys"),
                                                                Pump.pump == Ingredient.pump).\
                                                                order_by(Ingredient.alcool, Pump.pump).all():
        ingtype = sysIng.name.split('_')
        ing = []
        ing.append(ingtype[1])
        ing.append(int(pump.i2cbus, 16))
        if ingtype[1] in ("stepper", "motor"):
            for p in session.query(Pump).filter(Pump.description == pump.description).all():
                if p.type in ("motor_ENA","stepper_ENA"):
                    a = int(p.i2caddr)
                elif p.type in ("motor_A","stepper_ENB"):
                    b = int(p.i2caddr)
                elif p.type in ("motor_B", "stepper_A1"):
                    c = int(p.i2caddr)
                elif p.type == "stepper_A2":
                    d = int(p.i2caddr)
                elif p.type == "stepper_B1":
                    e = int(p.i2caddr)
                elif p.type == "stepper_B2":
                    f = int(p.i2caddr)
            if ingtype[1] == "motor":
                ing.append([a,b,c])
            else:
               ing.append([a,b,c,d,e,f])
        else:
            ing.append(int(pump.i2caddr))
        if ingtype[3] == "bw":
            ing.append(-float(int(sysIng.duration))/1000)
        else:
             ing.append(float(int(sysIng.duration))/1000)
        ing.append(float(pump.ratio))
        ing.append(str(pump.function))
                        
        if sysIng.alcool < 100:
            if sysIng.alcool < 10:
                startIng.append(ing)
            else:
                endIng.append(ing)
        else:
            fct_list.append(ing)
            session.hasfct = True
                        
    
    session.sysIngs = {'before':startIng,'after':endIng,'functions':fct_list}
    if len(fct_list) == 0:
        session.hasfct = False
    print("***************************************************")
    print(session.sysIngs)
    print("***************************************************")
    return session.sysIngs
        
        

def getIngList(session):
    
    if session.ingList != None:
        return session.ingList
    l = []
    l.append([])
    l.append([])
    for ingredient  in session.query(Ingredient).all():
        l[0].append(ingredient.name)
        l[1].append(ingredient.ingredient_id)
    #print(l)
    session.ingList = l
    return l

def setIngredients(session, ing_list):
    
    for row in ing_list:
        if session.query(Ingredient).filter(Ingredient.name == row['name']).count()==0:
            #print("new record!!")
            ing = Ingredient(row['name'],
                             row['pump'],
                             alcool=row['alcool'],
                             duration=row['time'],
                             qty_avail=row['qty'])
        else:
            ing = session.query(Ingredient).filter(Ingredient.name == row['name']).one()
            #print("Update!!")
            ing.pump = row['pump']
            ing.alcool = row['alcool']
            ing.duration = row['time']
            ing.qty_avail = row['qty']
            
        session.add(ing)
    session.ingList = None
    session.ingredients = None
    session.sysIngs = None
        
def delIngredients(session, ing_list):
    
    for ing in ing_list:
        session.delete(session.query(Ingredient).get(int(ing['id'])))
    session.ingList = None
    session.ingredients = None  

def getRecipe(session, cocktail):
    
    recipe_list = []
    for recipe, ingredient in session.query(Recipe, Ingredient).\
                        filter(Recipe.ingredient_id == Ingredient.ingredient_id).\
                        filter(Recipe.cocktail_id == cocktail).\
                        order_by(Recipe.order).all():
        recipe_list.append({'id' : ingredient.ingredient_id,
                            'name': str(ingredient.name), 
                            'qty': int(recipe.quantity)})
    return recipe_list

def setRecipe(session, cocktail):
#     print("**************** cocktail = %s" % cocktail)
#     print(cocktail['ingredients'])
    if session.query(Recipe).filter(Recipe.cocktail_id == cocktail['id']).count() == 0:
        i = 0
        for ing in cocktail['ingredients']:
            #print("1 %s" % ing)
            if ing[1] == 0:
                continue
            #print("2")
            i+=1
            r = Recipe(cocktail['id'], ing[0], i, quantity=ing[1])
            session.add(r)
    else:
        for r in session.query(Recipe).filter(Recipe.cocktail_id == cocktail['id']).all():
            session.delete(r)
        i = 1
        for ing in cocktail['ingredients']:
            if ing[1] > 0:
                r = Recipe(cocktail['id'], ing[0], i, quantity=ing[1])
                session.add(r)
                print("ing added: %d" %i)
                i += 1
#         l = session.query(Recipe).filter(Recipe.cocktail_id == cocktail['id']).order_by(Recipe.order).all()
#         i = 0
#         d = 0
#         for r in l:
#             try:
#                 if cocktail['ingredients'][i][1] == 0:
#                     session.delete(r)
#                     d +=1
#                 else:
#                     if d > 0:
#                         r.ingredient_id = cocktail['ingredients'][i-d][0]
#                     else:
#                         r.ingredient_id = cocktail['ingredients'][i][0]
#                     r.quantity = cocktail['ingredients'][i][1]
#                     session.add(r)
#                 i+=1
#             except IndexError:
#                 session.delete(r)
#         if len(cocktail['ingredients']) > len(l):
#             for i in range(len(l), len(cocktail['ingredients'])):
#                 if cocktail['ingredients'][i][1] == 0:
#                     continue
#                 r = Recipe(cocktail['id'], cocktail['ingredients'][i][0], i, quantity=cocktail['ingredients'][i][1])
#                 session.add(r)
#                 i+=1
        
def getServe(session, cocktail):
    sysIng = getSysRecipes(session)
    before = sysIng['before']
    after = sysIng['after']
    serve = []
    for recipe, ingredient, pump in session.query(Recipe, Ingredient, Pump).\
                        filter(Recipe.ingredient_id == Ingredient.ingredient_id).\
                        filter(Recipe.cocktail_id == cocktail).\
                        filter(Ingredient.pump == Pump.pump).order_by(Recipe.order).all():
        serve.append([str(pump.type), 
                      int(pump.i2cbus, 16), 
                      int(pump.i2caddr), 
                      float(int(ingredient.duration)*int(recipe.quantity)/1000), 
                      float(pump.ratio), 
                      str(pump.function)])
        
    return before+serve+after

        