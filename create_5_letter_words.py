import json


def load_and_parse_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        game_states = json.load(jsonfile)
    return game_states


words = load_and_parse_json('game_states')
five = []
for list in words:
    if len(list[0]['word']) == 5:
        five.append(list)

with open('five_letter_words', 'w', encoding='utf-8') as jsonfile:
    json.dump(five, jsonfile, indent=1)
