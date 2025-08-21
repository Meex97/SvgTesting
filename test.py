from operator import truediv

import requests
import json


def get_dialogue_answer(quesiton, n = 3):
    url = f"http://localhost:3000/esempio{n}.html"

    payload = {
        "query": quesiton
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    #print("Answer JSON:", response.json())

    return response.json()["answer"], (response.json()["image_link"], response.json()["id_elements"], response.json()["style_names"])


def compare_answers(test_case_answer, follow_up_answers, expect):
    test_results = []

    for follow_up in follow_up_answers:
        text_test = test_case_answer[0] == follow_up[0]
        multimodal_test = (test_case_answer[1][0] == follow_up[1][0]) and (test_case_answer[1][1] == follow_up[1][1]) and (test_case_answer[1][2] == follow_up[1][2])
        if expect == "same":
            test_results.append((text_test, multimodal_test))
        else:
            test_results.append((not text_test, not multimodal_test))
        print("{:<8} {:<8} {:<80}".format(text_test, multimodal_test, " / " if test_case_answer[0] == follow_up[0] else follow_up[0]))

    return test_results


def compare_multiple(test_case1, test_case2, follow_up):
    text_test1 = test_case1[0] == follow_up[0]
    multimodal_test1 = (test_case1[1][0] == follow_up[1][0]) and (test_case1[1][1] == follow_up[1][1]) and (test_case1[1][2] == follow_up[1][2])

    text_test2 = test_case2[0] == follow_up[0]
    multimodal_test2 = (test_case2[1][0] == follow_up[1][0]) and (test_case2[1][1] == follow_up[1][1]) and (test_case2[1][2] == follow_up[1][2])

    text_test_conc = test_case1[0] + " " + test_case2[0] == follow_up[0]
    multimodal_test_conc = (test_case1[0] + " " + test_case2[1][0] == follow_up[1][0]) and (test_case1[0] + " " + test_case2[1][1] == follow_up[1][1]) and (test_case1[0] + " " +
                test_case2[1][2] == follow_up[1][2])

    print("{:<8} {:<8} {:<8} {:<8} {:<8} {:<8}".format(text_test1, multimodal_test1, text_test2, multimodal_test2, text_test_conc, multimodal_test_conc))


def test_same(question, metamorphed_questions, n = 3):
    print(question)
    if not (any(metamorphed_questions) and any(any(sub) if isinstance(sub, list) else True for sub in metamorphed_questions)):
        return

    test_case_answer = get_dialogue_answer(question, n)
    print("test case answer: ", test_case_answer[0])
    print(f"Metamorphed questions: {metamorphed_questions}")

    print("{:<8} {:<8} {:<80}".format("text", "multi", "answer"))
    print("-" * 30)

    follow_up_answers = []
    for meta in metamorphed_questions:
        follow_up_answers.append(get_dialogue_answer(meta, n))

    res = compare_answers(test_case_answer, follow_up_answers, expect = "same")

    #print("testcase: " + question + "\n")
    #print(metamorphed_questions)
    #print(res)