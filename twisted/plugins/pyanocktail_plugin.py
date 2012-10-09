from twisted.application.service import ServiceMaker

pianocktail = ServiceMaker(
                           "Pianocktail", 
                           "pyanocktail.tap",
                           "A Pianocktail service",
                           "pianocktail")