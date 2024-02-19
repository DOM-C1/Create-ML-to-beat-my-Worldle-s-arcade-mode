import torch
import numpy as np
from itertools import product
from create_ml import FeedforwardModel, encode_game_state

model = FeedforwardModel()
model.load_state_dict(torch.load('wordle_solver.pth'))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()


def prepare_input(new_data):
    encoded_states = [encode_game_state(new_data, word_length=5, alphabet='abcdefghijklmnopqrstuvwxyz')
                      for _ in range(500)]

    input_vector = np.concatenate(encoded_states)[:130000]
    input_batch = np.expand_dims(input_vector, axis=0)

    input_batch = torch.tensor(input_batch, dtype=torch.float32).to(device)
    return input_batch


def predict_from_prepared_input(input_batch, model):
    with torch.no_grad():
        output_probabilities = model(
            input_batch).cpu().numpy()  #
    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    probabilities_reshaped = output_probabilities.reshape((5, 26))
    predicted_word = ''
    for position_probabilities in probabilities_reshaped:

        max_prob_index = np.argmax(position_probabilities)
        predicted_word += alphabet[max_prob_index]
    return predicted_word


light = prepare_input(
    {"correct_state": [[0, "l"]], "incorrect_state": [[2, "i"], [1, "g"]]})
grape = prepare_input(
    {"correct_state": [[2, "a"], [4, "e"]], "incorrect_state": [[0, "r"], [3, "g"]]})
chord = prepare_input(
    {"correct_state": [[0, "c"], [3, "r"]], "incorrect_state": [[4, "o"], [2, "d"]]})
flute = prepare_input(
    {"correct_state": [[1, "l"], [4, "e"]], "incorrect_state": [[3, "f"], [0, "u"]]})

crane_guess = prepare_input(
    {"correct_state": [[1, "r"], [4, "e"], [3, 'c']], "incorrect_state": []})
predictions = [
    predict_from_prepared_input(light, model),
    predict_from_prepared_input(grape, model),
    predict_from_prepared_input(chord, model),
    predict_from_prepared_input(flute, model),
    predict_from_prepared_input(crane_guess, model)
]


for pred in predictions:
    print(pred)
