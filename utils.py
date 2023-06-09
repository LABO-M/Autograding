import pathlib
import json
import re
from typing import Dict, List, Tuple, Optional

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

    pattern = re.compile(r'#問題(\d+)(\((\d+)\))?')

    for i, cell in enumerate(cells):
        if 'source' in cell and isinstance(cell['source'], list):
            for line in cell['source']:
                match = pattern.match(line)
                if match:
                    question_number = int(match.group(1))
                    sub_question_number = int(match.group(3)) if match.group(3) else None
                    key = (question_number, sub_question_number)
                    question_cells[key] = cells[i]

    return question_cells

def get_output_from_cell(cell: Dict) -> Tuple[Optional[str], bool]:
    if cell['outputs'] and cell['outputs'][0]:
        output = cell['outputs'][0]
        if 'text/plain' in output.get('data', {}):
            output_text = [x.strip() for x in output['data']['text/plain']]
            is_plot = any(text.startswith('<Figure') for text in output_text)
            return output_text, is_plot
        elif 'text' in output:
            return [x.strip() for x in output['text']], False
    return None, False
