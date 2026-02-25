import os
import json
import asyncio
import time
import random
from datetime import datetime, timezone
import uuid
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_KEY:
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_KEY)
        USE_AI = True
    except ImportError:
        USE_AI = False
else:
    USE_AI = False

DATA_FILE = "ideas.json"
EVENTS_FILE = "events.json"

def log_event(message):
    now = datetime.now(timezone.utc).isoformat()
    events = []
    if os.path.exists(EVENTS_FILE):
        try:
            with open(EVENTS_FILE, "r", encoding="utf-8") as f:
                events = json.load(f)
        except:
            events = []
    events.insert(0, {"timestamp": now, "message": message})
    # Keep only last 50 events
    events = events[:50]
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

PERSONAS = [
    {"role": "HR Specialist", "focus": "Employee engagement, talent management, training"},
    {"role": "System Architect", "focus": "System integration, API, technical architecture, performance"},
    {"role": "Data Scientist", "focus": "Analytics, predictive models, data-driven insights"},
    {"role": "Financial Analyst", "focus": "Cost reduction, ROI optimization, billing systems"},
    {"role": "Sales & Marketing", "focus": "Customer acquisition, upselling, market positioning"},
    {"role": "Operations Manager", "focus": "Process automation, efficiency gains, workflow optimization"}
]

def load_ideas():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_ideas(ideas):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(ideas, f, indent=2, ensure_ascii=False)

