import re
import glob
import json
import openai
import pathlib
from pprint import pprint

def identify_cell(sentence, cells, cell_type='code'):
    """全てのセルから条件に一致するセルの番号をreturn"""
    for i,_cell in enumerate(cells):
        if _cell['cell_type'] == cell_type and re.match(sentence, _cell['source'][0]):
            _cell_num = i
            break
    return _cell_num

def get_answer_cells(path_nb):
    """ディレクトリ内の問題の解答セルの番号をリストで返す"""
    answer_cells = []
    for _nb in path_nb.glob("*.ipynb"):
        with open(_nb, "r") as f:
            nb = json.load(f)
            cells = nb["cells"]

        for i, cell in enumerate(cells):
            if cell["cell_type"] == "code" and re.match(r'#問題\d+', cell['source'][0]):
                answer_cells.append(i)

    return answer_cells

def get_cell_content(nb, cell_num):
    """指定したセル番号のテキストの中身を返す"""
    cells = nb["cells"]
    cell = cells[cell_num]
    try:
        if cell['outputs']:
            output = cell['outputs'][0]
            if 'text/plain' in output.get('data', {}):
                cell_content = output['data']['text/plain']
            elif 'text' in output:
                cell_content = output['text']
            else:
                cell_content = None
        return cell_content
    except:
        pass

def display_submission_cells(path_sbmt_nb, answer_cells):
    """提出ファイルの解答セルを特定して、セルの中身を表示する"""
    for _nb in path_sbmt_nb.glob("*.ipynb"):
        with open(_nb, "r") as f:
            nb = json.load(f)
            cells = nb["cells"]

        for i in range(len(answer_cells)):
            sentence = f"#問題{i+1}"
            _cell_num = identify_cell(sentence, cells)
            if _cell_num is not None:
                cell_content = get_cell_content(nb, _cell_num)
                print(f"提出ファイル: {_nb.name} のセル番号: {_cell_num}")
                print(f"セル内容:\n{cell_content}")
            else:
                print(f"提出ファイル: {_nb.name} に {sentence} のセルが見つかりませんでした。")

    answer_content_dict = {} #{問題番号: 解答セルの中身}
    for i in range(len(answer_cells)):
        answer_content_dict[i+1] = get_cell_content(nb, answer_cells[i])

    pprint(answer_content_dict)

if __name__ == '__main__':
    # path to notebook(.ipynb)
    path_ans_nb = pathlib.Path("./answer/")
    path_sbmt_nb = pathlib.Path("./submitted/")

    # Get a list of answer cell numbers in the directory
    answer_cells = get_answer_cells(path_ans_nb)
    print(f"解答セルの番号: {answer_cells}")

    display_submission_cells(path_sbmt_nb, answer_cells)

