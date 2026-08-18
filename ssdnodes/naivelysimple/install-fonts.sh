mkdir -pv /tmp/fonts
cd /tmp/fonts
wget https://github.com/be5invis/Iosevka/releases/download/v34.8.0/PkgWebFont-IosevkaAile-34.8.0.zip
wget https://github.com/be5invis/Iosevka/releases/download/v34.8.0/PkgWebFont-IosevkaEtoile-34.8.0.zip

unzip PkgWebFont-IosevkaAile-34.8.0.zip
mv WOFF2 /srv/http/naivelysimple/assets/fonts/