MOCK_DATABASE = [
    {
        "role": "HR Specialist",
        "title": "評価プロセス可視化ダッシュボードの導入",
        "target": "既存顧客",
        "target_audience": "マネージャー・一般社員",
        "modules": "Performance & Goals",
        "approach": "【課題】評価面談時、期中の目標変更やフィードバックの経緯が不透明で従業員の不満に繋がる。\n\n【解決案】Performance & Goalsの標準レポート機能を拡張し、目標変更履歴と連続的フィードバック(CPM)のデータを一覧できるマネージャー向けダッシュボードを構築する。",
        "rationale": "評価の納得度低下という明確な人事課題を解決でき、既存顧客のモジュール活用度アップによるリテンション強化に直結する。",
        "viewpoint": "【HR Specialist見解】評価の納得感向上は離職防止の鍵です。標準機能の延長で実現できるため、ROIが非常に高い施策です。",
        "recommendation_score": 5,
        "schedule": [
            {"month": "Month 1", "phase": "課題アセスメント", "tasks": [
                {"name": "評価シートの現状分析", "duration": "1週間", "raci": "V: A,R / C: C", "dependency": "なし"},
                {"name": "マネージャー層への課題ヒアリング", "duration": "2週間", "raci": "V: C / C: A,R", "dependency": "分析完了後"}
            ]},
            {"month": "Month 2", "phase": "設計・構築", "tasks": [
                {"name": "ダッシュボード要件定義", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "Month 1完了"},
                {"name": "システム構築・レポート作成", "duration": "2週間", "raci": "V: A,R / C: I", "dependency": "要件定義承認後"}
            ]},
            {"month": "Month 3", "phase": "テスト・展開", "tasks": [
                {"name": "UAT（受入テスト）の実施", "duration": "2週間", "raci": "V: C / C: A,R", "dependency": "構築完了"},
                {"name": "説明会実施と全社展開", "duration": "2週間", "raci": "V: C / C: A,R", "dependency": "UAT完了後"}
            ]}
        ],
        "cost": "約150万円"
    },
    {
        "role": "System Architect",
        "title": "IDaaS連携による入退社プロセスの完全自動化",
        "target": "新規開拓",
        "target_audience": "情報システム部・人事運用部",
        "modules": "Employee Central",
        "approach": "【課題】入社時や異動時にアカウント付与が手作業で行われ、セキュリティリスクと業務遅延が発生。\n\n【解決案】Employee Centralをマスタとし、Azure ADやOkta(IDaaS)との自動同期API(SCIM)を設定する。",
        "rationale": "情報システム部と人事部の双方の工数を劇的に削減でき、セキュリティガバナンス強化という経営層の刺さる価値を提供できる。",
        "viewpoint": "【System Architect見解】初期の検証工数はかかりますが、稼働後の運用コスト削減効果は絶大です。情シス部門を巻き込むことで全社的な大型案件化が狙えます。",
        "recommendation_score": 4,
        "schedule": [
            {"month": "Month 1", "phase": "システム要件定義", "tasks": [
                {"name": "API連携方式・認証方式の策定", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "なし"},
                {"name": "権限マトリクスとマッピング定義", "duration": "2週間", "raci": "V: C / C: A,R", "dependency": "方式策定後"}
            ]},
            {"month": "Month 2", "phase": "SCIM連携実装", "tasks": [
                {"name": "Azure AD/Okta側の自動同期設定", "duration": "2週間", "raci": "V: A,R / C: I", "dependency": "Month 1完了"},
                {"name": "例外エラーハンドリング・ログ実装", "duration": "2週間", "raci": "V: A,R / C: I", "dependency": "同期設定完了後"}
            ]},
            {"month": "Month 3", "phase": "検証・移行", "tasks": [
                {"name": "テスト用ダミーデータでの結合テスト", "duration": "2週間", "raci": "V: A / C: R", "dependency": "実装完了"},
                {"name": "本番環境へのデプロイと情シス引き継ぎ", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "テスト完了後"}
            ]}
        ],
        "cost": "約400万円〜"
    },
    {
        "role": "Operations Manager",
        "title": "組織改編データ移行の事前バリデーションツール",
        "target": "既存顧客",
        "target_audience": "人事給与・労務実務担当者",
        "modules": "Employee Central",
        "approach": "【課題】大量のCSVインポートエラーで人事の残業が常態化。\n\n【解決案】インポート前にSuccessFactorsのデータ要件（必須項目・マスター整合性）をローカルで自動チェックするExcel/Webアプリを導入。",
        "rationale": "人事担当者のダイレクトなペインポイントを解消するため、成約率が極めて高い。",
        "viewpoint": "【Operations Manager見解】泥臭い課題への特効薬になります。導入期間が短く、素早い成功体験（Quick Win）を提供できるため強く推奨します。",
        "recommendation_score": 5,
        "schedule": [
            {"month": "Month 1", "phase": "仕様定義", "tasks": [
                {"name": "過去のエラーログ分析", "duration": "2週間", "raci": "V: A,R / C: I", "dependency": "なし"},
                {"name": "バリデーションルール一覧の策定", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "分析完了後"}
            ]},
            {"month": "Month 2", "phase": "開発・テスト", "tasks": [
                {"name": "チェックツールの実装", "duration": "2週間", "raci": "V: A,R / C: I", "dependency": "Month 1完了"},
                {"name": "過去データを用いた単体テスト", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "実装完了後"}
            ]},
            {"month": "Month 3", "phase": "実地運用", "tasks": [
                {"name": "次期組織改編データでのプレテスト", "duration": "2週間", "raci": "V: C / C: A,R", "dependency": "開発完了"},
                {"name": "操作マニュアル提供と運用開始", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "プレテスト完了後"}
            ]}
        ],
        "cost": "約100万円"
    },
    {
        "role": "Data Scientist",
        "title": "退職リスク予測モデルの実装",
        "target": "既存顧客",
        "target_audience": "経営層・CHRO・HRBP",
        "modules": "Employee Central, Performance & Goals",
        "approach": "【課題】キーパーソンの突然の退職を事前に察知できない。\n\n【解決案】SF内の給与・評価推移データを抽出し、機械学習で高リスク従業員をアラートするモデルを構築。",
        "rationale": "データドリブンな人事戦略の中核となり、高度な活用を望む層へアップセルしやすい。",
        "viewpoint": "【Data Scientist見解】データのクレンジングに顧客の協力が不可欠なため難易度は高いですが、実現時のインパクトは絶大です。",
        "recommendation_score": 3,
        "schedule": [
            {"month": "Month 1-2", "phase": "データ抽出・加工", "tasks": [
                {"name": "必要データセットの特定とマスク処理", "duration": "4週間", "raci": "V: C / C: A,R", "dependency": "なし"},
                {"name": "特徴量エンジニアリングと前処理", "duration": "4週間", "raci": "V: A,R / C: I", "dependency": "データ抽出完了後"}
            ]},
            {"month": "Month 3", "phase": "モデル構築", "tasks": [
                {"name": "機械学習モデルの学習および精度検証", "duration": "4週間", "raci": "V: A,R / C: C", "dependency": "前処理完了後"}
            ]},
            {"month": "Month 4", "phase": "ダッシュボード統合", "tasks": [
                {"name": "予測スコアのアラート画面への埋め込み", "duration": "2週間", "raci": "V: A,R / C: I", "dependency": "モデル完成後"},
                {"name": "HRBP向けアクションプラン策定支援", "duration": "2週間", "raci": "V: C / C: A,R", "dependency": "画面実装完了後"}
            ]}
        ],
        "cost": "約600万円"
    },
    {
        "role": "Sales & Marketing",
        "title": "内定者エンゲージメント向け専用ポータルのクイック導入",
        "target": "新規開拓",
        "target_audience": "採用担当者・内定者",
        "modules": "Onboarding",
        "approach": "【課題】内定承諾から入社までの辞退率が高い。\n\n【解決案】Onboardingを活用し、内定者専用のモバイルフレンドリーなポータルを短期構築する。",
        "rationale": "採用コスト削減という明確なROIを提示でき、ドアノック商材として強力。",
        "viewpoint": "【Sales & Marketing見解】パッケージ化しやすく、1ヶ月でのクイック導入を謳えるため、新規開拓の強力な武器になります。",
        "recommendation_score": 5,
        "schedule": [
            {"month": "Month 1", "phase": "ポータル設計", "tasks": [
                {"name": "ベストプラクティスUIの提示・選択", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "なし"},
                {"name": "掲載コンテンツ（動画等）の準備", "duration": "2週間", "raci": "V: I / C: A,R", "dependency": "UI決定後"}
            ]},
            {"month": "Month 2", "phase": "システム構築", "tasks": [
                {"name": "Onboardingモジュール初期設定", "duration": "3週間", "raci": "V: A,R / C: I", "dependency": "Month 1完了"},
                {"name": "コンテンツ登録・リンク設定", "duration": "1週間", "raci": "V: R / C: A", "dependency": "初期設定完了後"}
            ]},
            {"month": "Month 3", "phase": "公開検証", "tasks": [
                {"name": "モバイル端末・PCでの表示テスト", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "構築完了後"},
                {"name": "内定者向け運用マニュアル展開・公開", "duration": "2週間", "raci": "V: C / C: A,R", "dependency": "テスト完了後"}
            ]}
        ],
        "cost": "約250万円"
    },
    {
        "role": "HR Specialist",
        "title": "スキルオントロジーとLMSの自動連携",
        "target": "新規開拓",
        "target_audience": "人材開発部門・全従業員",
        "modules": "Learning, Succession & Development",
        "approach": "【課題】従業員がキャリアパスに必要なスキルを把握できずLMSが受講されない。\n\n【解決案】職務定義のスキル要件と連携し、不足スキルを補うLearningコースを自動リコメンドする。",
        "rationale": "リスキリングトレンドに合致し、Learningのライセンス販売に直結する。",
        "viewpoint": "【HR Specialist見解】コースの紐付け作業は顧客にも大きな負担を強いるため、PMOとしての手腕が問われます。価値は高いです。",
        "recommendation_score": 4,
        "schedule": [
            {"month": "Month 1", "phase": "スキル定義", "tasks": [
                {"name": "コア職務のレベル別要件定義", "duration": "4週間", "raci": "V: C / C: A,R", "dependency": "なし"}
            ]},
            {"month": "Month 2", "phase": "マッピング", "tasks": [
                {"name": "既存LMSコンテンツの棚卸し", "duration": "2週間", "raci": "V: I / C: A,R", "dependency": "Month 1完了"},
                {"name": "スキルタグとの紐付け設定", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "棚卸し完了後"}
            ]},
            {"month": "Month 3", "phase": "トライアル運用", "tasks": [
                {"name": "パイロット部門でのレコメンド検証", "duration": "2週間", "raci": "V: C / C: A,R", "dependency": "マッピング完了"},
                {"name": "全社向けのキャリア自律方針発信", "duration": "2週間", "raci": "V: I / C: A,R", "dependency": "検証完了後"}
            ]}
        ],
        "cost": "約450万円"
    },
    {
        "role": "Financial Analyst",
        "title": "ライセンス使用率分析とコスト最適化ツール",
        "target": "既存顧客",
        "target_audience": "経営企画・CFO・情報システム",
        "modules": "Platform (Foundation)",
        "approach": "【課題】退職者の残存アカウント等により無駄なライセンス費用が発生している。\n\n【解決案】利用頻度や最終ログイン日をAPIで自動抽出し、不要ライセンスを特定するレポートを提供する。",
        "rationale": "SaaSのコスト最適化はCFOの関心事であり、浮いた予算を別Add-onに回せる。",
        "viewpoint": "【Financial Analyst見解】ROIが最も数値化しやすく、役員レイヤーの予算決裁を容易に引き出せます。必須の提案です。",
        "recommendation_score": 5,
        "schedule": [
            {"month": "Month 1", "phase": "現状把握", "tasks": [
                {"name": "ライセンス契約状況とログイン状況の抽出", "duration": "4週間", "raci": "V: A,R / C: C", "dependency": "なし"}
            ]},
            {"month": "Month 2", "phase": "分析・試算", "tasks": [
                {"name": "休眠アカウントのリストアップ分析", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "Month 1完了"},
                {"name": "アカウント停止要否の判定とコスト試算", "duration": "2週間", "raci": "V: C / C: A,R", "dependency": "リストアップ完了後"}
            ]},
            {"month": "Month 3", "phase": "クリーンアップ", "tasks": [
                {"name": "不要アカウントの無効化処理", "duration": "2週間", "raci": "V: A / C: R", "dependency": "判定完了"},
                {"name": "効果測定レポートの提出", "duration": "2週間", "raci": "V: A,R / C: I", "dependency": "無効化完了後"}
            ]}
        ],
        "cost": "約80万円"
    },
    {
        "role": "System Architect",
        "title": "給与計算システム向け双方向APIハブ",
        "target": "既存顧客",
        "target_audience": "給与・労務担当者、IT部門",
        "modules": "Employee Central",
        "approach": "【課題】国内給与（ COMPANY等）との連携が手動CSVでミスが多い。\n\n【解決案】BTP (Integration Suite) を介してECのマスター変更を特定し、給与システムへ自動マッピング連携する。",
        "rationale": "給与自動化は人事給与チームの悲願であり、高額なSI案件として受注しやすい。",
        "viewpoint": "【System Architect見解】一度導入するとリプレイスされにくくなる強力なロックイン効果があります。BTPの主要ユースケースです。",
        "recommendation_score": 5,
        "schedule": [
            {"month": "Month 1", "phase": "マッピング定義", "tasks": [
                {"name": "国内給与システムのインターフェース仕様確認", "duration": "2週間", "raci": "V: C / C: A,R", "dependency": "なし"},
                {"name": "EC項目のデータマッピング・変換仕様定義", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "仕様確認後"}
            ]},
            {"month": "Month 2-3", "phase": "BTP開発", "tasks": [
                {"name": "Integration Flowの開発と暗号化設定", "duration": "6週間", "raci": "V: A,R / C: I", "dependency": "定義完了後"},
                {"name": "検証用ペイロール環境でのダミーデータ連携テスト", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "開発完了後"}
            ]},
            {"month": "Month 4", "phase": "並行稼働", "tasks": [
                {"name": "旧新システムでの結果突合テスト（並行稼働）", "duration": "4週間", "raci": "V: C / C: A,R", "dependency": "連携テスト完了後"}
            ]}
        ],
        "cost": "約800万円〜"
    },
    {
        "role": "Operations Manager",
        "title": "自動面接スケジュール調整Bot",
        "target": "新規開拓",
        "target_audience": "採用担当者・面接官",
        "modules": "Recruiting",
        "approach": "【課題】候補者と面接官のOutlook予定表のすり合わせが手動で発生。\n\n【解決案】Recruitingのステータス変更をトリガーにし、Microsoft Graph API経由で空き時間を自動抽出・送信する。",
        "rationale": "採用担当の業務負担を半減させる特効薬。",
        "viewpoint": "【Operations Manager見解】機能としては単一ですが、Outlook連携は全社セキュリティ審査がボトルネックになるリスクがあります。事前確認が必須。",
        "recommendation_score": 3,
        "schedule": [
            {"month": "Month 1", "phase": "API仕様定義", "tasks": [
                {"name": "O365とのセキュリティ確認とWebHook設計", "duration": "3週間", "raci": "V: C / C: A,R", "dependency": "なし"},
                {"name": "面接フローのプロセス定義", "duration": "1週間", "raci": "V: C / C: A,R", "dependency": "なし"}
            ]},
            {"month": "Month 2", "phase": "Bot開発", "tasks": [
                {"name": "空き時間抽出・調整ロジック実装", "duration": "3週間", "raci": "V: A,R / C: I", "dependency": "Month 1完了"},
                {"name": "テスト候補者を用いた受入テスト", "duration": "1週間", "raci": "V: C / C: A,R", "dependency": "実装完了後"}
            ]},
            {"month": "Month 3", "phase": "運用切り替え", "tasks": [
                {"name": "本番デプロイとエラーモニタリング", "duration": "2週間", "raci": "V: A,R / C: I", "dependency": "受入テスト完了"},
                {"name": "現場担当者への新フロー周知", "duration": "2週間", "raci": "V: I / C: A,R", "dependency": "デプロイ完了"}
            ]}
        ],
        "cost": "約350万円"
    },
    {
        "role": "Data Scientist",
        "title": "AI面接官による初期スクリーニング補助",
        "target": "新規開拓",
        "target_audience": "採用担当者・部門長",
        "modules": "Recruiting",
        "approach": "【課題】大量のエントリーシートの評価基準がブレて人事工数が圧迫される。\n\n【解決案】レジュメテキストと過去実績をLLMで解析しマッチ度を事前スコアリングするアドオン。",
        "rationale": "生成AI技術をエンタープライズHRに組み込む先進事例としてブランディングに貢献。",
        "viewpoint": "【Data Scientist見解】LLMのハルシネーションリスクやバイアス制御等の課題はありますが、先進性アピールとしては最強の商材です。",
        "recommendation_score": 4,
        "schedule": [
            {"month": "Month 1", "phase": "PoC", "tasks": [
                {"name": "コンピテンシー定義と過去データ抽出", "duration": "3週間", "raci": "V: C / C: A,R", "dependency": "なし"},
                {"name": "LLMプロンプトの基礎構築", "duration": "1週間", "raci": "V: A,R / C: I", "dependency": "データ抽出完了後"}
            ]},
            {"month": "Month 2", "phase": "システム結合", "tasks": [
                {"name": "SF RecruitingとのAPI連携実装", "duration": "2週間", "raci": "V: A,R / C: I", "dependency": "Month 1完了"},
                {"name": "実際の応募データを用いたスコア妥当性検証", "duration": "2週間", "raci": "V: C / C: A,R", "dependency": "連携完了後"}
            ]},
            {"month": "Month 3", "phase": "実運用", "tasks": [
                {"name": "バイアスチェックと本番リリース", "duration": "2週間", "raci": "V: A,R / C: C", "dependency": "妥当性検証完了"},
                {"name": "面接官向けの見方ガイド展開と運用開始", "duration": "2週間", "raci": "V: C / C: A,R", "dependency": "リリース後"}
            ]}
        ],
        "cost": "約500万円"
    }
]

