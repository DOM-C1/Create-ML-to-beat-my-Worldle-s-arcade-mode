import requests
import random
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.application import get_app
list_of_word_scores = []
# async module to make a timer work in parallel with input.


async def timer():
    global duration
    while duration > 0:
        await asyncio.sleep(1)
        duration -= 1
        # refreshes the timer screen while duration >=0
        if get_app().is_running:
            get_app().invalidate()


def bottom_toolbar():
    return f"Time left: {round(duration)} seconds"


# fetches a word with it's frequency in the form of a tuple, (word,frequency)
def get_n_letter_words_w_freq(length_of_word):
    themes = ["nature", "city", "emotion", "colour", "food",
              "music", "travel", "technology", "art", "sports"]
    global list_of_word_scores
    list_of_word_scores = []
    n = length_of_word*"?"
    for theme in themes:
        url = f"https://api.datamuse.com/words?ml={theme}&sp={n}&md=f&max=100"
        response = requests.get(url)
        response = response.json()
        for items in response:
            for i, item in enumerate(items.values()):

                if i == 0 and " " not in item and "-" not in item:
                    word = item
                elif i == 2:
                    for obj in item:
                        if "f:" in obj:
                            obj = obj.split(":")
                            list_of_word_scores.append((word, float(obj[1])))
    return list_of_word_scores


# filters words from above function, using word frequency as a proxy for difficulty (more frequent => easier word)
def set_difficulty(min_range, max_range):
    list_of_words = []
    for tuple in list_of_word_scores:
        if min_range <= tuple[1] <= max_range:
            list_of_words.append(tuple[0])
    return list_of_words


def is_valid_word(word):
    response = requests.get(f"https://api.datamuse.com/words?sp={word}")
    response = response.json()
    for dict in response:
        if word in dict.values():
            return True

    return False


def new_screen():
    print("\033[2J")


def list2string(guess_list):
    guess_string = ""
    for letter in guess_list:
        guess_string += letter
    return guess_string


def print_list_of_guesses(list_of_guesses):
    if list_of_guesses == []:
        return
    for i in range(len(list_of_guesses)):
        print(list2string(list_of_guesses[i]))
        print()


min_range = 100
max_range = 750
# works with the arcade game mode to dynamically adjust the difficulty based on performance


def difficulty_decider(avg_num_guesses, time_left):
    global min_range
    global max_range
    global duration
    global length_of_word
    if avg_num_guesses < 6:

        min_range *= 1.2
        max_range *= 0.8

        if time_left < 10:
            duration = 100 - 2*duration

        elif time_left >= 10:
            duration = 90 - duration
            if length_of_word < 7 and time_left > 15:
                length_of_word += 1

    if avg_num_guesses >= 6:
        min_range *= 0.8
        max_range *= 1.2

        if time_left < 10:
            duration = 100 - 2*duration
            if time_left < 7 and length_of_word > 3:
                length_of_word -= 1

        elif time_left >= 10:
            duration = 100 - duration


# Using ANSI characters to  display various colours needed for the game.
yellow_text = "\033[33m"
black_text = "\033[0m"
green_text = "\033[32m"
red_text = "\033[91m"


def classic_game_loop(list_of_words):
    random_word = random.choice(list_of_words)
    guess_list = ["_ "] * 5
    word_list = list(random_word)
    list_of_guesses = []

    for guesses in range(7):

        guess = input("Player guess a word: ")
        guess = guess.lower()
        guess = guess.replace(" ", "")

        while len(guess) != 5 or is_valid_word(guess) == False:

            new_screen()
            print_list_of_guesses(list_of_guesses)
            print(f"Invalid input, please enter a valid 5 letter word")
            guess = input("Player guess a word: ").lower()

        for i, letter in enumerate(guess):
            if letter == word_list[i]:
                guess_list[i] = green_text + letter + black_text
            elif letter in word_list:
                guess_list[i] = yellow_text + letter + black_text
            else:
                guess_list[i] = letter
        list_of_guesses.append(guess_list.copy())
        new_screen()
        print_list_of_guesses(list_of_guesses)

        if guess == random_word:
            print("Congratulations! You guessed the word!")
            break

    else:
        print(f"Sorry, you didn't guess the word. It was {random_word}")
    input("\n press enter to continue")
    new_screen()


