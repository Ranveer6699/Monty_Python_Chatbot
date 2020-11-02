# Name: Ranveer Singh
# Class and Section: CS 4395.001
# Net ID: rxs174730
# Python Chatbot

# Get information regarding the query
import spacy
import json
import random
import operator
import time
from mediawiki import MediaWiki
from difflib import SequenceMatcher


nlp = spacy.load("en_core_web_lg")
# We are making a dictionary of topics that our model would be capable of answering
# topics = dict()
topics = json.load(open("topics.json", "r"))

bot_responses = json.load(open("responses.json", "r"))

wikipedia = MediaWiki()


def string_similarity(a, b):
    """
    Measures the similarity of the two given strings. The function is a wrapper on the difflib SequenceMatcher
    :param a: The first string
    :param b: The second string
    :return: The similarity between the two strings
    """
    return SequenceMatcher(None, a, b).ratio()


def deep_topic_matching(query, resolved_key=None):
    """
    Matches the query with the list of topics available. The algorithm tends to go a level deeper as compared to
    shallow_topic_matching. The algorithm tends to go a level deeper for each key when it tries to resolve the topic
    :param query:
    :param resolved_key:
    :return: The topic with the highest match
    """
    # If the query matches with one of the topics, we prompt them for further questions
    matching_list = []
    query_tokens = nlp(query)

    # If we are matching with the topic values directly instead of first matching with a topic key
    if not resolved_key:
        for key, values in topics.items():
            for value in values:
                value_tokens = nlp(value)
                for p in query_tokens:
                    for q in value_tokens:
                        matching_list.append((key, p, value, p.similarity(q), string_similarity(value, query)))

    # If the query has already matched with a topic key
    else:
        values = topics[str(resolved_key)]
        for value in values:
            value_tokens = nlp(value)
            for p in query_tokens:
                for q in value_tokens:
                    matching_list.append((resolved_key, p, value, p.similarity(q), string_similarity(value, query)))

    # We sort the list of matches by their similarity metrics: The token similarity built in Spacy as well as string
    # match

    matching_list = sorted(matching_list, key=operator.itemgetter(4, 3), reverse=True)
    return matching_list[0]


def shallow_topic_matching(query, curr_user):
    """
    Resolves the query by performing a shallow topic matching where it search for the topic key in the query
    :param curr_user: The current user of the bot
    :param query: The query to be searched
    :return: The topic with the highest similarity
    """
    # If the query matches with one of the topics, we prompt them for further questions
    query_tokens = nlp(query)
    max_similarity = ("", "", "", 0, 0)

    key_tokens = nlp(' '.join(topics.keys()))
    for p in query_tokens:
        for q in key_tokens:
            if p.similarity(q) > max_similarity[3]:
                max_similarity = (q, p, q, p.similarity(q), string_similarity(str(q), query))

    # We try to resolve the deep matching for the same query and the given key
    max_similarity = deep_topic_matching(query, str(max_similarity[2]))
    if max_similarity[3] < 0.9:
        print(f"SillyBot: These are the {max_similarity[0]}. Can you be more specific\n")
        time.sleep(1)
        temp_topics = '\n'.join(topics[str(max_similarity[0])])
        print(f"SillyBot:\n{temp_topics}\n")
        time.sleep(3)
        query = input(f"{curr_user['name']}: ")
        print()
        max_similarity = deep_topic_matching(query, str(max_similarity[0]))

    else:
        print(f"SillyBot: Do you want to know more about {max_similarity[2]}. "
              f"If not, please select from the options below."
              f" Otherwise, press enter")
        time.sleep(1)
        temp_topics = '\n'.join(topics[str(max_similarity[0])])
        print(f"SillyBot:\n{temp_topics}\n")
        time.sleep(3)
        query = input(f"{curr_user['name']}: ")
        print()
        if query:
            max_similarity = deep_topic_matching(query, str(max_similarity[0]))
    return max_similarity