# Keep track of which mock IDs we have used so we don't duplicate
USED_MOCK_TITLES = set()

def generate_idea_mock(persona):
    now = datetime.now(timezone.utc).isoformat()
    idea_id = str(uuid.uuid4())
    
    # Extract only available unseen templates
    available_templates = [t for t in MOCK_DATABASE if t["title"] not in USED_MOCK_TITLES]
    
    # If we somehow run out, just reset
    if not available_templates:
        USED_MOCK_TITLES.clear()
        available_templates = MOCK_DATABASE

    # Try to find one matching the persona
    persona_templates = [t for t in available_templates if t["role"] == persona["role"]]
    if persona_templates:
        base = random.choice(persona_templates)
    else:
        # Fallback to any available if the chosen persona has used all theirs
        base = random.choice(available_templates)

    USED_MOCK_TITLES.add(base["title"])

    return {
        "id": idea_id,
        "persona": base["role"],
        "title": base["title"],
        "target": base["target"],
        "modules": base["modules"],
        "approach": base["approach"],
        "rationale": base["rationale"],
        "schedule": base["schedule"],
        "difficulty": base.get("difficulty", random.choice([
            "低難易度（既存設定の応用のみで完結するため）",
            "中難易度（一部アドオン開発やAPI連携が必要なため）",
            "高難易度（要件定義での利害調整が難航しやすいため）",
            "高難易度（全社的な業務フロー是正が伴うため）"
        ])),
        "reference": base.get("reference", "https://help.sap.com/docs/SAP_SUCCESSFACTORS_RELEASE_INFORMATION"),
        "recommendation_score": base.get("recommendation_score", random.randint(3, 5)),
        "cost": base["cost"],
        "created_at": now,
        "updated_at": now
    }

