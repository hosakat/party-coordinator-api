import os
import json
# from vertexai.generative_models import GenerativeModel, Tool, grounding
from models import ParticipantRequest, IntegratedRequest, ShopInfo
from tool_definitions import search_web
from typing import List
from google import genai
from dotenv import load_dotenv
from google.genai import types

# .envファイルを読み込む
load_dotenv()

# --- 環境変数とモデルの初期化 ---
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")

# デバッグ用に値を確認
print(f"Using Project ID: {PROJECT_ID}")
print(f"Using Location: {LOCATION}")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./party-coordinator-462715.json"

# # 通常のモデル
# model = GenerativeModel("gemini-1.5-pro-001")
# # Function Calling用のモデル
# function_calling_model = GenerativeModel(
#     "gemini-1.5-pro-001",
#     tools=[Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())]
# )
# # JSON出力用のモデル
# json_model = GenerativeModel(
#     "gemini-1.5-pro-001",
#     generation_config={"response_mime_type": "application/json"}
# )

client = genai.Client(
    project=PROJECT_ID,
    location=LOCATION,
    # vertexai=True
)

common_config = {
    # "location": "asia-northeast1",
    "location": "us-central1",
    "temperature": 0.1,
    "top_p": 0.4,
    "top_k": 10,
    "max_output_tokens": 65535,  # gemini-2.5-pro-preview-03-25モデル
    # "model": "gemini-1.5-pro-002",
    # "model": "gemini-2.0-flash-001",
    # "model": "gemini-2.5-pro-preview-03-25",
    "model": "gemini-2.5-pro"
}

aggregation_agent_config = types.GenerateContentConfig(
    temperature=common_config["temperature"],
    top_p=common_config["top_p"],
    top_k=common_config["top_k"],
    max_output_tokens=common_config["max_output_tokens"],
    response_modalities=["TEXT"],
    safety_settings=[
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
        ),
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
    ],
    # tools=tools,
    system_instruction=[types.Part.from_text(text="あなたは有能な飲み会幹事として有名です。全員が満足できる飲み会の幹事として、参加者の要望をうまく集約することが上手いです。")],
    response_mime_type= "application/json",
)

search_agent_config = types.GenerateContentConfig(
    temperature=common_config["temperature"],
    top_p=common_config["top_p"],
    top_k=common_config["top_k"],
    max_output_tokens=common_config["max_output_tokens"], # gemini-2.5-pro-preview-03-25モデル
    response_modalities=["TEXT"],
    safety_settings=[
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
        ),
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
    ],
    tools=[types.Tool(
        google_search=types.GoogleSearch()
    )],
    system_instruction=[types.Part.from_text(text="あなたは飲み会の幹事として、参加者の要望に合う飲食店を見つけるためにGoogle検索を駆使して粘り強く、最高のお店を見つけてください。")],
)

summary_agent_config = types.GenerateContentConfig(
    temperature=common_config["temperature"],
    top_p=common_config["top_p"],
    top_k=common_config["top_k"],
    max_output_tokens=common_config["max_output_tokens"], # gemini-2.5-pro-preview-03-25モデル
    response_modalities=["TEXT"],
    safety_settings=[
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
        ),
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
    ],
    # tools=tools,
    system_instruction=[types.Part.from_text(text="あなたは飲食店の有名なマーケターとして人が興味をそそられるようなキャッチコピーやPR文を書くのが得意です。飲食店の情報を魅力的に要約し、特定のテーマに合ったおすすめコメントを生成することができます。")],
    response_mime_type= "application/json",
)

def generate_ai_response(user_text, generate_content_config):
    """
    Vertex AIを使用してAIレスポンスを生成する関数

    Args:
        user_text (str): ユーザーからの入力テキスト
        generate_content_config (types.GenerateContentConfig): コンテンツ生成の設定

    Returns:
        str: AIからの応答テキスト
    """
    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=user_text)]),
    ]

    response = client.models.generate_content(
        model=common_config["model"],
        contents=contents,
        config=generate_content_config,
    )

    return response.text



