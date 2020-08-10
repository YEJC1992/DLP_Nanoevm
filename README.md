# DLP_Nanoevm

Installation Steps:

#Install required packages/software

1. Install python3, git, pandas,numpy and matplotlib on your linux machine

#Install HIDAPI

2A.
    $ sudo apt-get install python3-dev libusb-1.0-0-dev libudev-dev
    $ sudo pip3 install --upgrade setuptools
    $ sudo pip3 install hidapi


OR

2B. 
    $ sudo apt-get install python3-dev libusb-1.0-0-dev libudev-dev
    $ git clone https://github.com/trezor/cython-hidapi.git
    $ cd cython-hidapi
    Initialize hidapi submodule:
    $ git submodule update --init
    Build cython-hidapi extension module:
    $ python setup.py build
    Install cython-hidapi module into your Python distribution:
    $ sudo python setup.py install
    
#Get the code

3. git clone https://github.com/AnishaDatla22/DLP_Nanoevm.git

#Run the code

4. sudo python3 main.py    



