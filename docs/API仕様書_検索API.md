# API 仕様書

## API 名

AI Multi-Agent 飲食店検索 API

## URL パス

`/search`

## メソッド

`POST`

## リクエスト

### リクエストボディ項目

| 論理名     | 物理名     | 型          | 説明                             |
| ---------- | ---------- | ----------- | -------------------------------- |
| 参加者名   | memberName | string      | 参加者の名前                     |
| 最寄り駅   | station    | string      | 希望の最寄り駅                   |
| 要望       | request    | string      | お店選びに関する自由記述の要望   |
| アレルギー | allergy    | string/null | アレルギー情報（カンマ区切り等） |
| 最低予算   | minPrice   | string/null | 最低予算                         |
| 最高予算   | maxPrice   | string/null | 最高予算                         |

※リクエストボディは参加者ごとに上記項目を持つオブジェクトの配列です。

### リクエストボディ例

```json
[
	{
		"memberName": "田中太郎",
		"station": "渋谷",
		"request": "和食が食べたい。個室希望。",
		"allergy": "えび",
		"minPrice": "3000",
		"maxPrice": "5000"
	},
	{
		"memberName": "佐藤花子",
		"station": "渋谷",
		"request": "ベジタリアン対応のお店がいいです。",
		"allergy": null,
		"minPrice": "2000",
		"maxPrice": "4000"
	}
]
```

## レスポンス

### レスポンスボディ項目

| 論理名            | 物理名  | 型          | 説明                                         |
| ----------------- | ------- | ----------- | -------------------------------------------- |
| 店舗リスト        | shops   | array       | 検索結果の店舗情報リスト                     |
| 店名              | name    | string      | 店名                                         |
| 最寄り駅          | station | string      | 最寄り駅                                     |
| 価格帯            | budget  | string      | 価格帯の目安（例: 3,000 円〜4,000 円）       |
| おすすめ一言      | summary | string      | お店の特徴を踏まえたおすすめの一言           |
| Google マップ URL | mapUrl  | string/null | Google マップの URL（存在しない場合は null） |

### レスポンスボディ例

```json
{
	"shops": [
		{
			"name": "和食ダイニング さくら",
			"station": "渋谷",
			"budget": "3,000円〜4,000円",
			"summary": "落ち着いた個室で和食と日本酒が楽しめる、全員満足の人気店です。",
			"mapUrl": "https://maps.google.com/?q=和食ダイニング+さくら"
		},
		{
			"name": "イタリアンバル ROSSO",
			"station": "渋谷",
			"budget": "2,500円〜3,500円",
			"summary": "アレルギー対応メニューも充実したカジュアルなイタリアンバル。",
			"mapUrl": null
		},
		{
			"name": "ベジタブルキッチン Green",
			"station": "渋谷",
			"budget": "3,000円〜4,500円",
			"summary": "ヘルシー志向の方にもおすすめ、野菜中心の創作料理店です。",
			"mapUrl": "https://maps.google.com/?q=ベジタブルキッチン+Green"
		}
	]
}
```
