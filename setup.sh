#!/bin/bash
set -e
set -x

cd ~
apt-get update
apt-get install -y python3-gpg pinentry-tty git python3-pip apache2 wget
pip3 install https://github.com/ihaywood3/pgp-mime/archive/master.zip
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

mkdir /var/local/gpg-keys
chown www-data:www-data /var/local/gpg-keys
chmod 700 /var/local/gpg-keys/
sudo -u www-data -g www-data gpg --homedir /var/local/gpg-keys/ --import <<EOF
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQSuBFqbZI4RDAD2vdrFJhs8bVh4V56xBd1FE2vegY5xWVKAp9oxu4j82gWnp/V8
pnE6swHZc5Fl7PsicYlYVsLzePI3uyf0SNfNuC1KIgaPGRFQtM2yMb6ktQYPJiCI
zb/s6AdWoQ7zaPbptRn/xYMR7TmmTtx1pi7g+HbZknoKNygjrKRmbxyAAj96udtq
prOlsOVV0fjPL7L+hoVHnP/cHxppIroCSxsBOzTyQ+kvC8+BzeG5Dhy/R0lE3Nbp
v1L5h6p/x88DOfn7kUCdDweq2g8gqHWbO09m5qvUBVteRVyDSJN1Yoc5HiCml1B+
DojlbOJXfab7PP9yCFKCuhLKIuDCjv7EpI5ogi3tkXK19MOn15jGNWwFLNcsTiqx
ZOAPumio/GTJReNdzHj0c8znyDDSHh1R/qLtIr8nh3GpeOQemq0VoTOOfs3O4H8y
V6NWQvg/+J8ha5L3K8pW88+qbupCOqUMbNJ4d5C2yNv/TqSniEsTvUIcBWM0jp0y
4mb6c8IVxVt2DE8BAOf8Pz8OBcldk5xXSYJyV5k4ycoko3pGp2WG87/zLiaDC/9l
PxHKGxUJia+2+xjQNHfx7/61F5HZ+ZelkzPbOSahMipnpb+DDrevK5UXuQWExgWP
Ky4oyGXQVQbOHTRWUXY2UArggNeOVhORpduUmO3q3hfhBKV0aqAkVDHfPXi/qvr2
7NxXJAhSvZ6XEwNayRB1WFqhieI3tmBnMgdt8zgJ4cfLhrpaKbE0/gxhgA3lr9UO
TZNRxgnFtVD0OD8bqybGXuH5AB8YhpxvJpJOdbfz1wngSxih/aJU7hAyW6M2F/58
GhMr0V46c1YzLh1AV1mNdUNXbCV21fTf1a5Ng7DkP7dczfRzv6cPTPG9+Fwh7VZA
1F4LBsWlxqfJWdZQ8mMKiRG3ffMPzkKJPvNbqgIsmONk9TKm+lC/her9Wy5pNKji
fKsw+55/L2ucRXqcslryLqfStxxZbsIZ0SMUcS4gRprSCTSnNn5jj4RwBiYM+8YZ
nY7WjtuWVbSIhbgJIIF9gRBsDNUJcnVwFhBnDuZjSuxyioxzTYQ9/txFe9RicAIL
/RH859TzMMd9dwhoFPfbC+nac4AEUFjHPnjQqjrfeS/8EOZNBTiabdoSbcSLSU4K
g8zeBuohdYLbDN+qmAJrmyE/HfowDh8JlHYCyAoBQEIMJOoT1Jkd8ZTU7fHTZU6k
vtMo1e4aN9ZnszuWX5K6nX5brr4EHogGZKU3vIEGU2nB96xzZYBbBn1ksf7wwuUi
MBvfAXFma1V/dy2F67tOEZRVUpPjfiWJPMvAQi15DAIb0WX1uEjdEHl4/SXUC3hf
qU9kMOZmS8Auos384A46+B/OlfDgvE6NjHuHlxBexsF1YRwyfVNm5Vcsf8h98qx/
Y0CvUckFu8qzhNTK/nYgLureB/ZtkKREw/m5ePJtLuR5TD3rlKSKniV2EM4Yt0vj
xMCf2fqJkorAlty1zrSCWwAGxGsOJX515xFwLxlRYHcT8ORhxUFyyOdl0mSkbnXO
8l9Xm7NrNL7ae5rQ9Z43iFP5w1vOdWvY+faZVsZbPKt7gSb0jN6iurSvZgS6hJl3
Y7QfUml2ZXIgU3RvbmUgPGlhbkBoYXl3b29kLmlkLmF1Poh6BBMRCAAiBQJam2SO
AhsDBgsJCAcDAgYVCAIJCgsEFgIDAQIeAQIXgAAKCRCs/l/un8LPeChhAQCiaRUA
D1GmHoHhlLqURzETPIVscRNUmMBKJXEW35xXJgEAxqwN+ghikZIFZLAxkYqwN1Om
1dwq5tUlW6fddRReS4u5Aw0EWptkjhAMAJpnkUjZmj23KdQh7T4a9L0I7+40ylzk
f95muBKIHGFm/lp//VSdckHA7HNoC6jio3Q/Xu4cZGBc7Q1v8m27Bv5HYqIkHhHS
msuLqcICe8XnzNnlZYSjf+lpm9gSAxthfu4vuo+5fmM5hLI5ZGYgDbP0weVw/iw1
4x6OVVXnR1F4uk1ymkcqrzRLTuBNR3mamD45jWUFeg03JgkzjjiY4L020FXeqNk5
84fkXxK34U7pSxVLpFB6YOH9MuF7kGoMWq89DEwmVUmjTZ66EEezwkZlbdnrb5Af
t1w18TeVhgqPzkN41IH2NFtJyrfrel36OXB2EhKlkvzMiS47hLEiIzqTwCCOLn6j
4vNgWkouxd57MLlqqqtaModlYz+zAzx9p6PAswoyYuKxgSywHxIBFbiEgKItUQRn
v1Kz2UY+Ca2Bhl7u58m3B/4W0u1rwRiJBCxpxMoM1ZAyw5NJM46y3EJRLU0BE6Qn
DZfrpIWfEO4nhY2KwvF3gSlxjseGZLeEwwADBQv/WZtc6MawN+oGaFjRNpfuaDuI
57NCoeMY+Cb8knR40TebV9bdUdJ39wVDr0YtLKYIlNobe4swQcwPNN91Txfq8B7q
bot0w1gLFJ1Uo5SMZ3PtUXyS2HHUCeFCZ9R/tJqLo6n0ixUhz1RlgomR4NsKS7C+
4g1L9e07lMeIj6BvvSUIpy6uu7dvXGxkchu3zRRKK99NmUTqWDldfDGlYeOelzee
nbxoqYhPPl1V2/RDpeOqvdWaNYYrz8hGwTZjXM+h5j6NVe+mTT7PuLZFgeSz3WuN
8N9uv0WDsFkV4flGfPAZ6rwzKh0p+JbNgt4NBxDvs8GykJLfs6qoscJRcQ6u1lT4
yGd17+o3A/tYs5rJ66y87QxGlEOaK70fLHeKyQVE2vle1BS2GqB8DHqVg9oHLD/v
KQk+hZPanOiq/0ISx+nHZ5MGRNsa5gTuCgHoOocMNI3SfD0NdLtKK1J+HHDiWBJt
9ouoWY2xnoYjre4J5dcmlqmZyQbveP2fjqC8+gqbiGEEGBEIAAkFAlqbZI4CGwwA
CgkQrP5f7p/Cz3iqiwD/TPQ5loqdDp9YhQd5XvxoHSWi0dGR4HuhvTJazr9T67IB
AIFPOmduZ240pqpplSzfzEfJNglO0LayGcMrV3dV2Kg4
=fN3S
-----END PGP PUBLIC KEY BLOCK-----
EOF
