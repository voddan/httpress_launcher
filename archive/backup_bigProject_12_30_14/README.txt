This project is originally developed by
Vodopian Daniil dgvodopyan@gmail.com
for Parallels INC
as a part of MIPT internship 2014-2015

PROJECT:
The goal of this project is to create a way to launch
many instances of 'httpress' testing program
on a distributed cluster.

STRUCTURE:
httpress_launcher/
    archive/
    bin/
        hostlist/
        httpress_rh6
        httpress_mock.py
    scratches/
    src/
        httpress_launcher.py
    test/
    httpress_launcher.py
    README.txt

for USING you need:
    httpress_launcher.py -  executable, launches the rest of the code.
                            for details run 'httpress_launch.py --help'

    bin/httpress_rh6     -  executable, precompiled, runs tests from one localhost
                            for details run ' bin/httpress_rh6 -h'
                            make sure it suits your platform (Ubuntu, CenOS)
                            currently the name of the file is hardcodded in src/httpress_launcher.py

for DEVELOPMENT you may also need:
    src/                 -  directory with all code for production

    test/                -  directory with all unit tests

    bin/hostlist/        -  contains several examples of hostlists, which may be used for testing

    bin/httpress_mock.py -  executable, emulates successful run of bin/httpress_rh6 and the help message
                            very handy for testing since it does not use internet
                            currently the name of the file is hardcodded in src/httpress_launcher.py
