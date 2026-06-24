import json
import random
import re

# ========= CONFIG =========
PATH_QUOTES = "quotes/quotes.json"
PATH_README = "README.md"
PATH_STATUS = "status.json"

START_MARKER = "<!-- START_SECTION:daily_quote -->"
END_MARKER = "<!-- END_SECTION:daily_quote -->"

def load_status():
    try:
        with open(PATH_STATUS, "r", encoding="utf-8") as f:
            status = json.load(f)
    except FileNotFoundError:
        status = {}

    if "displayed_quotes" not in status:
        status["displayed_quotes"] = []

    return status

def save_status(status):
    with open(PATH_STATUS, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)

def load_quotes():
    with open(PATH_QUOTES, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_quote(quotes, status):
    remaining = [
        i for i in range(len(quotes))
        if i not in status["displayed_quotes"]
    ]

    if not remaining:
        status["displayed_quotes"] = []
        remaining = list(range(len(quotes)))

    idx = random.choice(remaining)
    status["displayed_quotes"].append(idx)

    return quotes[idx]

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
    quotes = load_quotes()

    q = pick_quote(quotes, status)

    block = f"""{START_MARKER}
<div align="center">

> {q['text']}

<b>— {q['author']}</b>

</div>
{END_MARKER}"""

    update_readme(block)
    save_status(status)

    print("Daily quote updated!")


if __name__ == "__main__":
    main()
