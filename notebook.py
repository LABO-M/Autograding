import re
import json
import pathlib
from typing import Dict, List
from utils import *

class StudentNotebook:
    def __init__(self, student_path: pathlib.Path, model_ans: Dict[int, List[str]]):
        self.student_path = student_path
        self.model_ans = model_ans
        self.cells = load_cells(self.student_path)
        self.student_name = self.get_student_name()

    def get_student_name(self) -> str:
        return self.student_path.parent.parts[-1].split("_")[0]

    def grade(self) -> int:
        score = 0
        question_cells = get_question_cells(self.cells)

        for question_num, ans_cell in question_cells.items():
            student_ans_text = get_output_from_cell(ans_cell)

            is_correct = student_ans_text == self.model_ans.get(question_num)

            if is_correct:
                score += 1

            self.mark_answer(question_num, ans_cell, is_correct)

        self.write_score(score, len(self.model_ans))
        return score

    def mark_answer(self, question_num: int, ans_cell: Dict, is_correct: bool) -> None:
        mark = '正解' if is_correct else '不正解'

        # 正誤を表示するマークダウンセルを作成する
        mark_cell = {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [f"**採点結果 (問題{question_num}): {mark}**"]
        }

        # マークダウンセルをアンサーセルの後に挿入する
        index = self.cells.index(ans_cell)
        self.cells.insert(index + 1, mark_cell)


    def write_score(self, score: int, total_questions: int) -> None:
        score_cell = {
            'cell_type': 'markdown',
            'metadata': {},
            'source': ["### 採点結果\n", f"**{score}点 / {total_questions}点満点中**"]
        }

        # ノートブックの一番上のセルの下に新たなセルを挿入
        self.cells.insert(1, score_cell)

        # 解答用の ipynb に dump (上書き)
        with open(self.student_path, "w") as f:
            json.dump({"cells": self.cells, "metadata": {}}, f)
