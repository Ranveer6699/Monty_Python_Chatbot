# Name: Ranveer Singh
# Class and Section: CS 4395.001
# Net ID: rxs174730
# Chatbot for Monty Python

import os
import json
import users
import parse_text
import monty_python_data
import warnings
import random
import nltk

# Not a good practice, but for  visual sake
warnings.filterwarnings("ignore")

# Loading, some of the template responses based on Python Jokes
bot_responses = json.load(open("responses.json", "r"))


def get_user():
    """
    Method for beginning the user conversation. The method introduces the bot and
    gets the user based on the name extracted
    :return: The yser with which the system is conversing
    """

    # Create the dataset if it doesn't already exist
    if not os.path.exists("users.json"):
        users.create_user("root", "users.json")

    flag = -1

    while flag == -1:
        # Sentence tokenization on the initial response of the user following the introduction
        sentence_list = nltk.sent_tokenize(
            input("SillyBot:\n" +
                  bot_responses["Introduction"][random.randint(0, len(bot_responses["Introduction"]) - 1)]
                  + "\n" + "User: "))
        print()
        # We assume that the user name is going to be in the first sentence
        sentence = sentence_list[0]

        # Get the user name from the sentence
        name = parse_text.get_name_from_sentence(sentence)

        # if a name is not detected, we ask the user to enter their name again
        while not name:
            print("SillyBot: Don't be Silly! Please enter a proper name")
            sentence_list = nltk.sent_tokenize(input("SillyBot: What is your name?\n\nUser: "))
            print()
            sentence = sentence_list[0]
            name = parse_text.get_name_from_sentence(sentence)

        # We create a user based on the given name
        curr_user, flag = users.create_user(name, "users.json")

        # We parse the remaining sentences to extract any relevant user information and add that to the user
        curr_user = users.add_information_unlabelled(curr_user, sentence_list[1:])

        # If the user already exists (based on the error code returned by the create_user method, we do the entire thing
        # again)
        if flag == -1:
            print("SillyBot: I am a Silly bot! You have a name matching someone else.\n"
                  "I can't remember two people with the same name!")

    # Return the current user
    return curr_user


def monty_python_converse(curr_user):
    """
    Method for conversing with the user about monty Python
    :param curr_user: The current user talking with the chatbot
    :return: None
    """

    # Ask the user what they want to know about Monty Python
    response = input(f"SillyBot: What do you want to know about Monty Python? I can talk about Monty Python members, "
                     f"their shows, movies, sketches, records, tv series, books and more \n"
                     f"\n{curr_user['name']}: ")
    print()
    # Parse the user response to get the query
    query = parse_text.get_query(response)

    # Get the relevant topic from the query
    response_tuple = monty_python_data.get_data(query, curr_user)

    # Ask the user whether they like the topic discussed
    response = input(f"SillyBot: Do you like {str(response_tuple[2])} ?\n"
                     f"\n{curr_user['name']}: ")
    print()
    # Get the label based on the sentiment of the user response
    response_score = parse_text.parse_sentiment(response)

    if response_score > 0:
        print(f"SillyBot: I love {str(response_tuple[2])} as well\n")
        curr_user = users.add_extracted_information("likes", user=curr_user, info=str(response_tuple[2]))
        # Ask user for what else do they like
        curr_user = users.add_information(label="likes", user=curr_user)
    elif response_score < 0:
        print(f"SillyBot: Its disappointing that you dislike {str(response_tuple[2])}."
              f" I can't hate anything Monty Python\n")
        curr_user = users.add_extracted_information("dislikes", user=curr_user, info=str(response_tuple[2]))
        # Ask user for what else do they dislike
        curr_user = users.add_information(label="dislikes", user=curr_user)
    else:
        # Ask the user about their personal information
        print(f"SillyBot: Hmm, I think you are not really into {str(response_tuple[2])}")
        curr_user = users.add_information(label="personal_information", user=curr_user)

    # Update the user data
    users.update_user_data(curr_user, "users.json")


