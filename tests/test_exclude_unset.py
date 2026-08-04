"""Demo: understand Pydantic's exclude_unset=True.

Run:
    python3 demo_exclude_unset.py
"""

import json
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str
    temperature: float = 0.7
    max_tokens: int = 1024
    metadata: dict[str, str] = {}


def show(title: str, message: ChatMessage) -> None:
    print(f"\n=== {title} ===")
    print("fields explicitly set:", sorted(message.model_fields_set))

    print("\nmodel_dump():")
    print(json.dumps(message.model_dump(), ensure_ascii=False, indent=2))

    print("\nmodel_dump(exclude_unset=True):")
    print(
        json.dumps(
            message.model_dump(exclude_unset=True),
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    show(
        "1. 只传必填字段：默认值没有被显式设置，所以会被 exclude_unset 跳过",
        ChatMessage(role="user", content="你好"),
    )

    show(
        "2. 显式传了默认值：虽然值等于默认值，但它已经被设置过，所以会保留",
        ChatMessage(
            role="user",
            content="你好",
            temperature=0.7,
            max_tokens=1024,
        ),
    )

    show(
        "3. 显式传了非默认值：当然也会保留",
        ChatMessage(
            role="user",
            content="请用一句话回答",
            temperature=0.2,
            max_tokens=50,
            metadata={"trace_id": "demo-001"},
        ),
    )


if __name__ == "__main__":
    main()
