# Maintainer: Bertrand Verdu <Choubidouha At gmail Dot com>
pkgname=pyanocktail-git
pkgver=20140626
pkgrel=1
pkgdesc="A Pianocktail Server In Python using Twisted Git version"
arch=('any')
url="https://github.com/bverdu/Pyanocktail"
license=('LGPL2')
depends=('python' 'python-setuptools' 'python-numpy' 'python-pyalsa' 'python-twisted' 'python-sqlalchemy' 'python-autobahn' 'i2c-tools')
md5sums=('SKIP')
source=("git+https://github.com/bverdu/Pyanocktail.git")

build(){
	cd "${srcdir}"
    msg "Connecting to GIT server...."

    if [ ! -d ${pkgname} ]; then
        git clone ${_gitroot} ${pkgname} --depth=1 || return 1
    fi

    cd ${pkgname}
    git pull master || return 1

    msg "GIT checkout done"

    msg "Starting make..."
}

package(){
cd "$srcdir"/"$pkgname"
python setup.py install --root="$pkgdir"
#chown -R piano:piano "$pkgdir/usr/share/pianocktail"
#chown -R piano:piano "$pkgdir/etc/pianocktail"
}
 
