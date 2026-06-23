import json
import random
import re

PATH_TIPS = "server_tips.json"
PATH_README = "README.md"
PATH_STATUS = "status.json"

START_MARKER = "<!-- START_SECTION:server_tip -->"
END_MARKER = "<!-- END_SECTION:server_tip -->"


def load_status():
    try:
        with open(PATH_STATUS, "r", encoding="utf-8") as f:
            status = json.load(f)
    except FileNotFoundError:
        status = {}

    if "displayed_server_tips" not in status:
        status["displayed_server_tips"] = []

    return status


def save_status(status):
    with open(PATH_STATUS, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)


def load_tips():
    with open(PATH_TIPS, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_tip(tips, status):
    remaining = [
        i for i in range(len(tips))
        if i not in status["displayed_server_tips"]
    ]

    if not remaining:
        status["displayed_server_tips"] = []
        remaining = list(range(len(tips)))

    idx = random.choice(remaining)
    status["displayed_server_tips"].append(idx)

    return tips[idx]


def update_readme(block):
    with open(PATH_README, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        re.DOTALL
    )

    content = pattern.sub(block, content)

    with open(PATH_README, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    status = load_status()
    tips = load_tips()

    tip = pick_tip(tips, status)

    block = f"""{START_MARKER}

> **{tip['title']}**
>
> {tip['text']}

{END_MARKER}"""

    update_readme(block)
    save_status(status)

    print("Daily server tip updated!")


if __name__ == "__main__":
    main()
