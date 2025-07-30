from operator import truediv

import requests
import json


def get_dialogue_answer(quesiton):
    url = "http://localhost:3000/esempio3.html"

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
        print("{:<8} {:<8}".format(text_test, multimodal_test))

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


def test_same(question, metamorphed_questions):
    if not metamorphed_questions:
        return

    print("{:<8} {:<8}".format("text", "multi"))
    print("-" * 30)
    test_case_answer = get_dialogue_answer(question)

    follow_up_answers = []
    for meta in metamorphed_questions:
        follow_up_answers.append(get_dialogue_answer(meta))

    res = compare_answers(test_case_answer, follow_up_answers, expect = "same")

    #print("testcase: " + question + "\n")
    #print(metamorphed_questions)
    #print(res)