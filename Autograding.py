import json
import pathlib
from typing import Dict, List


def identify_cell(sentence: str, cells: List[Dict], cell_type: str = 'code') -> int:
    for i, _cell in enumerate(cells):
        if _cell['cell_type'] == cell_type and _cell['source'][0] == sentence:
            return i
    return -1


def load_model_ans(path: pathlib.Path) -> Dict[int, List[str]]:
    with open(path, "r") as f:
        nb = json.load(f)
        cells = nb["cells"]

    model_ans = {}
    for i in range(1, 100):  # 100 は適当な上限です
        cn = identify_cell(sentence=f"#問題{i}\n", cells=cells)
        if cn != -1:
            ans_cell = cells[cn]
            if ans_cell['outputs'][0]:
                output = ans_cell['outputs'][0]
                if 'text/plain' in output.get('data', {}):
                    model_ans[i] = output['data']['text/plain']
                elif 'text' in output:
                    model_ans[i] = output['text']
                else:
                    model_ans[i] = None
        else:
            break

    return model_ans


def grade_student(ans_path: pathlib.Path, model_ans: Dict[int, List[str]]) -> int:
    with open(ans_path, "r") as f:
        nb = json.load(f)
        cells = nb["cells"]

    score = 0
    for question_num, model_ans_texts in model_ans.items():
        cn = identify_cell(sentence=f"#問題{question_num}\n", cells=cells)
        if cn != -1:
            ans_cell = cells[cn]
            if ans_cell['outputs'] and ans_cell['outputs'][0]:
                output = ans_cell['outputs'][0]
                student_ans_text = None
                if 'text/plain' in output.get('data', {}):
                    student_ans_text = output['data']['text/plain']
                elif 'text' in output:
                    student_ans_text = output['text']

                if student_ans_text == model_ans_texts:
                    score += 1

    return score


def main():
    answer_path = pathlib.Path("answer/model_ans_1.ipynb")
    submitted_path = pathlib.Path("submitted")

    model_ans = load_model_ans(answer_path)

    for student_path in submitted_path.glob("*.ipynb"):
        score = grade_student(student_path, model_ans)
        print(f"{student_path.name} のスコア: {score}")


if __name__ == "__main__":
    main()
