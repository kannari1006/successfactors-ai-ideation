import json
import os
import random

ideas_file = "ideas.json"
if os.path.exists(ideas_file):
    with open(ideas_file, "r", encoding="utf-8") as f:
        ideas = json.load(f)

    for i in ideas:
        if "recommendation_score" not in i:
            # Add a random default recommendation score if not present
            i["recommendation_score"] = random.randint(3, 5)

    with open(ideas_file, "w", encoding="utf-8") as f:
        json.dump(ideas, f, indent=2, ensure_ascii=False)
    print("Schema updated successfully with recommendation scores.")
else:
    print("File not found.")
