from fastapi import FastAPI, HTTPException, Body
from models import ParticipantRequest, SearchResponse
from agents import AggregationAgent, SearchAgent, SummaryAgent
from dotenv import load_dotenv
import os
from typing import List

from models import ShopInfo

# .envファイルから環境変数を読み込む
load_dotenv()

app = FastAPI(
    title="AI Multi-Agent Restaurant Search API",
    description="3つのAIエージェントが連携して、複数人の要望からお店を提案するAPI",
    version="1.1.0"
)

# 環境変数のチェック
if not os.getenv("GCP_PROJECT_ID") or not os.getenv("GCP_LOCATION"):
    raise RuntimeError("GCP_PROJECT_ID and GCP_LOCATION must be set in .env file")

@app.post("/search", response_model=SearchResponse)
async def search_restaurants(requests: List[ParticipantRequest] = Body(...)):
    """
    複数参加者のお店の検索要望を受け取り、AIが選んだお店情報を返す。
    """
    if not requests:
        raise HTTPException(status_code=400, detail="リクエストボディが空です。")

    try:
        print(f"Received requests: {requests}")
        # 1. 集約エージェントが、検索条件のパターンを生成
        aggregation_agent = AggregationAgent()
        search_patterns = aggregation_agent.run(requests)

        if not search_patterns:
            raise HTTPException(status_code=500, detail="検索条件の生成に失敗しました。")
        
        print(f"Generated search patterns: {search_patterns}")

        # 2. 各検索パターンで、検索・要約エージェントを並行して実行
        all_found_shops = []
        search_agent = SearchAgent()
        summary_agent = SummaryAgent()

        for pattern in search_patterns:
            # 2a. 検索エージェントがWeb検索を実行
            web_search_result = search_agent.run(pattern)

            print(f"Web search result for pattern {pattern}: {web_search_result}")
            
            if "見つかりませんでした" in web_search_result:
                continue

            # 2b. 要約エージェントが結果を整形
            shops = summary_agent.run(web_search_result, theme=pattern.theme)
            print(f"Formatted shops for pattern {pattern}: {shops}")
            all_found_shops.extend(shops)

        # 3. 結果をマージし、重複を排除して最終的なレスポンスを作成
        unique_shops = []
        seen_shop_names = set()
        for shop in all_found_shops:
            if shop.name not in seen_shop_names:
                unique_shops.append(shop)
                seen_shop_names.add(shop.name)
        
        if not unique_shops:
            raise HTTPException(status_code=404, detail="全ての検索パターンで、条件に合う店舗が見つかりませんでした。")

        # 最終的に返す件数を3件に絞る
        final_shops = unique_shops

        return SearchResponse(shops=final_shops)

    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

# ローカルでテスト実行するためのコード
# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.getenv("PORT", 8080))
#     uvicorn.run(app, host="0.0.0.0", port=port)