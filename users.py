# Name: Ranveer Singh
# Class and Section: CS 4385.001
# Net ID: rxs174730
# Python Chatbot

# This is the file which provides methods for dealing with users
import json
import parse_text
import nltk


def update_user_data(user, data_path):
    """
    Method for updating the user data
    :param user: The user name
    :param data_path: The file path containing the save directory
    :return: None
    """

    # Loads the dictionary of users
    users = json.load(open(data_path, "r"))
    users[user["name"]] = user
    json.dump(users, open(data_path, "w"), indent=5)


def user_already_exists(name, users_data):
    """
    Method to detect if the user with the given name already exists. The name has to be an exact match
    :param name: The user name
    :param users_data: The user dictionary with the user name as the key
    :return: True, if the user already exists. False otherwise
    """
    return name in users_data.keys()


def create_user(name, data_path: str, override=False) -> (dict, int):
    """
    Creates a user for the chatbot
    :param name: The name of the user
    :param data_path: File path containing all the user data
    :param override: Flag whcih decides whether to override user data. If true and user has a name that already exists,
    that user is deleted from the system
    :return: The name of the user as well as return code
    """
    user = dict()
    # Creating a user dictionary
    user[name] = {"name": name, "personal_information": [], "likes": [], "dislikes": []}

    # If the user name is root (The data is initialized for the first time)
    if name == "root":
        json.dump(user, open(data_path, "w"), indent=5)

    # If the data file already exists
    else:
        # Get the list of users
        users = json.load(open(data_path, "r"))

        # If the user already exits and override is False
        if user_already_exists(name, users) and not override:

            # We ask whether the user is the same one as mentioned before
            response = input("SillyBot: The user with the same name already exists! If you are that person, press Y\n"
                             "\nUser: ")
            print()
            if response in ["Y", "y"]:
                # Return the user data from the dataset
                return users[name], 0

            # If the user is different from one mentioned in the dataset, we return the error code
            return None, -1

        # If the user is new
        else:
            # Create the user dictionary, update the users dataset and return the current user
            # as well as the error code
            users[name] = {"name": name, "personal_information": [], "likes": [], "dislikes": []}
            json.dump(users, open(data_path, "w"), indent=5)
            return users[name], 0


def add_information(label: str, user):
    """
    Method for adding new information about the user
    :param label: The kind of information we are updating
    :param user: The user whose information we need to update
    :return: The updated user
    """
    bot_response = {"likes": "SillyBot: What else do you like\n",
                    "dislikes": "SillyBot: What else do you dislike\n",
                    "personal_information": "SillyBot: Screw that. Why don't you tell me more about yourself!\n"
                    }

    # We form individual sentences of the user token and parse them one by one
    response_list = nltk.sent_tokenize(input(bot_response[label] + f"\n{user['name']}: "))
    print()
    # We parse each sentence individually, and add the information extracted to the user
    for response in response_list:
        response = parse_text.get_information_from_text(response)
        user[label].append(response)
        user[label] = list(set(user[label]))

    # We return the updated user data
    return user


def add_extracted_information(label: str, user, info):
    """
    We add the extracted information about the user
    :param label: The label of the information added
    :param user: The user whose information is being updated
    :param info: The information to be updated
    :return: The updated user
    """
    user[label].append(info)
    user[label] = list(set(user[label]))
    return user


def add_information_unlabelled(user, info_list):
    """
    Add the extracted list of information about the user.
    Unlike the other options, we don't need to supply the label as the label is detected based on sentiment
    :param user: The user whose information needs to be updated
    :param info_list: The information that we need to add
    :return: The updated user
    """

    # For each information statement
    for info in info_list:
        # We get the sentiment score of the information sentence
        sent_score = parse_text.parse_sentiment(info)
        # We parse the sentence to extract the information
        info = parse_text.get_information_from_text(info)
        # We add the information to the appropriate list based on the label
        if sent_score > 0:
            user["likes"].append(info)
        elif sent_score < 0:
            user["dislikes"].append(info)
        else:
            user["personal_information"].append(info)

    # Return the updated user
    return user
