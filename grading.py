import json
import pathlib
from typing import Dict, List
from utils import *
from notebook import StudentNotebook

def load_model_ans(path: pathlib.Path) -> Dict[int, List[str]]:
    cells = load_cells(path)
    question_cells = get_question_cells(cells)

    model_ans = {}
    for question_num, ans_cell in question_cells.items():
        model_ans[question_num] = get_output_from_cell(ans_cell)

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
