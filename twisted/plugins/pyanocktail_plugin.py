from twisted.application.service import ServiceMaker

pianocktail2 = ServiceMaker(
                           "Pianocktail", 
                           "pyanocktail.tap",
                           "A Pianocktail service",
                           "pianocktail")