def generate_idea_ai(persona):
    now = datetime.now(timezone.utc).isoformat()
    try:
        prompt = f"""
あなたは '{persona['focus']}' を専門とする '{persona['role']}' として振る舞います。
目的は、SuccessFactorsのサービス提供を再活性化し、より収益性の高い斬新なアイデアを提案することです。

【重要条件】
- 「知見を活かす」等の抽象的な表現は避け、**実際に企業で起きている具体的な業務課題や、導入済みモジュールでよく起きがちなトラブル**をベースにしてください。
- 課題に対する具体的な改善案、またはFit to Standardを推進するためのアプローチを記載してください。
- SuccessFactors単体だけでなく、周辺システムとの連携も含めて構いません。

以下のキーを持つJSONブロックのみを出力してください。言語は必ず**日本語**で記述してください。
- "title": アイデアのキャッチーなタイトル
- "target": 対象顧客（「新規開拓」または「既存顧客の活用支援」のどちらを主目的とするか明記）
- "modules": 活用するSuccessFactorsのモジュール名（例: Employee Central, Recruiting, Performance & Goalsなど）
- "approach": どのような業務のFitを目指すか、またはよくあるトラブルに対しどう改善するかという、具体的なアプローチと解決策
- "rationale": なぜこのアイデアが顧客に刺さり、自社の収益獲得に繋がるのか、その根拠
- "viewpoint": 提案者としてのあなた（{persona['role']}）からのアピールポイントや見解を簡潔に（例: "【〇〇の見解】..."）
- "difficulty": そのアイディアの技術的・調整的な面での短・中・高の難易度と具体的な理由（例の単なるコピーはせず、各アイディアの特性に合わせた独自の難易度と理由を必ず生み出すこと）
- "reference": 参考ソースのURL（例: SAP Help Portalや関連する技術情報などのURL。なければ一般的なSAPのURL）
- "recommendation_score": 1〜5の整数でターゲット企業へのおすすめ度（優先度）を示す。
- "schedule": 導入スケジュールの配列。各要素は {{"phase": "フェーズ名", "actor": "ベンダー/顧客/全体", "name": "タスク名", "duration": "期間（例: 2週間）", "dependency": "依存関係"}} を含むこと。
- "cost": 想定される必要コスト（例: "約300万円", "中コスト（約3ヶ月の開発）"）

JSONのフォーマットは厳密に守ってください。Markdownのコードブロックは使用しないでください。
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        
        data = json.loads(response.text)
        idea_id = str(uuid.uuid4())
        return {
            "id": idea_id,
            "persona": persona["role"],
            "title": data.get("title", f"Idea by {persona['role']}"),
            "target": data.get("target", "未定"),
            "modules": data.get("modules", "未定"),
            "approach": data.get("approach", ""),
            "rationale": data.get("rationale", ""),
            "viewpoint": data.get("viewpoint", f"【{persona['role']}からの提案アピール】このアイディアは強力なROIを提供します。"),
            "difficulty": data.get("difficulty", "未定"),
            "reference": data.get("reference", ""),
            "recommendation_score": data.get("recommendation_score", 3),
            "schedule": data.get("schedule", {}),
            "cost": data.get("cost", ""),
            "created_at": now,
            "updated_at": now
        }
    except Exception as e:
        print(f"Failed to generate AI idea: {e}")
        return generate_idea_mock(persona)

def update_idea_ai(idea, reviewer_persona=None):
    now = datetime.now(timezone.utc).isoformat()
    try:
        reviewer_intro = ""
        if reviewer_persona and reviewer_persona['role'] != idea['persona']:
            reviewer_intro = f"\nあなたは '{reviewer_persona['focus']}' を専門とする '{reviewer_persona['role']}' として、このアイディアをレビューする立場にあります。専門家の視点から厳しく指摘し、プランをアップデートしてください。"
            
        prompt = f"""
