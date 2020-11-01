# Name: Ranveer Singh
# Class and Section: CS 4395.001
# Net ID: rxs174730
# Python Chatbot

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
import spacy

# Load the stopwords
stop_words = stopwords.words('english')

# Load the spacy model
nlp = spacy.load("en_core_web_lg")


# Get the user name from the sentence given
def get_name_from_sentence(sentence: str):
    """
    Method for getting the user name from the sentence
    :param sentence: The sentence in which we need to search the user name
    :return: The user name detected
    """

    # Parsing the sentence using the spacy model
    doc = nlp(sentence)

    # First, we try to find the name through NER
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    # If that fails, we try through pos tagging
    for token in doc:
        if token.pos_ == "PROPN":
            return str(token)

    # If no name detected, we return an empty string
    return ""


def parse_sentiment(response):
    """
    Method for parsing the sentiment of the response
    :param response: The response to parse sentiment of
    :return: The sentiment score which is positive for positive sentiments and negative for negative sentiments
    """
    sid = SentimentIntensityAnalyzer()
    ps = sid.polarity_scores(response)
    return ps['pos'] - ps['neg']


def get_query(response):
    """
    Method for getting a valid query from the response
    :param response: The response to parse
    :return: The parsed response
    """
    # We have to parse the sentence to get information about stuff the user is trying to answer
    # We are going to preprocess the response by tokenizing it, lowercasing it, removing any stopwords
    tokens = nltk.tokenize.word_tokenize(response)
    tokens = [t.lower() for t in tokens if t.isalpha() and t not in stop_words]
    return ' '.join(tokens)


def get_information_from_text(response):
    """
    Method to extract user information from the response text
    :param response: The response that we need to parse
    :return: The parsed information
    """
    doc = nlp(response)

    # We filter the tokens based on different criteria
    tokens = [token for token in doc if token.dep_ not in ["nsubj", "aux"] and token.pos_ not in ["AUX"]]
    tokens = [str(token) for token in tokens if (token.dep_, token.tag_) not in [("ROOT", "VBP")]
              and str(token.text) not in ['.', 'also']]
    return " ".join(tokens)
