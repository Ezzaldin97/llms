from typing import Dict, Optional, List
import unicodedata

class Helper:

    def _replace_control_char(self, s: str) -> str:
        chars = []
        for ch in s:
            if unicodedata.category(ch)[0] != "C":
                chars.append(ch) # this character is ok
            else:
                chars.append(f"\\u{ord(ch):04x}") # escape
        return "".join(chars)
    
    def render_tokens(self, t: bytes) -> str:
        s = t.decode("utf-8", errors = "ignore")
        s = self._replace_control_char(s)
        return s

    def encode_data(self, data: str) -> List[int]:
        enc = data.encode("utf-8")
        lst = list(enc)
        return lst
    
    def calc_frequencies(self, ids, counts: Optional[Dict] = None) -> Dict:
        counts = {} if counts is None else counts
        for pair in zip(ids, ids[1:]):
            counts[pair] = counts.get(pair, 0) + 1
        return counts
    
    def merging_pairs(self, ids, pair, idx) -> List[int]:
        new_ids = []
        counter = 0
        while counter < len(ids):
            if ids[counter] == pair[0] and counter < len(ids)-1 and ids[counter+1] == pair[1]:
                new_ids.append(idx)
                counter+=2
            else:
                new_ids.append(ids[counter])
                counter+=1
        return new_ids