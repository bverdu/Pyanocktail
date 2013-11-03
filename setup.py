# ==== twisted/plugins/pyanocktail_plugin.py ====
'''setup.py for Pianocktail.

After installation the application should be manageable as a twistd
command.

For example, to start it in the foreground enter:
$ twistd -n Pianocktail

To view the options for Pianocktail enter:
$ twistd Pianocktail --help
'''

__author__ = 'Bertrand Verdu'


import sys

from distutils.core import setup

def refresh_plugin_cache():
    from twisted.plugin import IPlugin, getPlugins
    list(getPlugins(IPlugin))

if __name__ == '__main__':
    
    if sys.version_info[:2] >= (2, 4):
        extraMeta = dict(
            classifiers=[
                "Development Status :: 4 - Beta",
                "Environment :: No Input/Output (Daemon)",
                "Programming Language :: Python2.7",
            ])
    else:
        extraMeta = {}

    setup(
        name="Pianocktail",
        version='0.5',
        description="Pianocktail server.",
        author=__author__,
        author_email="bertrand.verdu@gmail.com",
        url="http://github.com/bverdu/Pyanocktail",
        packages=[
            "pyanocktail",
            "twisted.plugins",
        ],
        package_data={
            'twisted': ['plugins/pyanocktail_plugin.py'],  
        },
        data_files=[('/usr/share/pianocktail/html', ['html/Pianocktail.html']),
                    ('/usr/share/pianocktail/html', ['html/config.html']),
                    ('/usr/share/pianocktail/html', ['html/analyze.html']),
                    ('/usr/share/pianocktail/html', ['html/pumps.html']),
                    ('/usr/share/pianocktail/html', ['html/recipes.html']),
                    ('/usr/share/pianocktail/html', ['html/pianocktail.js']),
                    ('/usr/share/pianocktail/html', ['html/style.css']),
                    ('/usr/share/pianocktail/scripts', ['scripts/PIANOCKTAIL.sci']),
                    ('/usr/share/pianocktail/scripts', ['scripts/RECETTE.sci']),
                    ('/usr/share/pianocktail/scripts', ['scripts/TEMPO.sci']),
                    ('/usr/share/pianocktail/scripts', ['scripts/TONALITE.sci']),
                    ('/usr/share/pianocktail/scripts', ['scripts/METRIQUE.sci']),
                    ('/usr/share/pianocktail/html/fonts', ['html/fonts/DEFTONE.ttf']),
                    ('/etc/pianocktail', []),
                    ('/usr/share/pianocktail/db', []),
                    ('/usr/lib/systemd/system', ['pianocktail.service']),
                    ('/usr/lib/systemd/system', ['pianocktail_80.service']),
                    ('/usr/lib/systemd/system', ['pianocktail_80.socket'])],
          **extraMeta)
    
    refresh_plugin_cache()
