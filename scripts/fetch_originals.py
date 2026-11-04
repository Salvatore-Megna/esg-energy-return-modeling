"""Download ONLY 3 authenticated historical data files from the existing public GitHub site.

These files are NOT redistributed inside this review ZIP. Please check third-party
license terms before including any ESG score panel in a public repository.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import urllib.error
import urllib.request

BASE = "https://raw.githubusercontent.com/Salvatore-Megna/Salvatore-Megna.github.io/main/projects/esg-performance/assets/"
FILES = {
    "SALVATORE MEGNA DATI PANEL.xlsx": (104928, "78c6357d377d6124d3e64c64777d9a266c4e1a45"),
    "prezzi_mensili_aggiornato.csv": (91219, "7d812d37898c914ec5712506021d472e20af590a"),
    "benchmarks_monthly_returns.csv": (7700, "14e03de0fd48a9782eec829ef643f53ec0f5b6e9"),
}


def git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def validate_payload(name: str, payload: bytes) -> None:
    size, sha = FILES[name]
    if len(payload) != size or git_blob_sha1(payload) != sha:
        raise ValueError(f"Authenticity check failed for {name}")


def main():
    from urllib.parse import quote
    destination = Path("data/raw")
    destination.mkdir(parents=True, exist_ok=True)
    for filename in FILES:
        path = destination / filename
        if path.exists():
            validate_payload(filename, path.read_bytes())
            print("Already verified:", filename)
            continue
        url = BASE + quote(filename)
        print("Retrieving:", filename)
        req = urllib.request.Request(url, headers={"User-Agent": "ESG-portfolio-reproducibility/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                payload = response.read()
        except (urllib.error.URLError, TimeoutError) as e:
            raise RuntimeError(f"Cannot download {filename}; retrieve it from the original GitHub site") from e
        validate_payload(filename, payload)
        path.write_bytes(payload)
        print("Verified Git blob SHA-1:", FILES[filename][1])


if __name__ == "__main__":
    main()