以下のビジネスアイデア（提案者: {idea['persona']}）をさらに魅力的に改善・拡張してください。{reviewer_intro}
タイトル: {idea['title']}
対象: {idea.get('target', '未定')}
モジュール: {idea.get('modules', '未定')}
アプローチ: {idea['approach']}
根拠: {idea['rationale']}

アイデアを少しブラッシュアップしてください。抽象的な表現を避け、具体的なトラブル事例や業務課題（Fit to Standardの課題など）により深くフォーカスした詳細をアプローチ部分に追記してください。
また、あなたのレビュー結果を反映し、難易度（difficulty）も必要に応じて再評価・説明を付加してください。
言語は必ず**日本語**で記述してください。
以下のキーを含むJSONブロックのみを出力してください:
- "title"
- "target"
- "modules"
- "approach"
- "rationale"
- "viewpoint" (既存のものがあれば保持)
- "review_comment" (今回のあなたのレビューや事前指摘、追加アピールポイントを簡潔に記載してください)
- "difficulty"
- "reference"
- "recommendation_score" (1〜5の整数で再評価)
- "schedule" (以前のスケジュール形式を維持しつつ調整)
- "cost"
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        data = json.loads(response.text)
        idea["title"] = data.get("title", idea["title"])
        idea["target"] = data.get("target", idea.get("target"))
        idea["modules"] = data.get("modules", idea.get("modules"))
        idea["approach"] = data.get("approach", idea["approach"])
        idea["rationale"] = data.get("rationale", idea["rationale"])
        idea["viewpoint"] = data.get("viewpoint", idea.get("viewpoint", ""))
        idea["review_comment"] = data.get("review_comment", idea.get("review_comment", ""))
        idea["difficulty"] = data.get("difficulty", idea.get("difficulty", ""))
        idea["reference"] = data.get("reference", idea.get("reference", ""))
        idea["recommendation_score"] = data.get("recommendation_score", idea.get("recommendation_score", 3))
        idea["schedule"] = data.get("schedule", idea.get("schedule", {}))
        idea["cost"] = data.get("cost", idea["cost"])
        idea["updated_at"] = now
        return idea
    except Exception as e:
        return update_idea_mock(idea, reviewer_persona)

