import json
import os
import re

ideas_file = "ideas.json"

if os.path.exists(ideas_file):
    with open(ideas_file, "r", encoding="utf-8") as f:
        ideas = json.load(f)

    for i in ideas:
        approach = i.get("approach", "")
        # Look for the old mock/AI reviews which were appended as "【...】..." at the end of the approach
        match = re.search(r'\n+?【(?:追加検討|.*?の指摘)】.*$', approach, re.DOTALL)
        if match and not i.get("review_comment"):
            extracted_review = match.group(0).strip()
            # Remove the newlines and brackets to make it look like the new format
            formatted_review = extracted_review.replace("【", "").replace("】", ": ", 1)
            i["review_comment"] = formatted_review
            # Remove it from the approach
            i["approach"] = approach.replace(match.group(0), "")

    with open(ideas_file, "w", encoding="utf-8") as f:
        json.dump(ideas, f, indent=2, ensure_ascii=False)
    print("Schema updated successfully with extracted review_comments.")
else:
    print("File not found.")
