import os
import json
import random
import re

DIR_IMG = "img"
PATH_QUOTES = "quotes/quotes.json"
PATH_README = "README.md"
PATH_STATUS = "status.json"

START_IMG = "<!-- START_SECTION:daily_meme -->"
END_IMG = "<!-- END_SECTION:daily_meme -->"

START_QUOTE = "<!-- START_SECTION:daily_quote -->"
END_QUOTE = "<!-- END_SECTION:daily_quote -->"


# ========== LOAD STATUS ==========
def load_status():
    try:
        with open(PATH_STATUS, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"displayed_images": [], "displayed_quotes": []}


def save_status(status):
    with open(PATH_STATUS, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)


# ========== IMAGE ==========
def get_images():
    return [
        f for f in os.listdir(DIR_IMG)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
    ]


def pick_image(all_images, status):
    remaining = [
        img for img in all_images
        if img not in status["displayed_images"]
    ]

    if not remaining:
        status["displayed_images"] = []
        remaining = all_images

    selected = random.choice(remaining)
    status["displayed_images"].append(selected)

    return selected


# ========== QUOTE ==========
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


# ========== README UPDATE ==========
def update_section(content, start, end, new_block):
    pattern = re.compile(
        rf"{re.escape(start)}.*?{re.escape(end)}",
        re.DOTALL
    )
    return pattern.sub(new_block, content)


def update_readme(image, quote):
    with open(PATH_README, "r", encoding="utf-8") as f:
        content = f.read()

    img_block = f"""{START_IMG}
<p align="center">
  <img src="{DIR_IMG}/{image}" />
</p>
{END_IMG}"""

    quote_block = f"""{START_QUOTE}
<div align="center">

> {quote['text']}

<b>— {quote['author']}</b>

</div>
{END_QUOTE}"""

    content = update_section(content, START_IMG, END_IMG, img_block)
    content = update_section(content, START_QUOTE, END_QUOTE, quote_block)

    with open(PATH_README, "w", encoding="utf-8") as f:
        f.write(content)


# ========== MAIN ==========
def main():
    status = load_status()

    images = get_images()
    if not images:
        raise Exception("No images found")

    quotes = load_quotes()

    selected_image = pick_image(images, status)
    selected_quote = pick_quote(quotes, status)

    update_readme(selected_image, selected_quote)

    save_status(status)
    print("Updated successfully")


if __name__ == "__main__":
    main()