def update_idea_mock(idea, reviewer_persona=None):
    now = datetime.now(timezone.utc).isoformat()
    details = [
        "更に、BTP(Business Technology Platform)を活用したモバイル承認フローをアドオンで提供することも視野に入れる。",
        "導入後の定着化（チェンジマネジメント）として、現場向けのマニュアル動画作成支援もパッケージに含める。",
        "カスタマーサクセスチームと連携し、稼働後3ヶ月間はKPIモニタリングを無償提供して満足度を高める。"
    ]
    
    reviewer_prefix = "追加検討"
    if reviewer_persona and reviewer_persona['role'] != idea['persona']:
        reviewer_prefix = f"{reviewer_persona['role']}からの指摘"
        
    idea["review_comment"] = f"{reviewer_prefix}: {random.choice(details)}"
    idea["recommendation_score"] = min(5, idea.get("recommendation_score", 3) + random.choice([0, 1]))
    idea["updated_at"] = now
    return idea

async def run_ai_simulation():
    log_event("AIシミュレーションを開始しました。")
    print(f"Starting AI Simulation loop. USE_AI: {USE_AI}")
    while True:
        try:
            ideas = load_ideas()
            
            # Deduplicate by title (keep newest) and cull low priority
            ideas.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            unique_titles = set()
            filtered_ideas = []
            for item in ideas:
                score = item.get("recommendation_score", 3)
                title = item.get("title", "")
                if score >= 4 and title not in unique_titles:
                    unique_titles.add(title)
                    filtered_ideas.append(item)
            
            ideas = filtered_ideas
            
            MAX_IDEAS = 25
            action = "generate"
            if len(ideas) >= MAX_IDEAS:
                action = random.choice(["replace", "update", "update", "update"])
            elif len(ideas) >= 15:
                action = random.choice(["generate", "update", "update"])
                
            if action in ["generate", "replace"]:
                persona = random.choice(PERSONAS)
                
                if action == "replace" or len(ideas) >= MAX_IDEAS:
                    # Sort primarily by score ascending, secondarily by updated_at ascending (oldest score first)
                    ideas.sort(key=lambda x: (x.get("recommendation_score", 4), x.get("updated_at", "")))
                    if ideas:
                        removed = ideas.pop(0)
                        log_event(f"【System】優先度の低いアイディア「{removed['title']}」を破棄し、整理しました。")
                        await asyncio.sleep(1)

                print(f"AI Worker: Generating new idea as {persona['role']}...")
                log_event(f"【{persona['role']}】が新規アイディアを考案中です...")
                
                # simulate thinking
                await asyncio.sleep(2)
                
                if USE_AI:
                    new_idea = generate_idea_ai(persona)
                else:
                    new_idea = generate_idea_mock(persona)
                ideas.insert(0, new_idea)
                save_ideas(ideas)
                log_event(f"【{persona['role']}】が新しいアイディア「{new_idea['title']}」を提出しました！")
            else:
                if ideas:
                    ideas.sort(key=lambda x: x.get("updated_at", ""))
                    target_idea = ideas[0]
                    persona_role = target_idea['persona']
                    
                    possible_reviewers = [p for p in PERSONAS if p['role'] != persona_role]
                    reviewer_persona = random.choice(possible_reviewers) if possible_reviewers else persona_role
                    reviewer_role = reviewer_persona['role'] if isinstance(reviewer_persona, dict) else reviewer_persona

                    print(f"AI Worker: {reviewer_role} is reviewing idea '{target_idea['title']}'...")
                    
                    log_event(f"【{reviewer_role}】が【{persona_role}】のアイディア「{target_idea['title']}」をレビューしています...")
                    await asyncio.sleep(2)
                    
                    if USE_AI:
                        target_idea = update_idea_ai(target_idea, reviewer_persona)
                    else:
                        target_idea = update_idea_mock(target_idea, reviewer_persona)
                    save_ideas(ideas)
                    log_event(f"【{reviewer_role}】がレビューを反映し、プランがアップデートされました！")
                    
            await asyncio.sleep(random.randint(10, 20))
        except Exception as e:
            print(f"Error in AI loop: {e}")
            await asyncio.sleep(10)
