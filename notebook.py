import re
import json
import pathlib
from typing import Dict, List
from utils import *

class StudentNotebook:
    def __init__(self, student_path: pathlib.Path, model_ans: Dict[int, List[str]], is_local: bool = True):
        self.student_path = student_path
        self.model_ans = model_ans
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
        question_cells = get_question_cells(self.cells)
        not_found_questions = []

        mark_answer = self.mark_answer_for_local if self.is_local else self.mark_answer
        write_score = self.write_score_for_local if self.is_local else self.write_score

        total_questions = sum(1 for ans, is_plot in self.model_ans.values() if not is_plot)

        for question_num, sub_question_num in self.model_ans.keys():
            ans_cell = question_cells.get((question_num, sub_question_num))

            if ans_cell is not None:
                student_ans_text, is_plot_student = get_output_from_cell(ans_cell)
                model_ans, is_plot_model = self.model_ans.get((question_num, sub_question_num))
                # プロット問題なら採点をスキップ
                if is_plot_model:
                    continue

                is_correct = student_ans_text == model_ans

                if is_correct:
                    score += 1

                mark_answer((question_num, sub_question_num), ans_cell, is_correct)
            else:
                not_found_questions.append((question_num, sub_question_num))

        write_score(score, total_questions, not_found_questions)
        return score

    def mark_answer_for_local(self, question_num: int, ans_cell: Dict, is_correct: bool) -> None:
        mark = '正解' if is_correct else '不正解'

        # 採点結果を格納
        self.marking_results.append((question_num, mark))

    def write_score_for_local(self, score: int, total_questions: int, not_found_questions: List[int]) -> None:
        score_text = f"＜採点結果＞\n{score}点／{total_questions}点満点中\nプロット問題を除く\n"
        if not_found_questions:
            not_found_text = ", ".join(f"{num[0]}({num[1]})" if num[1] is not None else str(num[0]) for num in not_found_questions)
            score_text += f"問題{not_found_text}のセルが見つかりませんでした。問題セルの書式を変更しないでください。\n"

        # スコアの表示
        print(score_text)

        # 各問題の採点結果の表示
        for question_tuple, mark in self.marking_results:
            if question_tuple[1] is not None:
                print(f"問題{question_tuple[0]} ({question_tuple[1]}): {mark}")
            else:
                print(f"問題{question_tuple[0]}: {mark}")

    def mark_answer(self, question_num: Tuple[int, Optional[int]], ans_cell: Dict, is_correct: bool) -> None:
        mark = '正解' if is_correct else '不正解'
        index = self.cells.index(ans_cell)

        # 小問番号がNoneの場合とそうでない場合でマークダウンの書式を分ける
        if question_num[1] is not None:
            mark_text = f"**採点結果 (問題{question_num[0]} ({question_num[1]})): {mark}**"
        else:
            mark_text = f"**採点結果 (問題{question_num[0]}): {mark}**"

        # 正誤を表示するマークダウンセルを作成する
        mark_cell = {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [mark_text]
        }

        # アンサーセルの後に同様のマークダウンセルがあるか確認
        if index < len(self.cells) - 1 and self.cells[index + 1]['cell_type'] == 'markdown' and self.cells[index + 1]['source'][0].startswith("**採点結果 (問題"):
            self.cells[index + 1] = mark_cell
        else:
            self.cells.insert(index + 1, mark_cell)


    def write_score(self, score: int, total_questions: int, not_found_questions: List[Tuple[int, Optional[int]]]) -> None:
        score_text = ["### 採点結果\n", f"**{score}点 / {total_questions}点満点中**"]
        if not_found_questions:
            not_found_text = ", ".join(f"{num[0]}({num[1]})" if num[1] is not None else str(num[0]) for num in not_found_questions)
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