def initial_response():
    """
    Method for asking the user whether they like Monty Python to provide initial set of responses from the template
    :return: The user returned by the get_user() method
    """
    curr_user = get_user()

    # if the current user already likes Monty Python
    try:
        curr_user["likes"].index("Monty Python")
        print("SillyBot: I see that you like Monty Python\n")
        print("SillyBot:\n" + bot_responses["Like Python"][random.randint(0, len(bot_responses["Like Python"]) - 1)])

    except ValueError:
        # if the current user hates Monty Python
        try:
            curr_user["dislikes"].index("Monty Python")
            print("SillyBot: I see that you hate Monty Python\n")
            print("SillyBot:\n" +
                  bot_responses["Hate Python"][random.randint(0, len(bot_responses["Hate Python"]) - 1)])

        # If the user has not showcased any strong opinions towards Monty Python, we ask the user about
        # their opinions on Monty Python and update the user database
        except ValueError:
            response = input(f"SillyBot: Hi {curr_user['name']}, Do you like Monty Python?\n\n{curr_user['name']}: ")
            print()
            response_score = parse_text.parse_sentiment(response)
            if response_score > 0:
                print("SillyBot:\n"
                      + bot_responses["Like Python"][random.randint(0, len(bot_responses["Like Python"]) - 1)])
                curr_user["likes"].append("Monty Python")
            elif response_score == 0:
                print("SillyBot: You should learn more about Monty Python")
            else:
                print("SillyBot:\n"
                      + bot_responses["Hate Python"][random.randint(0, len(bot_responses["Hate Python"]) - 1)])
                curr_user["dislikes"].append("Monty Python")

    finally:
        # Return the current user
        return curr_user


def extract_more_user_information(curr_user):
    """
    Method for extracting more information about the current user
    :param curr_user: The current user talking with the chatbot
    :return: The information as well as the label extracted
    """

    # Prompt the user for more information
    bot_response = bot_responses["MoreInformation"][
        random.randint(0, len(bot_responses["MoreInformation"]) - 1)]
    print("SillyBot:\n" + bot_response)

    # If the bot asked for user likes, we provide information what they already like and ask for more
    if "like" in bot_response:
        label = "likes"
        if len(curr_user["likes"]) > 0:
            if len(curr_user["likes"]) > 1:
                info = input(f"SillyBot: I know that you like "
                             f"{curr_user['likes'][random.randint(0, len(curr_user['likes']) - 1)]}"
                             f", but I want to know more\n\n{curr_user['name']}: ")
            else:
                info = input(f"SillyBot: I know that you like "
                             f"{curr_user['likes'][0]}"
                             f", but I want to know more\n\n{curr_user['name']}: ")
        else:
            info = input(f"SillyBot: Nudge Nudge! Tell me what you like!\n\n{curr_user['name']}: ")
        print()
    # If the bot asked for user dislikes, we provide information what they already dislike and ask for more
    elif "hate" in bot_response:
        label = "dislikes"
        if len(curr_user["dislikes"]) > 0:
            if len(curr_user["dislikes"]) > 1:
                info = input(f"SillyBot: I know that you hate "
                             f"{curr_user['dislikes'][random.randint(0, len(curr_user['dislikes']) - 1)]}"
                             f", but I want to know more\n\n{curr_user['name']}: ")
            else:
                info = input(f"SillyBot: I know that you hate "
                             f"{curr_user['dislikes'][0]}"
                             f", but I want to know more\n\n{curr_user['name']}: ")
        else:
            info = input(f"SillyBot: Nudge Nudge! Tell me what you hate!\n\n{curr_user['name']}: ")
        print()
    # Else, if the bot prompts for more personal information, we ask the user to tell them about themselves
    else:
        label = "personal_information"
        if len(curr_user["personal_information"]) > 0:
            temp = random.randint(0, len(curr_user['personal_information']) - 1)
            info = input(f"SillyBot: I know that you are {curr_user['personal_information'][temp]}"
                         f", but I want to know more\n\n{curr_user['name']}: ")
        else:
            info = input(f"SillyBot: Nudge Nudge! Tell me more about yourself!\n\n{curr_user['name']}: ")
        print()
    # We return the information as well as the information label returned by the user
    return info, label


# The main function for the program
def main():
    try:
        # Get the current user
        curr_user = initial_response()
        response = " "
        flag = False

        while response:
            # Randomly ask the user for more information
            if random.random() > 0.3 and flag:
                info, label = extract_more_user_information(curr_user)
                curr_user = users.add_information_unlabelled(curr_user, nltk.sent_tokenize(info))

            # Converse with the user about Monty Python
            monty_python_converse(curr_user)
            flag = True

            # Ask the user whether they want to continue
            response = input(f"SillYBot: Do you want to continue?\n"
                             f"Press any key followed by enter to continue or press enter to exit!\n"
                             f"\n{curr_user['name']}: ")
            print()
        print("SillyBot:\n"+ bot_responses["Exit"][random.randint(0, len(bot_responses["Exit"]) - 1)])
    except:
        # In case of fatal error, we exit
        print("SillyBot:\n" + bot_responses["Error"][random.randint(0, len(bot_responses["Error"]) - 1)])


if __name__ == "__main__":
    main()
