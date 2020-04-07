import setuptools
from setuptools import setup
from setuptools.command.install import install
import os
print(os.getcwd())
# class MyInstall(install):
#     def run(self):
#         install.run(self)
#         # path = os.getcwd().replace(" ", "\ ").replace("(","\(").replace(")","\)") + "/bin/"
#         # os.system("echo 'Setting up Tzara.desktop'")
#         os.("bash "+os.getcwd()+"install_mecab.sh")
#         # os.system("sh "+path+"desktopsetup.sh")

packages = setuptools.find_packages()
setup(name="Kore-language-processor",
      version="0.1",
      packages=packages,
      install_requires=['Pattern==3.6',
                        'tinysegmenter==0.4',
                        'nltk==3.4.1',
                        'mosestokenizer==1.1.0',
                        'Sastrawi==1.0.1',
                        'konlpy==0.5.2'
                        ],
      include_package_data=True
      )
