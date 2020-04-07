#!/usr/bin/env bash

set -e

# Set mecab related variable(s)
mecab_home="/data/FAQ/Korean/mecab"
mecab_dic=${mecab_home}"/lib/mecab/dic/mecab-ko-dic"

export PATH=${mecab_home}/bin:$PATH

# source /data/py3.6.7/venv/bin/activate

install_mecab_ko(){
    cd /tmp
    curl -LO https://bitbucket.org/eunjeon/mecab-ko/downloads/mecab-0.996-ko-0.9.2.tar.gz
    tar zxfv mecab-0.996-ko-0.9.2.tar.gz
    cd mecab-0.996-ko-0.9.2
    ./configure --prefix=${mecab_home}
    make
    make check
    make install
}

install_mecab_ko_dic(){
    echo "Install mecab-ko-dic to --> ${mecab_dic}"
    cd /tmp
    curl -LO https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/mecab-ko-dic-2.1.1-20180720.tar.gz
    tar -zxvf mecab-ko-dic-2.1.1-20180720.tar.gz
    cd mecab-ko-dic-2.1.1-20180720
    ./autogen.sh
    ./configure --prefix=${mecab_home}
    if [[ $os == "Linux" ]]; then
        mecab_lib=`mecab-config --libs-only-L`
        export LD_LIBRARY_PATH=${mecab_lib}:$LD_LIBRARY_PATH
    fi
    make
    echo "dicdir=${mecab_home}/lib/mecab/dic/mecab-ko-dic" > ${mecab_home}/etc/mecabrc
    make install
}

install_mecab_python(){
    pushd /tmp
    if [[ ! -d "mecab-python-0.996" ]]; then
        git clone https://bitbucket.org/eunjeon/mecab-python-0.996.git
    fi
    popd
    pip install /tmp/mecab-python-0.996
}


if hash "mecab" &>/dev/null; then
    echo "mecab-ko is already installed"
else
    echo "Install mecab-ko"
    install_mecab_ko
fi

if [[ -d $mecab_dic ]]; then
    echo "mecab-ko-dic is already installed"
else
    echo "Install mecab-ko-dic"
    install_mecab_ko_dic
fi

if [[ $(python -c 'import pkgutil; print(1 if pkgutil.find_loader("MeCab") else 0)') == "1" ]]; then
    echo "mecab-python is already installed"
else
    echo "Install mecab-python"
    install_mecab_python
fi

echo "Done."
