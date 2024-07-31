import json
import random
import argparse
from pydantic import BaseModel, ValidationError, validator
from typing import List


class Question(BaseModel):
    question: str
    options: List[str]
    answer: str

    @validator('options')
    def validate_options(cls, v, values, **kwargs):
        if len(v) < 2:
            raise ValueError("Must provide at least two options for a question.")
        if 'answer' in values and values['answer'] not in v:
            raise ValueError("The answer must be one of the options.")
        return v


class Player:
    def __init__(self, name: str):
        self.name = name
        self.score = 0

    def increase_score(self):
        self.score += 1


class TriviaGame:
    def __init__(self, questions: List[Question], players: List[Player]):
        self.questions = questions
        self.players = players
        self.current_question_index = 0

    def shuffle_questions(self):
        random.shuffle(self.questions)

    def shuffle_options(self, question: Question):
        random.shuffle(question.options)

    def get_next_question(self) -> Question:
        if self.current_question_index >= len(self.questions):
            return None
        question = self.questions[self.current_question_index]
        return question

    def play(self):
        self.shuffle_questions()
        current_player_index = 0
        while self.current_question_index < len(self.questions):
            current_player = self.players[current_player_index]
            question = self.get_next_question()

            if question is None:
                break

            self.shuffle_options(question)
            print(f"\n{current_player.name}, it's your turn to answer:")
            print(question.question)
            for i, option in enumerate(question.options, start=1):
                print(f"{i}. {option}")

            try:
                answer_index = int(input("Enter the number of your answer: ")) - 1
            except ValueError:
                print("Invalid input, please try again.")
                continue

            if answer_index < 0 or answer_index >= len(question.options):
                print("Invalid input, please try again.")
                continue

            selected_answer = question.options[answer_index]

            if selected_answer == question.answer:
                print("Correct! You earned a point.")
                current_player.increase_score()
                current_player_index = (current_player_index + 1) % len(self.players)
                self.current_question_index += 1  # Update the question index only on correct answer
            else:
                print("Incorrect!")
                current_player_index = (current_player_index + 1) % len(self.players)

        print("\nThe game is over! Here are the results:")
        for player in self.players:
            print(f"{player.name}: {player.score} points")

        winner = max(self.players, key=lambda p: p.score)
        print(f"\nThe winner is: {winner.name} with {winner.score} points!")


def load_questions_from_file(file_path: str) -> List[Question]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            questions = []
            for q in data:
                try:
                    question = Question(**q)
                    questions.append(question)
                except ValidationError as e:
                    print(f"Problem with question: {q.get('question', 'Unknown')}. {e}")
            return questions
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not valid (not a valid JSON).")
        return []


def main():
    parser = argparse.ArgumentParser(description="Trivia game for two players.")
    parser.add_argument('file_path', type=str, help="Path to the JSON file with questions.")
    parser.add_argument('num_players', type=int, help="Number of players.")

    args = parser.parse_args()

    questions = load_questions_from_file(args.file_path)
    if not questions:
        print("No valid questions found in the file.")
        return

    players = [Player(name=f"Player {i + 1}") for i in range(args.num_players)]

    game = TriviaGame(questions, players)
    game.play()


if __name__ == "__main__":
    main()

# Run the game in terminal - python trivia_game.py questions.json 2
