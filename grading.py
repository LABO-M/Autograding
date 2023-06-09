import json
import argparse
import pathlib
import fnmatch
from typing import Dict, List
from utils import *
from notebook import StudentNotebook

def load_model_ans(path: pathlib.Path) -> Dict[int, List[str]]:
    cells = load_cells(path)
    question_cells = get_question_cells(cells)

    model_ans = {}
    for question_num_tuple, ans_cell in question_cells.items():
        model_ans[question_num_tuple] = get_output_from_cell(ans_cell)

    return model_ans

# 生徒一括採点モード
def batch_grading(answer_dir_path: str, submitted_dir_path: str) -> None:
    answer_dir = pathlib.Path(answer_dir_path)
    submitted_dir = pathlib.Path(submitted_dir_path)

    # 解答モデルの読み込みと格納
    model_ans_dict = {}
    for model_ans_path in answer_dir.glob("*.ipynb"):
        model_name = model_ans_path.stem  # ファイル名から拡張子を除いた名前を取得
        model_ans_dict[model_name] = load_model_ans(model_ans_path)

    for student_path in submitted_dir.glob("*_assignsubmission_file_/*.ipynb"):
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

        student_notebook = StudentNotebook(student_path, model_ans, is_local=False)
        score = student_notebook.grade()
        print(f"{student_notebook.student_name} {model_name}のスコア: {score}")

# 生徒ローカル採点モード
def local_grading(model_ans_path: str, student_path: str) -> None:
    model_ans_path = pathlib.Path(model_ans_path)
    student_path = pathlib.Path(student_path)

    model_name = model_ans_path.stem
    model_ans = load_model_ans(model_ans_path)

    student_notebook = StudentNotebook(student_path, model_ans)
    score = student_notebook.grade()

def main():
    parser = argparse.ArgumentParser(description='Grading script.')
    parser.add_argument('--batch', action='store_true', help='Use batch mode. If not specified, local mode is used.')
    parser.add_argument('--model', type=str, help='Path to the model answer file.')
    parser.add_argument('--student', type=str, help='Path to the student notebook file.')
    parser.add_argument('--answer_dir', type=str, help='Path to the answer directory.')
    parser.add_argument('--submitted_dir', type=str, help='Path to the submitted directory.')

    args = parser.parse_args()

    if args.batch:
        if not args.answer_dir or not args.submitted_dir:
            raise ValueError("In batch mode, both --answer_dir and --submitted_dir must be specified.")
        batch_grading(args.answer_dir, args.submitted_dir)
    else:
        if not args.model or not args.student:
            raise ValueError("In local mode, both --model and --student must be specified.")
        local_grading(args.model, args.student)

if __name__ == "__main__":
    main()