async def arcade_game_loop(list_of_words, num_of_guesses):
    timer_task = asyncio.create_task(timer())
    random_word = random.choice(list_of_words)
    word_length = len(random_word)
    guess_list = ["_ "] * word_length
    word_list = list(random_word)
    global list_of_guesses
    global flag
    list_of_guesses = []
    print(
        f"You have {num_of_guesses} guesses and {int(duration)} seconds to guess a word of length {word_length}")
    input("Press enter to continue:")
    new_screen()
    session = PromptSession(bottom_toolbar=bottom_toolbar)

    for guesses in range(num_of_guesses):
        if duration <= 0:
            print(
                f"Oops, you ran out of time, the correct word was {random_word}")
            input("Press enter to continue to the main-menu")
            flag = False
            return

        guess = await session.prompt_async("Player guess a word: ")
        guess = guess.lower()
        guess = guess.replace(" ", "")

        while len(guess) != len(random_word) or is_valid_word(guess) == False:
            new_screen()
            print_list_of_guesses(list_of_guesses)
            print(
                f"Invalid input, please enter a valid {word_length} letter word")
            guess = await session.prompt_async("Player guess a word: ")
            guess = guess.lower()

        for i, letter in enumerate(guess):
            if letter == word_list[i]:
                guess_list[i] = green_text + letter + black_text
            elif letter in word_list:
                guess_list[i] = yellow_text + letter + black_text
            else:
                guess_list[i] = letter
        list_of_guesses.append(guess_list.copy())
        new_screen()
        print_list_of_guesses(list_of_guesses)

        if guess == random_word:
            print("Congratulations! You guessed the word!")
            input("Press enter to continue to the next round")
            new_screen()
            timer_task.cancel()
            break

    if guess != random_word:

        print(f"Sorry, you didn't guess the word. It was {random_word}")
        input("Press enter to continue to main-menu")
        new_screen()
        flag = False
        return


choice = ""
while choice != "quit":
    new_screen()
    print(f"Welcome to {red_text}A{black_text}poca{red_text}L{black_text}ex!")
    print()
    print()
    print()
    print("Which mode would you like to play?")
    print()
    print()
    print("1. Arcade mode")
    print()
    print()
    print("2. Classic mode")
    print()
    print()
    choice = input("Enter your choice (1,2 or 'quit'): ")
    if choice == "1":
        duration = 2.5
        avg_num_guesses = 0
        attempts = 0
        num_of_guesses = 10
        length_of_word = 5
        list_of_guesses = []
        flag = True
        new_screen()
        print("Welcome to Arcade Mode! Here, the challenge escalates if you do well, words will get trickier,there will be less time, and word length may vary. \n  Stay sharp, keep an eye on the time, and bring your A-game. Lets see how you fare as the stakes get higher!")
        print("\n")
        input("Are you ready? press enter to continue")
        new_screen()

        while duration > 0 and flag == True:
            avg_num_guesses = (len(list_of_guesses) + avg_num_guesses) / \
                attempts if attempts != 0 else avg_num_guesses

            difficulty_decider(avg_num_guesses, duration)
            get_n_letter_words_w_freq(length_of_word)
            word_set = set_difficulty(min_range, max_range)
            asyncio.run(arcade_game_loop(word_set, num_of_guesses))
            attempts += 1

    if choice == "2":
        list_of_word_scores = get_n_letter_words_w_freq(5)
        while True:
            new_screen()
            print("Classic mode selected, 5 guesses to find a 5 letter word")
            print()
            print("You decide the difficulty!")
            print()
            print("1. Easy")
            print()
            print("2. Medium")
            print()
            print("3. Hard")
            print()
            print("'quit' to enter main-menu")
            print()
            difficulty_select = input(
                "Enter your choice (1, 2, 3, or 'quit'): ")
            if difficulty_select == "quit":
                break
            while difficulty_select != "1" and difficulty_select != "2" and difficulty_select != "3":
                print("Invalid choice")
                difficulty_select = input("Enter your choice (1, 2, or 3): ")
            if difficulty_select == "1":
                new_screen()
                word_set = set_difficulty(20, 100000)
                print("Easy mode selected")
                print()
                print()
                classic_game_loop(word_set)
            elif difficulty_select == "2":
                new_screen()
                word_set = set_difficulty(10, 20)
                print("Medium difficulty selected")
                print()
                print()
                classic_game_loop(word_set)
            elif difficulty_select == "3":
                new_screen()
                word_set = set_difficulty(0, 5)
                print("Hard mode selected")
                print()
                print()
                classic_game_loop(word_set)
