import json
import random

PATH_SERVER_TIPS = "server_tips.json"

def load_server_tips():
    with open(PATH_SERVER_TIPS, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_server_tip(tips):
    return random.choice(tips)
