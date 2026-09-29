import json
from pathlib import Path
from typing import Any


def write_json(caminho: Path, dados: list[dict[str, Any]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)