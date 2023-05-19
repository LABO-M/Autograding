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

    def get_student_info(self):
        # 学籍番号と氏名を取得するセルを特定
        info_cell_index = identify_cell(sentence="### 学籍番号、氏名を入力せよ\n", cells=self.cells, cell_type='markdown')

        if info_cell_index != -1:
            info_cell = self.cells[info_cell_index]
            info_text = "\n".join(info_cell['source'])

            # 学籍番号と氏名を抽出
            student_id = re.search(r'学籍番号：\s*([\w-]+)', info_text.replace('\n', ' '))
            student_name = re.search(r'氏名:\s*([\w\s]+)', info_text.replace('\n', ' '))

            if student_id and student_name:
                return student_id.group(1), student_name.group(1).replace(' ', '')

        # 学籍番号と氏名が見つからない場合
        return None, None

    def grade(self) -> int:
        score = 0
        question_cells = get_question_cells(self.cells)

        for question_num, ans_cell in question_cells.items():
            student_ans_text = get_output_from_cell(ans_cell)
            if student_ans_text == self.model_ans.get(question_num):
                    score += 1

        self.write_score(score, len(self.model_ans))
        return score

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
