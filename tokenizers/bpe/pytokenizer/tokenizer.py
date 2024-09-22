from bpe.pytokenizer.utils import Helper
from bpe.pytokenizer.constants import RAW, GPT2_SPLIT_PATTERN, GPT4_SPLIT_PATTERN
from bpe.pytokenizer.base import Base
from tqdm import tqdm
from typing import List, Optional

helpers = Helper()

class BPETokenizer(Base):
    def __init__(self) -> None:
        super().__init__()

    def train(
            self, 
            data_path: str, 
            vocab_size: int, 
            chunck_pattern: Optional[str] = None
    ) -> None:
        with open(data_path, encoding="utf-8", mode="r") as file:
            data = file.read()
        if vocab_size < 256:
            raise ValueError(
                "vocab_size expected to be greater than 256"
            )
        if chunck_pattern:
            ### default split pattern is gpt-2 pattern.....
            if chunck_pattern == "gpt2" or chunck_pattern is None:
                self.pattern = GPT2_SPLIT_PATTERN
            elif chunck_pattern == "gpt4":
                self.pattern = GPT4_SPLIT_PATTERN
            else:
                raise ValueError("Expected chunck pattern to be gpt2 or gpt4")
        num_merges = vocab_size - RAW
        ids = helpers.encode_data(data)
        merges = {}
        vocab = {idx: bytes([idx]) for idx in range(RAW)}
        for i in tqdm(range(num_merges), desc = "Training: "):
            stats = helpers.calc_frequencies(ids)
            pair = max(stats, key = stats.get)
            idx = RAW + i
            ids = helpers.merging_pairs(ids, pair, idx)
            merges[pair] = idx
            vocab[idx] = vocab[pair[0]]+vocab[pair[1]]
        self.merges = merges
        self.vocab = vocab
    
    def decode(self, ids: List[int]) -> str:
        text_bytes = b"".join(self.vocab[id] for id in ids)
        text = text_bytes.decode("utf-8", errors="ignore")
        return text
    
    def encode(self, text: str) -> List[int]:
        ids = helpers.encode_data(text)
        while len(ids) > 2:
            stats = helpers.calc_frequencies(ids)
            pair = min(stats, key=lambda p: self.merges.get(p, float("inf")))
            if pair not in self.merges:
                break
            idx = self.merges[pair]
            ids = helpers.merging_pairs(ids, pair, idx)
        return ids
    
    def tokenize(self, text: str) -> List[str]:
        ids = self.encode(text)
        return [self.vocab[id].decode("utf-8", errors="ignore") for id in ids]
    
    def id_to_token(self, id: int) -> str:
        try:
            return self.vocab[id].decode("utf-8", errors="ignore")
        except KeyError:
            raise KeyError(f"{id} doesn't exist")