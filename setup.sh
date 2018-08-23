#!/bin/bash
set -e
set -x

cd ~
apt-get update
apt-get install -y libssl-dev python3-gpg pinentry-tty git python3-pip apache2 wget
pip3 install https://github.com/ihaywood3/pgp-mime/archive/master.zip
pip3 install bitshares
pip3 install requests
if [ -d aud-gateway ] ; then
    cd aud-gateway
    git pull
    cd ..
else
    git clone https://github.com/ihaywood3/aud-gateway/
fi
if [ ! -h /usr/local/lib/cgi-bin ] ; then
    ln -s ~/aud-gateway/cgi-bin /usr/local/lib/cgi-bin
fi
if [ ! -h /var/www/gateway ] ; then
    ln -s ~/aud-gateway/web /var/www/gateway
fi
if [ ! -f /etc/apache2/sites-available/gateway.conf ] ; then
    ln ~/aud-gateway/gateway.conf /etc/apache2/sites-available/gateway.conf
fi
a2enmod include
a2enmod cgi
a2ensite gateway
a2dissite 000-default
systemctl restart apache2

mkdir /home/www-data
chown www-data:www-data /home/www-data
chmod 700 /home/www-data
sudo -H -u www-data -g www-data gpg  --import < ~/aud-gateway/web/key.asc
