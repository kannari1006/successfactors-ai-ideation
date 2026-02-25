import json
import random

def generate_varied_schedule(title, target):
    # Total months varies between 3 and 7
    total_months = random.randint(3, 7)
    
    # We define standard phases based on total months
    
    overall_items = []
    vendor_items = []
    client_items = []
    task_list = []
    
    if total_months <= 3:
        overall_items = [
            {"name": "要件定義", "start": 1, "end": 1},
            {"name": "開発・実装", "start": 2, "end": 2},
            {"name": "テスト・リリース", "start": 3, "end": 3}
        ]
        vendor_items = [
            {"name": "システム要件定義", "start": 1, "end": 1},
            {"name": "システム構築", "start": 2, "end": 2},
            {"name": "結合テスト・本番展開", "start": 3, "end": 3}
        ]
        client_items = [
            {"name": "業務要件整理", "start": 1, "end": 1},
            {"name": "既存データ整理", "start": 1, "end": 2},
            {"name": "UAT・マニュアル", "start": 3, "end": 3}
        ]
        task_list = [
            {"phase": "要件定義", "name": "業務課題とToBeフローの策定", "duration": "2週間", "dependency": "なし", "actor": "顧客"},
            {"phase": "要件定義", "name": "システム要件ヒアリング・Fit&Gap", "duration": "2週間", "dependency": "ToBeフロー策定後", "actor": "ベンダー"},
            {"phase": "開発・実装", "name": "SuccessFactors基本設定・拡張開発", "duration": "3週間", "dependency": "要件定義完了", "actor": "ベンダー"},
            {"phase": "開発・実装", "name": "移行用データクレンジング", "duration": "4週間", "dependency": "なし", "actor": "顧客"},
            {"phase": "テスト・リリース", "name": "結合テスト・移行リハーサル", "duration": "2週間", "dependency": "開発完了", "actor": "ベンダー"},
            {"phase": "テスト・リリース", "name": "UAT（受入テスト）", "duration": "1週間", "dependency": "結合テスト完了", "actor": "顧客"},
            {"phase": "テスト・リリース", "name": "社内マニュアル作成・展開", "duration": "2週間", "dependency": "UAT完了", "actor": "顧客"}
        ]
    elif total_months == 4:
        overall_items = [
            {"name": "企画・要件定義", "start": 1, "end": 1},
            {"name": "プロトタイプ構築", "start": 2, "end": 2},
            {"name": "本番実装", "start": 3, "end": 3},
            {"name": "テスト・移行", "start": 4, "end": 4}
        ]
        vendor_items = [
            {"name": "システム要件定義", "start": 1, "end": 1},
            {"name": "設定・レビュー", "start": 2, "end": 2},
            {"name": "本番環境構築・開発", "start": 3, "end": 3},
            {"name": "テスト・運用引き継ぎ", "start": 4, "end": 4}
        ]
        client_items = [
            {"name": "企画策定", "start": 1, "end": 1},
            {"name": "評価・フィードバック", "start": 2, "end": 2},
            {"name": "実データ準備", "start": 2, "end": 3},
            {"name": "受入テスト・周知", "start": 4, "end": 4}
        ]
        task_list = [
            {"phase": "企画・要件定義", "name": "導入目的の明確化・KPI設定", "duration": "2週間", "dependency": "なし", "actor": "顧客"},
            {"phase": "企画・要件定義", "name": "システム要件・データ要件定義", "duration": "2週間", "dependency": "導入目的明確化後", "actor": "ベンダー"},
            {"phase": "プロトタイプ構築", "name": "標準機能によるプロトタイプ作成", "duration": "2週間", "dependency": "要件定義完了", "actor": "ベンダー"},
            {"phase": "プロトタイプ構築", "name": "プロトタイプ触込・Gap特定", "duration": "2週間", "dependency": "プロトタイプ作成後", "actor": "顧客"},
            {"phase": "本番実装", "name": "本番環境構築・権限設定", "duration": "3週間", "dependency": "Gap合意後", "actor": "ベンダー"},
            {"phase": "本番実装", "name": "マスタデータ登録", "duration": "1週間", "dependency": "構築着手", "actor": "顧客"},
            {"phase": "テスト・移行", "name": "システム結合テスト", "duration": "2週間", "dependency": "実装完了", "actor": "ベンダー"},
            {"phase": "テスト・移行", "name": "受入テスト・本番稼働", "duration": "2週間", "dependency": "結合テスト完了", "actor": "顧客"}
        ]
    elif total_months == 5:
        overall_items = [
            {"name": "要件定義", "start": 1, "end": 1},
            {"name": "基本設計", "start": 2, "end": 2},
            {"name": "詳細設計・構築", "start": 3, "end": 4},
            {"name": "テスト・リリース", "start": 5, "end": 5}
        ]
        vendor_items = [
            {"name": "要件ヒアリング", "start": 1, "end": 1},
            {"name": "基本設計", "start": 2, "end": 2},
            {"name": "詳細設計・構築", "start": 3, "end": 4},
            {"name": "テスト・移行計画", "start": 5, "end": 5}
        ]
        client_items = [
            {"name": "業務フローToBe策定", "start": 1, "end": 1},
            {"name": "承認プロセス決定", "start": 2, "end": 2},
            {"name": "データクレンジング", "start": 2, "end": 4},
            {"name": "UAT・展開準備", "start": 5, "end": 5}
        ]
        task_list = [
            {"phase": "要件定義", "name": "現行課題の洗い出し・ToBe定義", "duration": "3週間", "dependency": "なし", "actor": "顧客"},
            {"phase": "要件定義", "name": "システム化要件の整理", "duration": "2週間", "dependency": "ToBe定義開始後", "actor": "ベンダー"},
            {"phase": "基本設計", "name": "モジュール構成・連携方式設計", "duration": "3週間", "dependency": "要件定義完了", "actor": "ベンダー"},
            {"phase": "基本設計", "name": "決裁・承認ルートの確定", "duration": "2週間", "dependency": "なし", "actor": "顧客"},
            {"phase": "詳細設計・構築", "name": "カスタムオブジェクト開発・UI設定", "duration": "6週間", "dependency": "基本設計完了", "actor": "ベンダー"},
            {"phase": "詳細設計・構築", "name": "移行対象データの抽出・加工", "duration": "6週間", "dependency": "なし", "actor": "顧客"},
            {"phase": "テスト・リリース", "name": "総合テスト・パフォーマンス検証", "duration": "2週間", "dependency": "構築完了", "actor": "ベンダー"},
            {"phase": "テスト・リリース", "name": "業務シナリオテスト (UAT)", "duration": "2週間", "dependency": "総合テスト完了後", "actor": "顧客"}
        ]
    else: # 6 or 7 months
        total=total_months
        overall_items = [
            {"name": "要件定義", "start": 1, "end": 1},
            {"name": "設計", "start": 2, "end": 3},
            {"name": "構築", "start": 4, "end": total-1},
            {"name": "テスト・本番", "start": total, "end": total}
        ]
        vendor_items = [
            {"name": "要件定義支援", "start": 1, "end": 1},
            {"name": "システム設計", "start": 2, "end": 3},
            {"name": "実装・単体テスト", "start": 4, "end": total-1},
            {"name": "総合テスト・稼働支援", "start": total, "end": total}
        ]
        client_items = [
            {"name": "業務要件確定", "start": 1, "end": 1},
            {"name": "データ移行方針決定", "start": 2, "end": 3},
            {"name": "データ移行作業", "start": 3, "end": total-1},
            {"name": "UAT・本番移行判定", "start": total, "end": total}
        ]
        task_list = [
            {"phase": "要件定義", "name": "プロジェクト憲章・体制構築", "duration": "2週間", "dependency": "なし", "actor": "全体"},
            {"phase": "要件定義", "name": "業務要件定義・ギャップ分析", "duration": "4週間", "dependency": "体制構築後", "actor": "ベンダー"},
            {"phase": "要件定義", "name": "システム外運用ルールの策定", "duration": "3週間", "dependency": "ギャップ分析後", "actor": "顧客"},
            {"phase": "設計", "name": "統合データモデル設計", "duration": "5週間", "dependency": "要件定義完了", "actor": "ベンダー"},
            {"phase": "構築", "name": "コア機能実装・連携API開発", "duration": str((total-3)*4) + "週間", "dependency": "設計完了", "actor": "ベンダー"},
            {"phase": "構築", "name": "テストシナリオ作成", "duration": "3週間", "dependency": "実装後半", "actor": "顧客"},
            {"phase": "構築", "name": "本番系データセットアップ", "duration": "4週間", "dependency": "開発完了前", "actor": "顧客"},
            {"phase": "テスト・本番", "name": "システム結合・総合テスト", "duration": "2週間", "dependency": "実装完了", "actor": "ベンダー"},
            {"phase": "テスト・本番", "name": "UAT（ユーザー受入テスト）", "duration": "2週間", "dependency": "総合テスト後", "actor": "顧客"}
        ]
        
    return {
        "durations": total_months,
        "tracks": [
            {"name": "全体スケジュール", "items": overall_items},
            {"name": "ベンダー (導入)", "items": vendor_items},
            {"name": "企業側 (人事・情シス)", "items": client_items}
        ],
        "tasks": task_list
    }

def process():
    with open('ideas.json', 'r', encoding='utf-8') as f:
        ideas = json.load(f)
        
    random.seed(42)
    
    for idea in ideas:
        idea['schedule'] = generate_varied_schedule(idea['title'], idea['target'])
        
    with open('ideas.json', 'w', encoding='utf-8') as f:
        json.dump(ideas, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    process()
