from typing import Dict, List

def identify_cell(sentence: str, cells: List[Dict], cell_type: str = 'code') -> int:
    for i, _cell in enumerate(cells):
        if _cell['cell_type'] == cell_type and _cell['source'][0] == sentence:
            return i
    return -1
