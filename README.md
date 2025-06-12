# Wordle Solver and Game

This repository contains a collection of scripts used to generate a database of Wordle game states, train a neural network to guess five letter words and play an interactive Wordle clone. The project was created as an experiment to beat the author's Worldle arcade mode.

## Features

- **Create_word_database.py** &ndash; Fetches themed words from the Datamuse API and writes them to `list_of_words.json`.
- **create_game_states.py** &ndash; Generates simulated game states for each word in the word list to create training data.
- **create_5_letter_words.py** &ndash; Filters the generated game states to only keep five letter words and saves them as `five_letter_words`.
- **create_ml.py** &ndash; Trains a feed‑forward PyTorch model on the game state data and saves the model weights to `wordle_solver.pth`.
- **test_model.py** &ndash; Demonstrates loading the trained model and predicts words for new puzzle states.
- **wordle_game.py** &ndash; Provides an interactive terminal game with both classic and arcade modes.

## Installation

1. Create a Python environment and install the required dependencies:

```bash
pip install -r requirements.txt
```

2. (Optional) Generate the word database and training data by running the scripts in the following order:

```bash
python Create_word_database.py
python create_game_states.py
python create_5_letter_words.py
```

3. Train the model:

```bash
python create_ml.py
```

The trained weights will be saved to `wordle_solver.pth`.

## Usage

To play the terminal game:

```bash
python wordle_game.py
```

To test the neural network on example puzzles:

```bash
python test_model.py
```

## Notes

- The dataset generation scripts require internet access to query the Datamuse API.
- Training the neural network may take some time depending on your hardware.

