# Maintainer: Bertrand Verdu <Choubidouha At gmail Dot com>
pkgname=pyanocktail
pkgver=0.5
pkgrel=1
pkgdesc="A Pianocktail Server In Python using Twisted"
arch=('any')
url="https://github.com/bverdu/Pyanocktail"
license=('LGPL2')
depends=('python2' 'setuptools' 'python2-pyalsa' 'twisted' 'python2-sqlalchemy' 'python2-autobahn' 'i2c-tools')
source=(http://sourceforge.net/projects/pianocktail/files/$pkgname-$pkgver.tar.gz)
md5sums=('038d600e7e7828b581e73a2496da9f27')

package(){
cd "$srcdir"/"$pkgname"-"$pkgver"
python2 setup.py install --root="$pkgdir"
chown -R piano:piano "$pkgdir/usr/share/pianocktail"
chown -R piano:piano "$pkgdir/etc/pianocktail"
}
 
