'''
Created on 29 sept. 2013

@author: babe
'''
from sqlalchemy import and_, or_
from pyanocktail.dbUtils import initdb, Cocktail, Recipe,\
 Ingredient, Pump, getCocktails, getIngredients, getRecipe,\
 getServe, getPumps
from docutils.nodes import row


if __name__ == '__main__':
    session = initdb('mysql://test:test@localhost/testdb',False)
#     print(session)
#     test1 = Pump(1,description='test1')
#     session.add(test1)
#     session.commit()
#     test2 = Ingredient('Jus d\'Orange',1, description='tu prends une orange et la presse !',alcool=False)
#     session.add(test2)
#     session.commit()
#     test3 = Pump(2,description='test3')
#     session.add(test3)
#     session.commit()
#     test4 = Ingredient('Rhum',2, description='no comment')
#     session.add(test4)
#     session.commit()
#     test5 = Cocktail('Rhum-Orange',description='test5')
#     session.add(test5)
#     session.commit()
#     test6 = Recipe(2,4,1)
#     session.add(test6)
#     session.commit()
#     test7 = Recipe(2,3,2,3)
#     session.add(test7)
#     session.commit()
#     for row in session.query(Recipe, Recipe.cocktail_id).all(): 
#         print row.Recipe.ingredient, row.cocktail_id 
#     disabled_cock = []
#     alcool = False
#     for r in session.query(Recipe).all():
#         if (r.ingredient.qty_avail  < 1) or (r.ingredient.alcool != alcool):
#             disabled_cock.append(r.cocktail)
#         else:
#             print("cocktail OK: %s" % r.cocktail)
#         print(disabled_cock)
    alcool = False
#     for r in session.query(Recipe.cocktail).filter(Recipe.ingredient.in_((Ingredient.ingredient_id).filter(Ingredient.alcool == alcool).filter(Ingredient.qty_avail > 0))):
#         print r.name
            
#     for part in session.query(Recipe).\
#                     filter(Recipe.ingredient_id == 3).\
#                     filter(Recipe.order == 2): 
#         print part.cocktail
#         
#     for r in session.query(Recipe).\
#                     filter(Recipe.ingredient_id.\
#                     in_(session.query(Ingredient.ingredient_id).\
#                     filter(Ingredient.alcool == alcool))):
#         print r.ingredient_id
        
#     for cocktail in session.query(Cocktail).all():
#         print(cocktail)
#         for r in session.query(Recipe).\
#                     filter(Recipe.ingredient_id.\
#                     in_(session.query(Ingredient.ingredient_id).\
#                     filter(or_(Ingredient.alcool != alcool ,\
#                     Ingredient.qty_avail == 0)))).all():
#             print r.cocktail
#             if r.cocktail == cocktail:
#                 print("discarded : %s" % cocktail.name)
#             else:
#                 print("accepted : %s" % cocktail.name)
#             
#     print(session.query(Recipe).\
#                     filter(Recipe.ingredient_id.\
#                     in_(session.query(Ingredient.ingredient_id).\
#                     filter(or_(Ingredient.alcool != alcool ,\
#                     Ingredient.qty_avail == 0))))).all()
#     session.add(Cocktail('Jus d\'orange',description='du pur jus sans alcool'))
#     session.commit()
#     session.add(Recipe(3,3,1,2))
#     session.commit()
    cocktails= []
    discarded = []
    reason = []
#     if alcool == False:
#         for cocktail, recipe, ingredient  in session.query(Cocktail, Recipe, Ingredient).\
#                                 filter(Cocktail.cocktail_id == Recipe.cocktail_id).\
#                                 filter(Recipe.ingredient_id == Ingredient.ingredient_id).\
#                                 filter(or_(Ingredient.qty_avail < Recipe.quantity, Ingredient.alcool != alcool)).all():
#             discarded.append(cocktail)
#             
#     for cocktail in session.query(Cocktail).all():
#         try:
#             discarded.index(cocktail)
#         except:
#             cocktails.append(cocktail)
#                 
#     print(discarded)
#     print(cocktails)
    
#     if alcool == False:
#         r = 0
#         for cocktail, recipe, ingredient  in session.query(Cocktail, Recipe, Ingredient).\
#                                 filter(Cocktail.cocktail_id == Recipe.cocktail_id).\
#                                 filter(Recipe.ingredient_id == Ingredient.ingredient_id).\
#                                 filter(or_(Ingredient.qty_avail < Recipe.quantity, Ingredient.alcool != alcool)).all():
#             discarded.append(cocktail)
#             if ingredient.alcool:
#                 r += 2
#                 if ingredient.qty_avail < recipe.quantity:
#                     r+= 1
#             else:
#                 r = 1
#             reason.append(r)
#     else:
#         for cocktail, recipe, ingredient  in session.query(Cocktail, Recipe, Ingredient).\
#                                 filter(Cocktail.cocktail_id == Recipe.cocktail_id).\
#                                 filter(Recipe.ingredient_id == Ingredient.ingredient_id).\
#                                 filter(Ingredient.qty_avail < Recipe.quantity).all():
#             discarded.append(cocktail)
#             reason.append(1)
#             
#     for cocktail in session.query(Cocktail).all():
#         try:
#             r = discarded.index(cocktail)
#             print(reason)
#             print(reason[r])
#             cocktails.append([cocktail, reason[r]])
#         except:
#             cocktails.append([cocktail, 0])
#                 
#     print(discarded)
#     print(cocktails)
#         
    print(getCocktails(session, alcool))
    print(getIngredients(session))
    print(getPumps(session))
    print(getRecipe(session, 3))
    print(getServe(session, 2))
    