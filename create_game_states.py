import random
import json
import csv


def random_sample_from_list(input_list, range_start, range_end):
    m = random.randint(range_start, range_end)
    m = min(m, len(input_list))
    random_items = random.sample(input_list, m)

    return random_items


def generate_game_states(word, alphabet='abcdefghijklmnopqrstuvwxyz'):
    all_game_states = []
    iterations = 500
    for _ in range(iterations):
        max_reveals = len(word)
        game_states = []

        for num_reveals in range(1, max_reveals + 1):
            revealed_letters = sorted(random.sample(
                range(len(word)), k=num_reveals))
            correct_state = [(index, word[index])
                             for index in revealed_letters]

            incorrect_states = []
            for index in range(len(word)):
                if index not in revealed_letters:
                    possible_incorrect_letters = [word[i] for i in range(
                        len(word)) if i != index and word[i] not in [l for _, l in correct_state]]
                    if possible_incorrect_letters:
                        chosen_letter = random.choice(
                            possible_incorrect_letters)
                        incorrect_states.append((index, chosen_letter))

            sample_of_incorrect_states = random.sample(incorrect_states, random.randint(
                1, len(incorrect_states))) if incorrect_states else []

            letters_not_in_word = [
                letter for letter in alphabet if letter not in word]
            num_incorrect_letters = random.randint(1, 10)
            incorrect_letters = random.sample(
                letters_not_in_word, num_incorrect_letters)

            game_states.append({
                'correct_state': correct_state,
                'incorrect_state': sample_of_incorrect_states,
                'incorrect_letters': incorrect_letters,
                'word': word
            })

        all_game_states.extend(game_states)

    return all_game_states


def simulate_game():
    game_states = []
    with open('list_of_words.json', 'r') as file:
        list_of_words = json.load(file)
    for dictionary in list_of_words:
        words_of_length = dictionary['words']
        for words in words_of_length:
            game_states.append(generate_game_states(words))
    with open('game_states', 'w') as file:
        json.dump(game_states, file, indent=1)


simulate_game()
