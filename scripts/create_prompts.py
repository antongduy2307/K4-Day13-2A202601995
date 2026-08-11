"""Tao prompt v1 (baseline/production) va v2 (candidate) tren Langfuse cho day13-chat.

Chay mot lan: python scripts/create_prompts.py
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

from langfuse import get_client  # noqa: E402

PROMPT_NAME = os.getenv("LANGFUSE_PROMPT_NAME", "day13-chat")

PROMPT_V1 = "Feature={{feature}}\nDocs={{docs}}\nQuestion={{message}}"

PROMPT_V2 = (
    "Feature={{feature}}\n"
    "Docs={{docs}}\n"
    "Question={{message}}\n"
    "Answer in at most 3 short sentences."
)


def main() -> None:
    client = get_client()

    v1 = client.create_prompt(
        name=PROMPT_NAME,
        type="text",
        prompt=PROMPT_V1,
        labels=["baseline", "production"],
    )
    print(f"Created v1: version={v1.version} labels={v1.labels}")

    v2 = client.create_prompt(
        name=PROMPT_NAME,
        type="text",
        prompt=PROMPT_V2,
        labels=["candidate"],
    )
    print(f"Created v2: version={v2.version} labels={v2.labels}")

    client.flush()


if __name__ == "__main__":
    main()
