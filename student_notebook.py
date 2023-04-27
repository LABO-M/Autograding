import json
import pathlib
from typing import Dict, List
from utils import identify_cell


class StudentNotebook:
    def __init__(self, student_path: pathlib.Path, model_ans: Dict[int, List[str]]):
        self.student_path = student_path
        self.model_ans = model_ans
        self.cells = self._load_cells()

    def _load_cells(self) -> List[Dict]:
        with open(self.student_path, "r") as f:
            nb = json.load(f)
            cells = nb["cells"]
        return cells

    def grade(self) -> int:
        score = 0
        for question_num, model_ans_texts in self.model_ans.items():
            cn = identify_cell(sentence=f"#問題{question_num}\n", cells=self.cells)
            if cn != -1:
                ans_cell = self.cells[cn]
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
