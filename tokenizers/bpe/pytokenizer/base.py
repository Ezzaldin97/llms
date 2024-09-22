from bpe.pytokenizer.utils import Helper
from typing import List, Dict
import os

class Base:
    def __init__(self) -> None:
        self.merges = {}
        self.pattern = ""
        self.special_tokens = {}
        self.vocab = self._construct_vocab()

    def _construct_vocab(self) -> Dict[int, bytes]:
        vocab = {idx: bytes([idx]) for idx in range(256)}
        for (idx1, idx2), idx in self.merges.items():
            vocab[idx] = vocab[idx1] + vocab[idx2]
        for token, idx in self.special_tokens.items():
            vocab[idx] = token.encode("utf-8")
        return vocab

    def train(self, data_path: str, vocab_size: int) -> None:
        raise NotImplementedError
    
    def encode(self, text: str) -> List[int]:
        raise NotImplementedError
    
    def decode(self, ids: List[int]) -> str:
        raise NotImplementedError
    
    def tokenize(self, text: str) -> List[str]:
        raise NotImplementedError
    
    def id_to_token(self, id: int) -> str:
        raise NotImplementedError
        
    def save(self, name: str, path: str) -> None:
        model_file = f"{name}.model"
        with open(os.path.join(path, model_file), mode = "a+") as model:
            model.write("microbpe\n")
            model.write(f"{self.pattern}")
            model.write(f"{len(self.special_tokens)}\n")
            for token, idx in self.special_tokens.items():
                model.write(f"{token} {idx}\n")
            for idx1, idx2 in self.merges:
                model.write(f"{idx1} {idx2}\n")
        vocab_file = f"{name}.txt"
        inverted_merges = {idx: pair for pair, idx in self.merges.items()}
        with open(os.path.join(path, vocab_file), mode = "a+", encoding="utf-8") as vocab:
            for idx, token in self.vocab.items():
                helper = Helper()
                s = helper.render_tokens(token)
                if idx in inverted_merges:
                    # if this token has children, render it nicely as a merge
                    idx0, idx1 = inverted_merges[idx]
                    s0 = helper.render_tokens(self.vocab[idx0])
                    s1 = helper.render_tokens(self.vocab[idx1])
                    vocab.write(f"[{s0}][{s1}] -> [{s}] {idx}\n")
                else:
                    # (this should just be the first 256 tokens, the bytes)
                    vocab.write(f"[{s}] {idx}\n")

    def load(self, path: str) -> None:
        if path.endswith(".model"):
            merges = {}
            special_tokens = {}
            idx = 256
            with open(path, mode = "r", encoding="utf-8") as model:
                version = model.readline().strip()
                assert version == "microbpe"
                special_tokens_length = int(model.readline().strip())
                for _ in range(special_tokens_length):
                    special, special_idx = model.readline().strip().split()
                    special_tokens[special] = special_idx
                for line in model:
                    idx1, idx2 = map(int, line.split())
                    merges[(idx1, idx2)] = idx
                    idx+=1
            self.merges = merges
            self.special_tokens = special_tokens
            self.vocab = self._construct_vocab()
        else:
            raise ValueError("Expected to find .model file")
