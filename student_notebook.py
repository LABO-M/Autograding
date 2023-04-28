import json
import pathlib
from typing import Dict, List
from utils import *

class StudentNotebook:
    def __init__(self, student_path: pathlib.Path, model_ans: Dict[int, List[str]]):
        self.student_path = student_path
        self.model_ans = model_ans
        self.cells = load_cells(self.student_path)

    def grade(self) -> int:
        score = 0
        question_cells = get_question_cells(self.cells)

        for question_num, ans_cell in question_cells.items():
            student_ans_text = get_output_from_cell(ans_cell)
            if student_ans_text == self.model_ans.get(question_num):
                    score += 1

        return score