def manage_empty_sections(wiki_page, section_name):
    """
    Some sections returned by the wikipedia api tend to be empty due to formatting issues. The function tries to salvage
    the failed query by trying to return links embedded in that section
    :param wiki_page: The page we are searching in
    :param section_name: The section we need to deal with
    :return: Void. It prints the returned links in the function instead
    """

    print("SillyBot: I may not be able to answer this question accurately. I am a silly bot after all\n")

    # Get the links for the page  section
    links = wiki_page.parse_section_links(section_name)

    # If any links are returned
    if len(links) > 0:
        # The links are returned as a list of tuples with the first value of each tuple actually containing
        # the link title in question
        links = [link[0] for link in links]
        print("\n".join(links))

    # If we are unable to return anything, we give out a statement indicating failure
    else:
        print("SillyBot: I am Sorry Dave, I can't answer the question. Oops! Wrong reference\n")


def answer_wiki_page(similarity_tuple, curr_user):
    """
    The method for getting the wiki page for the given title, displaying relevant information about the sections
    and getting user input on the topics they want answered present in the page
    :param similarity_tuple: The tuple which contains the string with the highest similarity
    :return: None
    """

    # Get the wiki page for the given title
    wiki_page = wikipedia.page(str(similarity_tuple[2]))

    # Flag indicating whether we need to print out the summary
    summary_flag = True

    # Printing the list of topics (sections) in a page we can provide information on
    print(f"SillyBot:\nThese are the topics about the {wiki_page.title} I can answer!")
    page_sections = wiki_page.sections
    print("\n".join(page_sections))

    # Asking the user for their choice
    exit_query = "Otherwise, you can press '!' followed by enter to exit.\n"
    bot_response = bot_responses["Choices"][random.randint(0, len(bot_responses["Choices"]) - 1)]
    input_query = "\nSillyBot:\n" + bot_response + exit_query + "\n" + curr_user["name"] + ": "
    response = input(input_query)
    print()
    # While the response is not '!'
    while response != '!':
        sim = []
        if response != "!":
            # We parse the user response to get the section or topic they want answered
            response_tokens = nlp(response)
            for section in page_sections:
                for section_tokens in nlp(section):
                    for rt in response_tokens:
                        sim.append((section, rt, section_tokens.similarity(rt), string_similarity(section, response)))

            # Sorting the topic matches based on the spacy similarity score as well as the string similarity
            sim = sorted(sim, key=operator.itemgetter(3, 2), reverse=True)

            # Providing user information about the selected topic
            print(f"SillyBot: You want to know more about {str(sim[0][0])}\n")
            raw_text = wiki_page.section(str(sim[0][0]))

            # If the response returned is not empty, we print the response
            if len(raw_text) > 0:
                print(raw_text)
                print()

            # Otherwise, we try to salvage the links to print
            else:
                manage_empty_sections(wiki_page, str(sim[0][0]))
                print()

            # Delay between the user response as well as the next query
            time.sleep(3)

            summary_flag = False

            # Asking users if they want to know anything else about the topic
            print(f"SillyBot: Is there anything else about {wiki_page.title} you want to know?!\n")
            print("\n".join(page_sections))
            bot_response = bot_responses["Choices"][random.randint(0, len(bot_responses["Choices"]) - 1)]
            input_query = "\nSillyBot:\n" + bot_response + exit_query + "\n" + "User: "
            response = input(input_query)
            print()

    # If the user decided to exit and they didn't ask any questions, we give them a summary of the topic instead
    if response == "!":
        if summary_flag:
            print(f"\nSillyBot: You don't want anything to learn about {wiki_page.title}! "
                  f"I will still give you a summary\n")
            print(wiki_page.summary)


def process_wiki_page(similarity_tuple: tuple, curr_user):
    """
    Method for processing the wiki page based on the topics matches. The function is basically a wrapper around a try
    catch statement for the answer_wiki_page method
    :param curr_user: Current user for the bot
    :param similarity_tuple: The tuple which contains the matched topic
    :return: None
    """
    try:
        answer_wiki_page(similarity_tuple, curr_user)

    # If we encounter any error while answering the question, we exit
    except:
        print("\nSillyBot:\n" + bot_responses["Confusion"][random.randint(0, len(bot_responses["Confusion"]) - 1)])


def get_data(query: str, curr_user):
    """
    Method for getting data about the query
    :param curr_user: The current user
    :param query: The query made by the user to be answered
    :return: The max_similarity tuple which contains the topic matched by the query
    """
    # We would first preprocess the response and get the simiarity tuple
    max_similarity = shallow_topic_matching(query, curr_user)

    # We will process the wiki page for the given topic
    process_wiki_page(max_similarity, curr_user)
    return max_similarity
