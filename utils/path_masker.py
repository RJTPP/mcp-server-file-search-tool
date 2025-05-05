from pathlib import Path
from typing import List, Tuple, Dict, Literal


def create_masked_map(
    look_for: List[str],
    mask_token: str = "MASK",
    mode: Literal["prefix", "segment"] = "prefix"
) -> Tuple[Dict[str, str], Dict[str, str]]:
    masked_map = {}
    reversed_map = {}
    for idx, sensitive in enumerate(look_for):
        masked = f"[{mask_token}{idx}]"
        full_path = str(Path(sensitive).resolve(strict=False)).rstrip("/")
        key = full_path if mode == "prefix" else Path(full_path).name
        masked_map[key] = masked
        reversed_map[masked] = key
    return masked_map, reversed_map


class PathMasker:
    def __init__(
        self,
        look_for: List[str],
        mask_token: str = "MASK",
        mode: Literal["prefix", "segment"] = "prefix"
    ):
        self.mode = mode
        self.masked_map, self.reversed_map = create_masked_map(look_for, mask_token, mode)

    def mask_path(self, path: str) -> str:
        abs_path = str(Path(path).resolve(strict=False)).rstrip("/")

        if self.mode == "prefix":
            for original, masked in sorted(self.masked_map.items(), key=lambda x: -len(x[0])):
                if abs_path.startswith(original):
                    return abs_path.replace(original, masked, 1)
            return abs_path

        elif self.mode == "segment":
            parts = abs_path.split("/")
            masked_parts = [
                self.masked_map.get(part, part) for part in parts
            ]
            return "/".join(masked_parts)

    def unmask_path(self, path: str) -> str:
        if self.mode == "prefix":
            for masked, original in self.reversed_map.items():
                if path.startswith(masked):
                    return path.replace(masked, original, 1)
            return path

        elif self.mode == "segment":
            parts = path.split("/")
            unmasked_parts = [
                self.reversed_map.get(part, part) for part in parts
            ]
            return "/".join(unmasked_parts)

    def mask_multiple_paths(self, paths: List[str]) -> List[str]:
        return [self.mask_path(path) for path in paths]

    def unmask_multiple_paths(self, paths: List[str]) -> List[str]:
        return [self.unmask_path(path) for path in paths]
        