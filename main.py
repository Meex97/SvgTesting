import requests
import json

from metamorph_utils import *


def multiple_question(question):
    print("\nTest case: " + question + "\n____________________")
    metamorphed_qs = []

    file_path = "res/corpus.txt"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                question = line.strip()



    except FileNotFoundError:
        print(f"file '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")

def main():
    print("Start SVG-AIML testing\n")
    file_path = "res/corpus.txt"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                question = line.strip()
                #print(f" {i}: {question}")
                #get_dialogue_answer(question)

                metamorphed_qs = get_metamorphed_questions(question, 8)



    except FileNotFoundError:
        print(f"file '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")



def get_dialogue_answer(quesiton):
    url = "http://localhost:3000/esempio3.html"

    payload = {
        "query": quesiton
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    print("Answer JSON:", response.json())


if __name__ == "__main__":
    main()