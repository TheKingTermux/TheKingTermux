import re
from datetime import datetime
from zoneinfo import ZoneInfo

PATH_README = "README.md"

START_MARKER = "<!-- START_SECTION:time -->"
END_MARKER = "<!-- END_SECTION:time -->"

TZ = ZoneInfo("Asia/Jakarta")


def get_time():
    now = datetime.now(TZ)

    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%A, %d %B %Y")

    return time_str, date_str

def update_readme(time_str, date_str):
    with open(PATH_README, "r", encoding="utf-8") as f:
        content = f.read()

    block = f"""{START_MARKER}
<div align="center">
🕒 {time_str} WIB  
📅 {date_str}
</div>
{END_MARKER}"""

    pattern = re.compile(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        re.DOTALL
    )

    content = pattern.sub(block, content)

    with open(PATH_README, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    time_str = get_time()
    update_readme(time_str)
    print("Time updated!")


if __name__ == "__main__":
    main()
