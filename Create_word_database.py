import json
import requests


def set_difficulty(min_range, max_range):
    list_of_words = []
    for tuple in list_of_word_scores:
        if min_range <= tuple[1] <= max_range:
            list_of_words.append(tuple[0])

    return list_of_words


def get_n_letter_words_w_freq(length_of_word):
    themes = [
        "nature",
        "city",
        "emotion",
        "colour",
        "food",
        "music",
        "travel",
        "technology",
        "art",
        "sports",
        "animals",
        "history",
        "science",
        "literature",
        "fashion",
        "vehicles",
        "space",
        "mythology",
        "geography",
        "architecture",
        "movies",
        "hobbies",
        "health",
        "politics",
        "economics"
    ]
    list_of_words = []
    n = length_of_word*"?"
    for theme in themes:
        url = f"https://api.datamuse.com/words?ml={theme}&sp={n}&md=f&max=50"
        response = requests.get(url)
        response = response.json()
        for items in response:
            for i, item in enumerate(items.values()):

                if i == 0 and all(char.isalpha() for char in item) and any(char in ['a', 'e', 'i', 'o', 'u'] for char in item):
                    word = item
                    list_of_words.append(word)
    return list_of_words


def process_write():
    max_word_length = 7
    min_word_length = 3
    list_of_words = []
    for number in range(min_word_length, max_word_length + 1):
        words = get_n_letter_words_w_freq(number)
        list_of_words.append({'word_length': number, 'words': words})
    with open('list_of_words.json', 'w') as file:
        json.dump(list_of_words, file, indent=4)


process_write()
