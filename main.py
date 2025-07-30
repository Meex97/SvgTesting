from metamorph_utils import *
from test import *


def multiple_question(question, index):
    print("\nTest case: " + question + "\n____________________")
    metamorphed_qs = []
    file_path = "res/corpus.txt"

    tmp_q = question
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                question2 = line.strip()
                if i != index and random.random() < 0.2:
                    tmp_q += " " + question2
                    print("Follow-up: " + tmp_q)
                    metamorphed_qs.append((question2, tmp_q))
                    tmp_q = question


    except FileNotFoundError:
        print(f"file '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")

    return metamorphed_qs


def test_multiple_questions(question, i):
    metamorphed_qs = multiple_question(question, i)

    test_case1 = get_dialogue_answer(question)
    print("{:<8} {:<8} {:<8} {:<8} {:<8} {:<8}".format("text1", "multi1", "text2", "multi2","text_cnc", "multi_cnc"))
    print("-" * 70)

    for q2, m in metamorphed_qs:
        #print(question + "____" + q2)
        test_case2 = get_dialogue_answer(q2)
        follow_up = get_dialogue_answer(m)
        compare_multiple(test_case1, test_case2, follow_up)


def main():
    print("Start SVG-AIML testing\n")
    file_path = "res/corpus.txt"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                question = line.strip()
                #print(f" {i}: {question}")
                #get_dialogue_answer(question)

                # 1: filler words
                #test_same(question, get_metamorphed_questions(question, 1))
                # 7: synonyms
                test_same(question, get_metamorphed_questions(question, 7))
                # 8: mistakes
                #test_same(question, get_metamorphed_questions(question, 8))

                # 10: multiple questions
                #test_multiple_questions(question, i)



    except FileNotFoundError:
        print(f"file '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")



if __name__ == "__main__":
    main()