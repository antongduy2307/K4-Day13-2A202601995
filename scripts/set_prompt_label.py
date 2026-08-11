"""Doi label 'production' sang mot version cu the cua prompt day13-chat.

Chay: python scripts/set_prompt_label.py <version>
"""
from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()

from langfuse import get_client  # noqa: E402

PROMPT_NAME = os.getenv("LANGFUSE_PROMPT_NAME", "day13-chat")


def main() -> None:
    version = int(sys.argv[1])
    client = get_client()
    updated = client.update_prompt(name=PROMPT_NAME, version=version, new_labels=["production"])
    print(f"production label -> version={updated.version} labels={updated.labels}")


if __name__ == "__main__":
    main()
