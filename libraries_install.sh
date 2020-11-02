#!/bin/sh
pip3 install -U setuptools
pip3 install pymediawiki
pip3 install nltk
pip3 install vaderSentiment
pip3 install -U spacy
python3 -m spacy download en_core_web_lg