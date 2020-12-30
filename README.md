# Monty_Python_Chatbot

A Chatbot for Monty Python
The code was executed and tested in a PyCharm Virtual environment.
It would be better if you test the code in Pycharm itself as running it on windows may have some problem as stuff like
spacy may not install properly there

To run the program in Google Collab
This is google drive link for the folder
https://drive.google.com/drive/folders/1JXIfkrcnrC3Cl9aLxTqAL86psyyW8hhN?usp=sharing

Just open the ipynb notebook and hit run. You would need to allow it to access your file system in the first cell
I am not sure if it will definitely work but if it does, it will be a lot easier to test

To run the program (in a linux environment or virtual)
1) Run the script libraries_install.sh. The script should install most of the things required to run my project, i.e
nltk, spacy, spacy language model large, setuptools, vaderSentiment, as well as pymediawiki
Unfortunately, the project would require you downloading a large language model from spacy which is about 800 mb.
However, I have included another script which would delete the downloaded model (model_uninstall.sh)

2) Make sure that all the files of the project are in the same directory

3) Run the main file by issuing a command like "python3 main.py