class AggregationAgent:
    """参加者の要望を分析し、複数の検索パターンを生成するエージェント"""

    def run(self, requests: List[ParticipantRequest]) -> List[IntegratedRequest]:
        participants_summary = "\n".join([
            f"- {req.member_name} (予算: {req.min_price or '指定なし'}円〜{req.max_price or '指定なし'}円, アレルギー: {req.allergy or 'なし'}), 最寄り駅: {req.station},要望: {req.request}"
            for req in requests
        ])

        # AIに出力させたいJSONのスキーマを指定
        output_schema = {"type": "array", "items": IntegratedRequest.model_json_schema()}

        prompt = f"""
        あなたは優秀な飲み会の幹事です。以下の複数人の要望を分析し、全員が満足できそうなお店の検索条件を1〜3パターン提案してください。
        相反する要望がある場合は、うまくバランスを取るか、それぞれが主役になるような別のパターンとして分けて提案してください。
        開催場所は各々の最寄り駅を基準にし、距離だけでなく交通の便も考慮して全員が集まりやすく、かつ飲食店が多い場所を選んでください。
        予算は全員が許容できる共通の範囲を考慮してください。少し高めの予算でも、全員が満足できる内容であれば許容されることを念頭に置いてください。
        各パターンは、指定されたJSONスキーマに従って生成してください。

        # 参加者の要望リスト
        {participants_summary}

        # 出力JSONスキーマ
        {json.dumps(output_schema, indent=2)}
        """

        print("--- AggregationAgent実行中 ---")
        # response = json_model.generate_content(prompt)
        response =  generate_ai_response(prompt, aggregation_agent_config)
        
        try:
            patterns_data = json.loads(response)
            return [IntegratedRequest.model_validate(p) for p in patterns_data]
        except (json.JSONDecodeError, TypeError) as e:
            print(f"集約エージェントのJSONパースに失敗しました: {e}")
            return []


class SearchAgent:
    """生成された検索パターンに基づきWeb検索を実行するエージェント"""

    def run(self, request: IntegratedRequest) -> str:
        prompt = f"""
        以下の検索条件に最も合う飲食店を探すため、Google検索グラウンディングとGoogle Mapグラウンディングを使用して、検索してください。
        検索した結果、良いと思うお店を最大2軒まで選んでください。
        可能であれば、GoogleマップのURLも取得してください。取得するのであれば、必ず正しいものを取得してください。
        検索クエリは、keywordsを元に、具体的で効果的なものにしてください。

        # 検索条件
        - テーマ: {request.theme}
        - エリア: {request.station}
        - 予算: {request.budget_yen}円以下
        - キーワード: {request.keywords}
        - 必須アレルギー対応: {', '.join(request.allergies) if request.allergies else 'なし'}

        # 検索結果
        - 店名
        - 最寄り駅
        - 価格帯の目安
        - お店の特徴
        - GoogleマップのURL（可能であれば） 
        - この店を選ぶ理由（「{request.theme}」に合う点を強調）

        これ以外の情報は出力に必要ありません。
        """
        
        print(f"--- SearchAgent実行中 (テーマ: {request.theme}) ---")
        
        try:
            response = generate_ai_response(prompt, search_agent_config)
        
            # tool_call = response.candidates[0].content.parts[0].function_call
            # if tool_call.name == "search_web":
            #     tool_response = search_web(query=tool_call.args["query"])
            return response
        except (IndexError, AttributeError) as e:
             print(f"Function Callingの実行に失敗しました: {e}")

        return f"「{request.theme}」に合うお店は見つかりませんでした。"

class SummaryAgent:
    """検索結果を整形し、おすすめコメントを生成するエージェント"""

    def run(self, web_search_result: str, theme: str) -> list[ShopInfo]:
        shop_info_schema = ShopInfo.model_json_schema()

        prompt = f"""
        以下のWeb検索結果テキストから、お店の情報を抽出し、指定のJSONスキーマに従って情報を要約してください。
        `summary`には、お店の特徴と、今回の検索テーマである「{theme}」を考慮した、魅力的なおすすめの一言を生成してください。
        最大3店舗まで選んでください。

        # JSONスキーマ
        {json.dumps(shop_info_schema)}

        # Web検索結果
        {web_search_result}
        """

        print("--- SummaryAgent実行中 ---")
        response =  generate_ai_response(prompt, summary_agent_config)
        
        try:
            # AIがリストを返すか、単一のオブジェクトを返すか、キーを持つオブジェクトを返すか、柔軟に対応
            response_data = json.loads(response)
            
            if isinstance(response_data, dict):
                # {"shops": [...]} のような形式を想定
                shop_list_data = response_data.get("shops", [])
            elif isinstance(response_data, list):
                # [...] のようなリスト形式を想定
                shop_list_data = response_data
            else:
                print(f"要約エージェントでデータの抽出に失敗しました。")
                shop_list_data = []

            return [ShopInfo.model_validate(shop) for shop in shop_list_data]
        except (json.JSONDecodeError, TypeError) as e:
            print(f"要約エージェントのJSONパースに失敗しました: {e}")
            return []