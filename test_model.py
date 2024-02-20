import torch
import numpy as np
from itertools import product
from create_ml import FeedforwardModel, encode_game_state

model = FeedforwardModel()
model.load_state_dict(torch.load('wordle_solver.pth'))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()


def create_puzzle_dict():

    puzzle_dict = {
        "correct_state": [],
        "incorrect_state": [],
        "incorrect_letters": []
    }

    correct_guesses = input(
        "Enter correct guesses with positions (e.g., '0e,1a'): ")
    puzzle_dict["correct_state"] = [
        [int(guess[0]), guess[1]] for guess in correct_guesses.split(',') if guess]

    incorrect_guesses = input(
        "Enter incorrect guesses with positions (e.g., '2i,3g'): ")
    puzzle_dict["incorrect_state"] = [
        [int(guess[:-1]), guess[-1]] for guess in incorrect_guesses.split(',') if guess]

    incorrect_letters = input(
        "Enter incorrect letters without positions (e.g., 'x,y,z'): ")
    puzzle_dict["incorrect_letters"] = [letter.strip()
                                        for letter in incorrect_letters.split(',') if letter]

    return puzzle_dict


def prepare_input(new_data):
    encoded_states = [encode_game_state(new_data, word_length=5, alphabet='abcdefghijklmnopqrstuvwxyz')
                      for _ in range(500)]

    input_vector = np.concatenate(encoded_states)[:143000]
    input_batch = np.expand_dims(input_vector, axis=0)

    input_batch = torch.tensor(input_batch, dtype=torch.float32).to(device)
    return input_batch


def predict_from_prepared_input(input_batch, model):
    with torch.no_grad():
        output_probabilities = model(
            input_batch).cpu().numpy()
    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    probabilities_reshaped = output_probabilities.reshape((5, 26))
    predicted_word = ''
    for position_probabilities in probabilities_reshaped:

        max_prob_index = np.argmax(position_probabilities)
        predicted_word += alphabet[max_prob_index]
    return predicted_word


# Model thinks this is 'lighs'
light = prepare_input({
    "correct_state": [[0, "l"]],
    "incorrect_state": [[2, "i"], [1, "g"], [0, 'h']],
    "incorrect_letters": ['x', 'y', 'z', 'a']
})
# Model correctly guesses this is 'grape'
grape = prepare_input({
    "correct_state": [[2, "a"], [4, "e"]],
    "incorrect_state": [[0, "r"], [3, "g"]],
    "incorrect_letters": ['b', 'c', 'd', 's']
})
# Model correctly guesses this 'chord'
chord = prepare_input({
    "correct_state": [[0, "c"], [3, "r"]],
    "incorrect_state": [[4, "o"], [2, "d"], [0, 'h']],
    "incorrect_letters": ['m', 'n', 'p']
})
# Model thinks this 'flace'
flute = prepare_input({
    "correct_state": [[1, "l"], [4, "e"]],
    "incorrect_state": [[3, "f"], [0, "u"]],
    "incorrect_letters": ['q', 's', 'm']
})

predictions = [
    predict_from_prepared_input(light, model),
    predict_from_prepared_input(grape, model),
    predict_from_prepared_input(chord, model),
    predict_from_prepared_input(flute, model),

]


for pred in predictions:
    print(pred)
# Create own tests here
while True:
    print(predict_from_prepared_input(
        prepare_input(create_puzzle_dict()), model))
