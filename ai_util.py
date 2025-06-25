import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- 環境変数とモデルの初期化 ---
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
LOCATION = os.environ.get("GCP_LOCATION")

client = genai.Client(
    # project_id=PROJECT_ID,
    # location=LOCATION,
    vertexai=True
)

common_config = {
        "project": "qumoa-genai-09-project",
        # "location": "asia-northeast1",
        "location": "us-central1",
        "tempelature": 0.1,
        "top_p": 0.4,
        "top_k": 10,
        "max_output_tokens": 65535,  # gemini-2.5-pro-preview-03-25モデル
        # "model": "gemini-1.5-pro-002",
        # "model": "gemini-2.0-flash-001",
        # "model": "gemini-2.5-pro-preview-03-25",
        "model": "gemini-2.5-pro-preview-05-06"
    }

aggregation_agent_config = types.GenerateContentConfig(
    temperature=common_config.temperature,
    top_p=common_config.top_p,
    top_k=common_config.top_k,
    # max_output_tokens=8192,
    max_output_tokens=common_config.max_output_tokens, # gemini-2.5-pro-preview-03-25モデル
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
    system_instruction=[types.Part.from_text(text=system_prompt)],
    response_mime_type= "application/json",
)

def generate_ai_response(user_text, generate_content_config):
    """
    Vertex AIを使用してAIレスポンスを生成する関数

    Args:
        user_text (str): ユーザーからの入力テキスト
        system_prompt (str): システムプロンプト

    Returns:
        str: AIからの応答テキスト
    """
    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=user_text)]),
    ]

    response = client.models.generate_content(
        model=common_config.model,
        contents=contents,
        config=generate_content_config,
    )

    return response.text