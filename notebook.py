import re
import json
import pathlib
from typing import Dict, List
from utils import *

class StudentNotebook:
    def __init__(self, student_path: pathlib.Path, model_ans: Dict[int, List[str]], is_local: bool = True):
        self.student_path = student_path
        self.model_ans = model_ans
        self.max_question_num = len(model_ans)
        self.marking_results = []  # 採点結果を格納するリストを追加
        self.cells = load_cells(self.student_path)
        # ローカルモードでない場合のみ、get_student_nameを実行
        self.is_local = is_local
        if not self.is_local:
            self.student_name = self.get_student_name()

    def get_student_name(self) -> str:
        return self.student_path.parent.parts[-1].split("_")[0]

    def grade(self) -> int:
        score = 0
        question_cells = get_question_cells(self.cells, self.max_question_num)
        not_found_questions = []

        mark_answer = self.mark_answer_for_local if self.is_local else self.mark_answer
        write_score = self.write_score_for_local if self.is_local else self.write_score

        for question_num in range(1, self.max_question_num + 1):
            ans_cell = question_cells.get(question_num)

            if ans_cell is not None:
                student_ans_text = get_output_from_cell(ans_cell)
                model_ans = self.model_ans.get(question_num)
                is_correct = student_ans_text == model_ans

                if is_correct:
                    score += 1

                mark_answer(question_num, ans_cell, is_correct)
            else:
                not_found_questions.append(question_num)

        write_score(score, len(self.model_ans), not_found_questions)
        return score

    def mark_answer_for_local(self, question_num: int, ans_cell: Dict, is_correct: bool) -> None:
        mark = '正解' if is_correct else '不正解'

        # 採点結果を格納
        self.marking_results.append((question_num, mark))

    def write_score_for_local(self, score: int, total_questions: int, not_found_questions: List[int]) -> None:
        score_text = f"＜採点結果＞\n{score}点／{total_questions}点満点中\n"
        if not_found_questions:
            not_found_text = ", ".join(str(num) for num in not_found_questions)
            score_text += f"問題{not_found_text}のセルが見つかりませんでした。問題セルの書式を変更しないでください。\n"

        # スコアの表示
        print(score_text)

        # 各問題の採点結果の表示
        for question_num, mark in self.marking_results:
            print(f"問題{question_num}: {mark}")

    def mark_answer(self, question_num: int, ans_cell: Dict, is_correct: bool) -> None:
        mark = '正解' if is_correct else '不正解'
        index = self.cells.index(ans_cell)

        # 正誤を表示するマークダウンセルを作成する
        mark_cell = {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [f"**採点結果 (問題{question_num}): {mark}**"]
        }

        # アンサーセルの後に同様のマークダウンセルがあるか確認
        if index < len(self.cells) - 1 and self.cells[index + 1]['cell_type'] == 'markdown' and self.cells[index + 1]['source'][0].startswith("**採点結果 (問題"):
            self.cells[index + 1] = mark_cell
        else:
            self.cells.insert(index + 1, mark_cell)


    def write_score(self, score: int, total_questions: int, not_found_questions: List[int]) -> None:
        score_text = ["### 採点結果\n", f"**{score}点 / {total_questions}点満点中**"]
        if not_found_questions:
            not_found_text = ", ".join(str(num) for num in not_found_questions)
            score_text.append(f"\n\n問題{not_found_text}のセルが見つかりませんでした。問題セルの書式を変更しないでください。")

        score_cell = {
            'cell_type': 'markdown',
            'metadata': {},
            'source': score_text
        }

        # 既にスコアセルが存在するかどうか確認
        if self.cells[1]['cell_type'] == 'markdown' and self.cells[1]['source'][0] == "### 採点結果\n":
            self.cells[1] = score_cell
        else:
            self.cells.insert(1, score_cell)

        # 解答用の ipynb に dump (上書き)
        try:
            with open(self.student_path, "w") as f:
                json.dump({"cells": self.cells, "metadata": {}}, f)
        except Exception as e:
            print(f"エラー: ファイルへの書き込みに失敗しました。 (エラーメッセージ: {str(e)})")
