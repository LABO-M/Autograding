import json
import pathlib
import fnmatch
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
    answer_dir = pathlib.Path("answer/7231000021-2")
    submitted_path = pathlib.Path("submitted/7231000021-2")

    # 解答モデルの読み込みと格納
    model_ans_dict = {}
    for model_ans_path in answer_dir.glob("*.ipynb"):
        model_name = model_ans_path.stem  # ファイル名から拡張子を除いた名前を取得
        model_ans_dict[model_name] = load_model_ans(model_ans_path)

    for student_path in submitted_path.glob("*_assignsubmission_file_/*.ipynb"):
        # 採点ファイルの名前から解答モデルを特定
        assignment_name = student_path.stem

        # ファイル名が特定のパターンに一致する解答モデルを探す
        model_ans = None
        for model_name, ans in model_ans_dict.items():
            if fnmatch.fnmatch(assignment_name, f"{model_name}*"):
                model_ans = ans
                break

        # 解答モデルが見つからない場合はエラーを表示して次のファイルへ
        if model_ans is None:
            print(f"エラー: 解答モデルが見つからない (ファイル名: {assignment_name})")
            continue

        student_notebook = StudentNotebook(student_path, model_ans)
        score = student_notebook.grade()
        print(f"{student_notebook.student_name} {model_name}のスコア: {score}")


if __name__ == "__main__":
    main()
