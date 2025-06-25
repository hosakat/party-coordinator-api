from pydantic import BaseModel, Field
from typing import List, Optional

# --- 追加: 参加者一人の要望を表すモデル ---
class ParticipantRequest(BaseModel):
    group_id: str = Field(..., alias="groupId", description="リクエストをまとめるためのグループID")
    member_name: str = Field(..., alias="memberName", description="参加者の名前")
    station: str = Field(..., description="希望の最寄り駅")
    request: str = Field(..., description="お店選びに関する自由記述の要望")
    allergy: Optional[str] = Field(None, description="アレルギー情報（カンマ区切りなど）")
    min_price: Optional[str] = Field(None, alias="minPrice", description="最低予算（文字列）")
    max_price: Optional[str] = Field(None, alias="maxPrice", description="最高予算（文字列）")

    class Config:
        populate_by_name = True # alias (groupIdなど) でデータを受け取れるようにする

# --- 変更なし: AIエージェントに渡すための内部モデル ---
# 複数の参加者の要望を集約した結果をこのモデルに入れる
# class IntegratedRequest(BaseModel):
#     station: str = Field(..., description="検索の基準となる最寄り駅")
#     allergies: List[str] = Field(default_factory=list, description="全員分を考慮したアレルギーリスト")
#     budget_yen: Optional[int] = Field(None, description="全員が許容できる共通の予算")
#     other_requests: str = Field(..., description="全員の要望をまとめたテキスト")

# --- 更新: 集約エージェントが生成する検索条件のモデル ---
class IntegratedRequest(BaseModel):
    """集約エージェントによって生成される、単一の検索条件パターン"""
    theme: str = Field(..., description="この検索パターンのテーマやコンセプト（例：『全員満足の和食コース』プラン）")
    station: str = Field(..., description="検索の基準となる最寄り駅")
    budget_yen: Optional[int] = Field(None, description="全員が許容できる共通の予算")
    keywords: str = Field(..., description="店選びのための具体的なキーワード（例：『渋谷 和食 個室 日本酒』）")
    allergies: List[str] = Field(default_factory=list, description="全員分を考慮したアレルギーリスト")

# --- 変更なし: レスポンスモデル ---
class ShopInfo(BaseModel):
    name: str = Field(..., description="店名")
    station: str = Field(..., description="最寄り駅")
    budget: str = Field(..., description="価格帯の目安（例: 3,000円〜4,000円）")
    summary: str = Field(..., description="お店の特徴を踏まえたおすすめの一言")
    mapUrl: Optional[str] = Field(None, description="GoogleマップのURL")

class SearchResponse(BaseModel):
    shops: List[ShopInfo]