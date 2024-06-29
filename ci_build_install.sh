#!/bin/bash

# execute in the unichat directory
# unichat
# |
# _/unichat
# |
# _/tests
#
#
# create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# install requirements
pip install -r requirements.txt

# execute unittests
export PYTHONPATH=$PYTHONPATH:'unichat/'
python -m unittest discover -s tests/unittests
pytest tests/pytests

# static code analyzier 
pylint unichat --exit-zero

# building with setuptoos 
python setup.py sdist 
# installing unichat as a pip package to venv
pip install . 

# after this you can execute `python -m unichat` and the app runs
# (assumed you have an .env file with telegram API keys in your home dir)
#
# in a python shell you can `import unichat` `unichat.run_app()`
# and the app should run

