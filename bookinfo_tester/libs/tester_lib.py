import requests
from termcolor import colored


def reviews_v1_testing(api_url):
    """
    Function for testing the v1 reviews
    """
    response = requests.request("GET", api_url).json()
    for review in response['reviews']:
        if "rating" in review:
            print(colored("This is not v1 reviews, fail!", "red"))
        if "rating" not in review:
            print(colored("This is v1 reviews, success!", "green"))


def reviews_v2_testing(api_url):
    """
    Function for testing the v2 reviews
    """
    response = requests.request("GET", api_url, auth=('jason', '')).json()
    for review in response['reviews']:
        try:
            color = review['rating']['color']
            if color == "black":
                print(colored("This is v2 reviews, success!", "green"))
            else:
                print(colored("This is not v2 reviews, fail!", "red"))
        except KeyError:
            print(colored("This is not v2 reviews, fail!", "red"))


def reviews_v3_testing(api_url):
    """
    Function for testing the v3 reviews
    """
    response = requests.request("GET", api_url).json()
    for review in response['reviews']:
        try:
            color = review['rating']['color']
            if color == "red":
                print(colored("This is v3 reviews, success!", "green"))
            else:
                print(colored("This is not v3 reviews, fail!", "red"))
        except KeyError:
            print(colored("This is not v3 reviews, fail!", "red"))
