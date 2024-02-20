import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
import numpy as np
import json


def load_and_parse_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        game_states = json.load(jsonfile)
    return game_states


def encode_game_state(game_state_dict, word_length=5, alphabet='abcdefghijklmnopqrstuvwxyz'):
    correct_positions = np.zeros((word_length, len(alphabet)), dtype=int)
    misplaced_positions = np.zeros((word_length, len(alphabet)), dtype=int)
    incorrect_letters_vector = np.zeros(len(alphabet), dtype=int)
    for pos, letter in game_state_dict.get('correct_state', []):
        correct_positions[pos][alphabet.index(letter)] = 1
    for pos, letter in game_state_dict.get('incorrect_state', []):
        misplaced_positions[pos][alphabet.index(letter)] = 1
    for letter in game_state_dict.get('incorrect_letters', []):
        incorrect_letters_vector[alphabet.index(letter)] = 1

    input_vector = np.concatenate([
        correct_positions.flatten(),
        misplaced_positions.flatten(),
        incorrect_letters_vector
    ])
    return input_vector


def encode_target_word(word, alphabet='abcdefghijklmnopqrstuvwxyz'):
    target_vector = np.zeros((len(word), len(alphabet)), dtype=int)
    for i, letter in enumerate(word):
        target_vector[i][alphabet.index(letter)] = 1
    return target_vector.flatten()


def create_3d_dataset(data, word_length=5, alphabet_size=26, max_states_per_word=500):
    all_encoded_states = []
    for word_data in data:
        word_encoded_states = []
        for game_state_dict in word_data[:max_states_per_word]:
            encoded_state = encode_game_state(
                game_state_dict, word_length=word_length, alphabet='abcdefghijklmnopqrstuvwxyz')
            word_encoded_states.append(encoded_state)
        num_missing_states = max_states_per_word - len(word_encoded_states)
        if num_missing_states > 0:
            padding = np.zeros(
                (num_missing_states, word_length * alphabet_size * 2 + alphabet_size))
            word_encoded_states.extend(padding)
        all_encoded_states.append(word_encoded_states)
    dataset_3d = np.array(all_encoded_states)
    return dataset_3d


words = load_and_parse_json('five_letter_words')
dataset_3d = create_3d_dataset(words)
Y = []

Y = [encode_target_word(
    word[0]['word'], alphabet='abcdefghijklmnopqrstuvwxyz') for word in words]
X = torch.tensor(dataset_3d, dtype=torch.float32)
Y = torch.tensor(Y, dtype=torch.float32)
X_train, X_test, Y_train, Y_test = train_test_split(
    X.numpy(), Y.numpy(), test_size=0.14, random_state=42)
train_dataset = TensorDataset(torch.tensor(X_train), torch.tensor(Y_train))
test_dataset = TensorDataset(torch.tensor(X_test), torch.tensor(Y_test))
train_loader = DataLoader(train_dataset, batch_size=50, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=150, shuffle=False)


class FeedforwardModel(nn.Module):
    def __init__(self):
        super(FeedforwardModel, self).__init__()
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(143000, 256)
        self.dropout1 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(256, 128)
        self.dropout2 = nn.Dropout(0.5)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 130)

    def forward(self, x):
        x = self.flatten(x)
        x = torch.relu(self.fc1(x))
        x = self.dropout1(x)
        x = torch.relu(self.fc2(x))
        x = self.dropout2(x)
        x = torch.relu(self.fc3(x))
        x = torch.sigmoid(self.fc4(x))
        return x


model = FeedforwardModel()
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

model.train()
for epoch in range(32):
    for inputs, targets in train_loader:
        inputs, targets = inputs.to(device), targets.to(
            device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
    print(f'Epoch {epoch+1}, Loss: {loss.item()}')

model.eval()
torch.save(model.state_dict(), 'wordle_solver.pth')

total = 0
correct = 0
with torch.no_grad():
    for inputs, targets in test_loader:
        inputs, targets = inputs.to(device), targets.to(device)
        outputs = model(inputs)
        predicted = outputs.round()
        total += targets.size(0)

        correct += (predicted == targets).sum().item()
print(f"Test Accuracy: {correct / total*100}, Test Loss: {loss.item()}")
