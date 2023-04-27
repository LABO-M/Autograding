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

def convert_to_json(_nb):
    """ipynbファイルをjson形式に変換し、内容、回答セル番号、提出ファイル名を返す"""
    with open(_nb, "r") as f:
        nb = json.load(f)
        cells = nb["cells"]

    return nb, cells

def get_code_cell_nums(_nb):
    """ディレクトリ内の問題の解答セルの番号をリストで返す"""
    code_cell_nums = []
    cells = convert_to_json(_nb)[1]
    for i, cell in enumerate(cells):
        if cell["cell_type"] == "code" and re.match(r'#問題\d+', cell['source'][0]):
            code_cell_nums.append(i)

    return code_cell_nums

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

def make_dict_from_content(_nb, code_cell_nums):
    """get_cell_contentの出力を辞書型に変換する"""
    cell_content_dict = {} #{問題番号: 解答セルの中身}
    for i in range(len(code_cell_nums)):
        cell_content_dict[i+1] = get_cell_content(_nb, code_cell_nums[i])

    return cell_content_dict

def display_code_cells(_nb, code_cell_nums):
    """提出ファイルの解答セルを特定して、セルの中身を表示する"""
    display_nb = convert_to_json(_nb)[0]
    cells = convert_to_json(_nb)[1]

    for i in range(len(code_cell_nums)):
        sentence = f"#問題{i+1}"
        _cell_num = identify_cell(sentence, cells)
        if _cell_num is not None:
            cell_content = get_cell_content(display_nb, _cell_num)
            print(f"提出ファイル: {_nb.name} のセル番号: {_cell_num}")
            print(f"セル内容:\n{cell_content}")
        else:
            print(f"提出ファイル: {_nb.name} に {sentence} のセルが見つかりませんでした。")
    
    content_dict = make_dict_from_content(display_nb, code_cell_nums)
    pprint(content_dict)

if __name__ == '__main__':
    # path to notebook(.ipynb)
    path_ans_nb = pathlib.Path("./answer/")
    path_sbmt_nb = pathlib.Path("./submitted/")

    # Get a list of answer cell numbers in the directory, code_cell_nums = ge, code_cell_nums(path_ans_nb)

    for _nb in path_ans_nb.glob("*.ipynb"):

        code_cell_nums = get_code_cell_nums(_nb)
        print(f"解答セルの番号:{code_cell_nums}")

        display_code_cells(_nb, code_cell_nums)

    for _nb in path_sbmt_nb.glob("*.ipynb"):

        code_cell_nums = get_code_cell_nums(_nb)
        print(f"解答セルの番号:{code_cell_nums}")

        display_code_cells(_nb, code_cell_nums)

    

