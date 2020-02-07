
export HOMEBIN=$HOME/bin
mkdir -p $HOMEBIN

tar xvf archives.tar.gz || exit 0
cd archives

sh cmake-3.12.0-Linux-x86_64.sh --prefix=$HOME --exclude-subdir
export PATH=$HOMEBIN:$PATH
cmake --version

cd swipl-devel
cp build.templ build
sed -i 's,doc=out-of-date,doc=dont-download,g' prepare
./build
cd ..

cd SFST/src/
sed -i "s,DESTDIR = /usr/local/,DESTDIR = $HOME/," Makefile
make install
cd ../../

python3.6 -m venv venv
source venv/bin/activate

for whl in whl/*.whl;do
  pip install --no-dependencies $whl
done

cd ParZu/external/Wapiti
make
cd ../..

# configure clevertagger
sed -i "s,^SMOR_MODEL =.*$,SMOR_MODEL = '$PWD/external/zmorge-20140521-smor_newlemma.ca'," external/clevertagger/config.py
sed -i "s,^CRF_MODEL =.*$,CRF_MODEL = '$PWD/external/hdt_ab.zmorge-20140521-smor_newlemma.model'," external/clevertagger/config.py
sed -i "s,^CRF_BACKEND_EXEC =.*$,CRF_BACKEND_EXEC = '$PWD/external/Wapiti/wapiti'," external/clevertagger/config.py

# configure ParZu
cp config.ini.example config.ini
sed -i "s,^smor_model =.*$,smor_model = $PWD/external/zmorge-20150315-smor_newlemma.ca," config.ini
sed -i "s,^taggercmd =.*$,taggercmd = $PWD/external/clevertagger/clevertagger," config.ini


nohup python parzu_server.py --host 0.0.0.0

sleep 10

# to test
curl -H "Content-Type: application/json" -X POST -d '{"text": "Ich bin ein Berliner."}' "http://localhost:5003/parse/"

