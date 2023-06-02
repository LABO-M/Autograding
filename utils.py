import pathlib
import json
import re
from typing import Dict, List, Optional

def identify_cell(sentence: str, cells: List[Dict], cell_type: str = 'code') -> int:
    for i, _cell in enumerate(cells):
        if _cell['cell_type'] == cell_type and len(_cell['source']) > 0 and _cell['source'][0].startswith(sentence):
            return i
    return -1

def load_cells(path: pathlib.Path) -> List[Dict]:
    with open(path, "r") as f:
        nb = json.load(f)
        cells = nb["cells"]
    return cells

def get_question_cells(cells: List[Dict], max_question_num: int = 30) -> Dict[int, Dict]:
    question_cells = {}

    # 正規表現を用いて「#問題X(Y)」の形式を捜索
    pattern = re.compile(r'#問題(\d+)(\((\d+)\))?')

    for i, cell in enumerate(cells):
        if 'source' in cell and isinstance(cell['source'], list):
            for line in cell['source']:
                match = pattern.match(line)
                if match:
                    # question_numberには「X」の部分が、sub_question_numberには「Y」の部分が入る
                    question_number = int(match.group(1))
                    sub_question_number = int(match.group(3)) if match.group(3) else None
                    key = (question_number, sub_question_number)
                    question_cells[key] = cells[i]

    return question_cells

def get_output_from_cell(cell: Dict) -> Optional[str]:
    if cell['outputs'] and cell['outputs'][0]:
        output = cell['outputs'][0]
        if 'text/plain' in output.get('data', {}):
            return [x.strip() for x in output['data']['text/plain']]
        elif 'text' in output:
            return [x.strip() for x in output['text']]
    return None
