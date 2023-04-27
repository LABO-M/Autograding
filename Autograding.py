import json
import pathlib
from typing import Dict, List
from utils import identify_cell
from student_notebook import StudentNotebook

def load_model_ans(path: pathlib.Path) -> Dict[int, List[str]]:
    with open(path, "r") as f:
        nb = json.load(f)
        cells = nb["cells"]

    model_ans = {}
    for i in range(1, 10):  # 10 は適当な上限です
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


def main():
    answer_path = pathlib.Path("answer/model_ans_1.ipynb")
    submitted_path = pathlib.Path("submitted")

    model_ans = load_model_ans(answer_path)

    for student_path in submitted_path.glob("*.ipynb"):
        student_notebook = StudentNotebook(student_path, model_ans)
        score = student_notebook.grade()
        print(f"{student_path.name} のスコア: {score}")


if __name__ == "__main__":
    main()
