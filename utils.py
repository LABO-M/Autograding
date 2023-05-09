import pathlib
import json
from typing import Dict, List, Optional

def identify_cell(sentence: str, cells: List[Dict], cell_type: str = 'code') -> int:
    for i, _cell in enumerate(cells):
        if _cell['cell_type'] == cell_type and len(_cell['source']) > 0 and _cell['source'][0] == sentence:
            return i
    return -1

def load_cells(path: pathlib.Path) -> List[Dict]:
    with open(path, "r") as f:
        nb = json.load(f)
        cells = nb["cells"]
    return cells

def get_question_cells(cells: List[Dict]) -> Dict[int, Dict]:
    question_cells = {}
    question_num = 1

    while True:
        cn = identify_cell(sentence=f"#問題{question_num}\n", cells=cells)
        if cn != -1:
            question_cells[question_num] = cells[cn]
        else:
            break
        question_num += 1

    return question_cells

def get_output_from_cell(cell: Dict) -> Optional[str]:
    if cell['outputs'] and cell['outputs'][0]:
        output = cell['outputs'][0]
        if 'text/plain' in output.get('data', {}):
            return output['data']['text/plain']
        elif 'text' in output:
            return output['text']
    return None
