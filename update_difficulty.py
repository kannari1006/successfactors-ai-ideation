import json
import os
import random

ideas_file = "ideas.json"
difficulties = [
    "低難易度（標準機能の範囲内で完結するため）",
    "低難易度（クイックウィンとして1ヶ月で導入可能）",
    "中難易度（一部アドオン開発が必要だが、要件は明確）",
    "中難易度（API連携の実装工数がやや掛かるため）",
    "中難易度（現場への操作トレーニングが主となるため）",
    "高難易度（要件定義での利害調整が難航しやすい）",
    "高難易度（複数部門にまたがる業務フローの再設計が必要）",
    "高難易度（経営層の強いコミットメントが必須となるため）"
]

if os.path.exists(ideas_file):
    with open(ideas_file, "r", encoding="utf-8") as f:
        ideas = json.load(f)

    for i in ideas:
        # Assign a random varied difficulty if it's the old default one
        if i.get("difficulty") == "高難易度（要件定義での利害調整が難航しやすい）":
            i["difficulty"] = random.choice(difficulties)

    with open(ideas_file, "w", encoding="utf-8") as f:
        json.dump(ideas, f, indent=2, ensure_ascii=False)
    print("Schema updated successfully with varied difficulties.")
else:
    print("File not found.")
