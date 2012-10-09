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

try:
    from twisted.web import websockets
except ImportError:
    raise SystemExit("twisted websockets not found.  Make sure you "
                     "have installed the websockets branch of Twisted core package.")

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
        version='0.4',
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
        **extraMeta)
    
    refresh_plugin_cache()
