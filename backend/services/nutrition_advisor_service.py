"""
栄養士AI相談サービス

ルールベースのチャットボットと栄養アドバイス生成機能を提供
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4

from backend.services.nutrition_service import NutritionService


class NutritionAdvisorService:
    """栄養士AIサービス"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.chat_history_file = self.data_dir / "advisor_chat_history.json"
        self.user_profiles_file = self.data_dir / "advisor_user_profiles.json"
        self.nutrition_service = NutritionService()

        # チャット履歴とユーザープロファイルのロード
        self.chat_history = self._load_chat_history()
        self.user_profiles = self._load_user_profiles()

        # アドバイスデータベース
        self.knowledge_base = self._initialize_knowledge_base()
        self.quick_actions = self._initialize_quick_actions()

    def _load_chat_history(self) -> Dict[str, List[Dict]]:
        """チャット履歴をロード"""
        if self.chat_history_file.exists():
            with open(self.chat_history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_chat_history(self):
        """チャット履歴を保存"""
        with open(self.chat_history_file, "w", encoding="utf-8") as f:
            json.dump(self.chat_history, f, ensure_ascii=False, indent=2)

    def _load_user_profiles(self) -> Dict[str, Dict]:
        """ユーザープロファイルをロード"""
        if self.user_profiles_file.exists():
            with open(self.user_profiles_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_user_profiles(self):
        """ユーザープロファイルを保存"""
        with open(self.user_profiles_file, "w", encoding="utf-8") as f:
            json.dump(self.user_profiles, f, ensure_ascii=False, indent=2)

    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """栄養知識ベースを初期化"""
        return {
            "greetings": {
                "patterns": [
                    r"こんにちは",
                    r"はじめまして",
                    r"こんばんは",
                    r"おはよう",
                ],
                "responses": [
                    "こんにちは！栄養アドバイザーです。栄養や食事についてお気軽にご質問ください。",
                    "はじめまして！健康的な食生活をサポートします。何かお困りのことはありますか？",
                    "こんにちは！今日の食事についてお悩みですか？お気軽にご相談ください。",
                ],
            },
            "protein": {
                "patterns": [
                    r"タンパク質",
                    r"たんぱく質",
                    r"プロテイン",
                    r"筋肉",
                    r"肉",
                    r"魚",
                ],
                "responses": [
                    "タンパク質は体を作る重要な栄養素です。成人は体重1kgあたり1.0〜1.2g程度が推奨されます。",
                    "良質なタンパク質源として、鶏肉、魚、卵、大豆製品、乳製品がおすすめです。",
                    "筋肉を増やしたい場合は、運動後30分以内にタンパク質を摂取すると効果的です。",
                ],
                "tips": [
                    "動物性と植物性のタンパク質をバランスよく摂取しましょう",
                    "プロテインパウダーに頼りすぎず、食事から摂ることを優先しましょう",
                ],
            },
            "carbohydrates": {
                "patterns": [
                    r"炭水化物",
                    r"糖質",
                    r"ご飯",
                    r"パン",
                    r"麺",
                    r"エネルギー",
                ],
                "responses": [
                    "炭水化物は体のエネルギー源です。総摂取カロリーの50〜65%が目安です。",
                    "玄米、全粒粉パン、オートミールなど、食物繊維が豊富な複合炭水化物がおすすめです。",
                    "糖質制限は短期的には効果がありますが、長期的にはバランスが大切です。",
                ],
                "tips": [
                    "白米より玄米や雑穀米を選ぶと栄養価が高まります",
                    "夜遅い時間の炭水化物摂取は控えめにしましょう",
                ],
            },
            "fat": {
                "patterns": [r"脂質", r"脂肪", r"油", r"オイル", r"コレステロール"],
                "responses": [
                    "脂質は細胞膜やホルモンの材料となる重要な栄養素です。総摂取カロリーの20〜30%が目安です。",
                    "オメガ3脂肪酸（魚油、亜麻仁油）とオメガ6脂肪酸のバランスが重要です。",
                    "トランス脂肪酸（マーガリン、ショートニング）は避け、不飽和脂肪酸を選びましょう。",
                ],
                "tips": [
                    "ナッツ類やアボカドから良質な脂質を摂取できます",
                    "揚げ物より蒸し料理や焼き料理を選びましょう",
                ],
            },
            "vitamins": {
                "patterns": [r"ビタミン", r"野菜", r"果物", r"サプリ"],
                "responses": [
                    "ビタミンは体の調子を整える重要な栄養素です。色とりどりの野菜を食べることで様々なビタミンが摂れます。",
                    "ビタミンCは水溶性なので毎日摂取が必要です。柑橘類、いちご、ブロッコリーが豊富です。",
                    "ビタミンDは日光浴や魚から摂取できます。不足しがちな栄養素なので意識的に摂りましょう。",
                ],
                "tips": [
                    "野菜は1日350g以上を目標にしましょう",
                    "サプリメントは食事で不足する分を補う程度にしましょう",
                ],
            },
            "minerals": {
                "patterns": [
                    r"ミネラル",
                    r"カルシウム",
                    r"鉄分",
                    r"亜鉛",
                    r"マグネシウム",
                ],
                "responses": [
                    "カルシウムは骨の健康に不可欠です。乳製品、小魚、大豆製品から摂取しましょう。",
                    "鉄分は貧血予防に重要です。レバー、赤身肉、ほうれん草が豊富です。ビタミンCと一緒に摂ると吸収率が上がります。",
                    "亜鉛は免疫機能や味覚に関わります。牡蠣、レバー、ナッツ類に多く含まれます。",
                ],
                "tips": [
                    "鉄分はコーヒーやお茶で吸収が阻害されるので食後すぐの摂取は避けましょう",
                    "カルシウムとマグネシウムはバランスよく摂取することが重要です",
                ],
            },
            "weight_loss": {
                "patterns": [r"痩せたい", r"ダイエット", r"減量", r"体重を減らす"],
                "responses": [
                    "健康的なダイエットは、摂取カロリーを消費カロリーより少し少なくすることです。急激な減量は避けましょう。",
                    "1ヶ月に体重の3〜5%減が理想的なペースです。バランスの良い食事と適度な運動が大切です。",
                    "食事を抜くのではなく、栄養バランスを保ちながら総カロリーを減らしましょう。",
                ],
                "tips": [
                    "よく噛んでゆっくり食べると満腹感が得られやすいです",
                    "野菜から食べ始めると血糖値の急上昇を防げます",
                    "水分を十分に摂ることも重要です（1日1.5〜2L）",
                ],
            },
            "weight_gain": {
                "patterns": [r"太りたい", r"体重を増やす", r"増量"],
                "responses": [
                    "健康的に体重を増やすには、高タンパク質で栄養価の高い食事を小分けに食べることが効果的です。",
                    "筋肉を増やすために、タンパク質と炭水化物をしっかり摂り、筋力トレーニングを組み合わせましょう。",
                    "ナッツ類、アボカド、オリーブオイルなど、良質な脂質を積極的に摂りましょう。",
                ],
                "tips": [
                    "3食に加えて間食（おやつ）を取り入れましょう",
                    "プロテインシェイクやスムージーでカロリーを補給できます",
                ],
            },
            "allergies": {
                "patterns": [r"アレルギー", r"アレルゲン", r"食物アレルギー"],
                "responses": [
                    "食物アレルギーがある場合は、代替食材で必要な栄養素を補うことが重要です。",
                    "乳アレルギーの場合、カルシウムは小魚、大豆製品、緑黄色野菜から摂取できます。",
                    "卵アレルギーの場合、タンパク質は肉、魚、大豆製品で補えます。",
                ],
                "tips": [
                    "外食時は必ずアレルゲンの確認を行いましょう",
                    "栄養士や医師に相談して個別の食事プランを立てましょう",
                ],
            },
            "diabetes": {
                "patterns": [r"糖尿病", r"血糖値", r"インスリン"],
                "responses": [
                    "糖尿病管理では、血糖値の急上昇を防ぐことが重要です。低GI食品を選びましょう。",
                    "食物繊維が豊富な食品（野菜、海藻、きのこ）を先に食べると血糖値の上昇が緩やかになります。",
                    "規則正しい食事時間と適度な運動が血糖コントロールに効果的です。",
                ],
                "tips": [
                    "炭水化物は全体量を把握してコントロールしましょう",
                    "定期的に血糖値を測定し、主治医と相談しながら管理しましょう",
                ],
            },
            "hydration": {
                "patterns": [r"水分", r"水", r"お茶", r"飲み物", r"脱水"],
                "responses": [
                    "1日に1.5〜2Lの水分摂取が推奨されます。特に運動時や暑い日は多めに摂りましょう。",
                    "水やお茶が基本です。糖分の多いジュースは控えめに。",
                    "コーヒーやお茶にはカフェインが含まれ利尿作用があるので、水分補給としては水が最適です。",
                ],
                "tips": [
                    "喉が渇く前にこまめに水分補給しましょう",
                    "尿の色が濃い場合は水分不足のサインです",
                ],
            },
            "meal_timing": {
                "patterns": [r"食事時間", r"朝食", r"夕食", r"間食", r"いつ食べる"],
                "responses": [
                    "朝食は1日のエネルギー源として重要です。できるだけ規則正しく食べましょう。",
                    "夕食は就寝3時間前までに済ませると消化に良く、睡眠の質も向上します。",
                    "間食は午後3時頃が最適です。ナッツやヨーグルト、果物がおすすめです。",
                ],
                "tips": [
                    "1日3食、規則正しく食べることが基本です",
                    "夜遅い時間の食事は消化器官に負担をかけます",
                ],
            },
            "exercise": {
                "patterns": [r"運動", r"筋トレ", r"有酸素運動", r"トレーニング"],
                "responses": [
                    "運動前は消化の良い炭水化物を、運動後30分以内にタンパク質と炭水化物を摂取すると効果的です。",
                    "有酸素運動前は軽い食事、筋トレ後はタンパク質をしっかり摂りましょう。",
                    "運動中の水分補給も忘れずに。長時間の運動では電解質も補給しましょう。",
                ],
                "tips": [
                    "空腹での激しい運動は避けましょう",
                    "運動後のゴールデンタイム（30分以内）を活用しましょう",
                ],
            },
            "sleep": {
                "patterns": [r"睡眠", r"寝る", r"夜更かし", r"不眠"],
                "responses": [
                    "良質な睡眠は栄養の吸収や体の回復に重要です。就寝前のカフェイン摂取は避けましょう。",
                    "トリプトファン（バナナ、乳製品、ナッツ）を含む食品は睡眠の質を高めます。",
                    "就寝直前の食事は睡眠の質を下げるので、3時間前までに済ませましょう。",
                ],
                "tips": [
                    "規則正しい生活リズムが睡眠の質を高めます",
                    "夜遅い時間のブルーライト（スマホ、PC）は避けましょう",
                ],
            },
            "stress": {
                "patterns": [r"ストレス", r"疲れ", r"イライラ", r"精神"],
                "responses": [
                    "ストレス管理にはビタミンB群、ビタミンC、マグネシウムが重要です。",
                    "バランスの良い食事、十分な睡眠、適度な運動がストレス軽減に効果的です。",
                    "腸内環境を整えることもメンタルヘルスに良い影響を与えます。発酵食品を取り入れましょう。",
                ],
                "tips": [
                    "深呼吸やリラックスできる時間を作りましょう",
                    "カフェインの過剰摂取はストレスを増幅させることがあります",
                ],
            },
            "pregnancy": {
                "patterns": [r"妊娠", r"妊婦", r"授乳", r"マタニティ"],
                "responses": [
                    "妊娠中は葉酸、鉄分、カルシウムが特に重要です。バランスの良い食事を心がけましょう。",
                    "葉酸は胎児の神経管形成に必須です。緑黄色野菜、豆類に多く含まれます。",
                    "授乳中はエネルギーとタンパク質の必要量が増えます。水分補給も十分に行いましょう。",
                ],
                "tips": [
                    "生肉、生魚、アルコールは避けましょう",
                    "必ず医師や助産師の指導を受けながら食事管理を行いましょう",
                ],
            },
            "elderly": {
                "patterns": [r"高齢", r"シニア", r"老人", r"年配"],
                "responses": [
                    "高齢者はタンパク質不足になりやすいので、意識的に摂取しましょう。",
                    "カルシウムとビタミンDで骨の健康を維持することが重要です。",
                    "柔らかく調理し、飲み込みやすい食事を心がけましょう。",
                ],
                "tips": [
                    "少量でも栄養価の高い食事を選びましょう",
                    "水分摂取が減りがちなので意識的に水分を摂りましょう",
                ],
            },
            "unknown": {
                "responses": [
                    "申し訳ございませんが、その質問には十分な情報がありません。もう少し詳しく教えていただけますか？",
                    "その内容については、専門の医師や栄養士にご相談されることをおすすめします。",
                    "ご質問の内容を理解できませんでした。別の言い方で質問していただけますか？",
                ],
            },
        }

    def _initialize_quick_actions(self) -> List[Dict[str, str]]:
        """クイックアクションを初期化"""
        return [
            {
                "id": "weight_loss",
                "label": "ダイエットのコツは？",
                "message": "ダイエットについて教えてください",
            },
            {
                "id": "protein",
                "label": "タンパク質の摂り方は？",
                "message": "タンパク質について教えてください",
            },
            {
                "id": "balanced_diet",
                "label": "バランスの良い食事とは？",
                "message": "バランスの良い食事について教えてください",
            },
            {
                "id": "hydration",
                "label": "水分補給のタイミングは？",
                "message": "水分補給について教えてください",
            },
            {
                "id": "meal_timing",
                "label": "食事のタイミングは？",
                "message": "食事時間について教えてください",
            },
            {
                "id": "vitamins",
                "label": "ビタミンの重要性は？",
                "message": "ビタミンについて教えてください",
            },
        ]

    def _estimate_nutrition_for_recipe(self, recipe_id: str) -> Dict[str, float]:
        """レシピIDから栄養情報を推定（ダミー実装）"""
        # 実際のレシピDBが利用できない場合のダミー推定値
        # 一般的な食事の平均的な栄養価を返す
        return {
            "calories": 350.0,
            "protein": 20.0,
            "carbohydrates": 40.0,
            "fat": 12.0,
        }

    def chat(
        self, user_id: str, message: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """チャットメッセージを処理"""
        # ユーザープロファイルの取得・作成
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "created_at": datetime.now().isoformat(),
                "preferences": {},
                "restrictions": [],
                "goals": [],
            }
            self._save_user_profiles()

        # チャット履歴の取得・作成
        if user_id not in self.chat_history:
            self.chat_history[user_id] = []

        # メッセージを履歴に追加
        user_message = {
            "id": str(uuid4()),
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
        }
        self.chat_history[user_id].append(user_message)

        # 応答を生成
        response_content, response_type, tips = self._generate_response(
            message, self.user_profiles[user_id], context
        )

        # 応答を履歴に追加
        assistant_message = {
            "id": str(uuid4()),
            "role": "assistant",
            "content": response_content,
            "type": response_type,
            "tips": tips,
            "timestamp": datetime.now().isoformat(),
        }
        self.chat_history[user_id].append(assistant_message)

        # 履歴を保存（最新100件のみ保持）
        self.chat_history[user_id] = self.chat_history[user_id][-100:]
        self._save_chat_history()

        return {
            "message": assistant_message,
            "conversation_id": user_id,
            "quick_actions": self._get_relevant_quick_actions(response_type),
        }

    def _generate_response(
        self, message: str, user_profile: Dict, context: Optional[Dict]
    ) -> Tuple[str, str, List[str]]:
        """応答を生成"""
        message.lower()

        # パターンマッチング
        for category, data in self.knowledge_base.items():
            if category == "unknown":
                continue

            patterns = data.get("patterns", [])
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    responses = data.get("responses", [])
                    tips = data.get("tips", [])

                    # ユーザープロファイルに基づいてカスタマイズ
                    response = self._personalize_response(
                        responses[0] if responses else "情報が見つかりませんでした。",
                        user_profile,
                        category,
                    )

                    return response, category, tips

        # 未知の質問
        unknown_responses = self.knowledge_base["unknown"]["responses"]
        return unknown_responses[0], "unknown", []

    def _personalize_response(
        self, base_response: str, user_profile: Dict, category: str
    ) -> str:
        """ユーザープロファイルに基づいて応答をパーソナライズ"""
        response = base_response

        # 目標に応じた追加情報
        goals = user_profile.get("goals", [])
        if "weight_loss" in goals and category in ["carbohydrates", "fat"]:
            response += "\n\n減量が目標の場合は、特に総カロリーに注意しましょう。"
        elif "muscle_gain" in goals and category == "protein":
            response += "\n\n筋肉増強が目標の場合は、体重1kgあたり1.6〜2.0gのタンパク質摂取を目指しましょう。"

        # 制限事項に応じた警告
        restrictions = user_profile.get("restrictions", [])
        if "diabetes" in restrictions and category == "carbohydrates":
            response += "\n\n⚠️ 糖尿病の方は、血糖値の変動に注意し、主治医の指導に従ってください。"
        elif "allergy" in restrictions and category in ["protein", "fat"]:
            response += "\n\n⚠️ アレルギーがある場合は、代替食材を選びましょう。"

        return response

    def _get_relevant_quick_actions(self, response_type: str) -> List[Dict[str, str]]:
        """応答タイプに応じた関連クイックアクションを取得"""
        # 全クイックアクションから関連するものを選択
        # 簡易実装として全てを返す
        return self.quick_actions

    def get_chat_history(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """チャット履歴を取得"""
        history = self.chat_history.get(user_id, [])
        total = len(history)

        # ページネーション
        paginated_history = history[-(offset + limit) : -offset if offset > 0 else None]
        paginated_history.reverse()

        return {
            "history": paginated_history,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def analyze_meal(self, user_id: str, meal_data: Dict) -> Dict[str, Any]:
        """食事を分析してアドバイスを提供"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "meal_type": meal_data.get("meal_type", "unknown"),
            "items": meal_data.get("items", []),
            "nutrition": {},
            "advice": [],
            "score": 0,
        }

        # 栄養計算
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0

        for item in meal_data.get("items", []):
            recipe_id = item.get("recipe_id")
            if recipe_id:
                # レシピIDから栄養情報を取得（仮の推定値を使用）
                # 実際のレシピDBがない場合のダミー栄養情報
                nutrition_info = self._estimate_nutrition_for_recipe(recipe_id)
                if nutrition_info:
                    servings = item.get("servings", 1)
                    total_calories += nutrition_info.get("calories", 0) * servings
                    total_protein += nutrition_info.get("protein", 0) * servings
                    total_carbs += nutrition_info.get("carbohydrates", 0) * servings
                    total_fat += nutrition_info.get("fat", 0) * servings

        analysis["nutrition"] = {
            "calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "carbohydrates": round(total_carbs, 1),
            "fat": round(total_fat, 1),
        }

        # アドバイス生成
        meal_type = meal_data.get("meal_type", "meal")
        advice = []
        score = 70  # 基本スコア

        # カロリーチェック
        if meal_type == "breakfast":
            if 300 <= total_calories <= 500:
                score += 10
            else:
                advice.append("朝食は300〜500kcal程度が理想的です。")
                score -= 5
        elif meal_type == "lunch":
            if 500 <= total_calories <= 800:
                score += 10
            else:
                advice.append("昼食は500〜800kcal程度が理想的です。")
                score -= 5
        elif meal_type == "dinner":
            if 400 <= total_calories <= 700:
                score += 10
            else:
                advice.append("夕食は400〜700kcal程度が理想的です。")
                score -= 5

        # タンパク質チェック
        if total_protein < 15:
            advice.append(
                "タンパク質が不足しています。肉、魚、卵、大豆製品を追加しましょう。"
            )
            score -= 10
        elif total_protein >= 20:
            score += 10

        # 炭水化物チェック
        carb_ratio = (
            (total_carbs * 4 / total_calories * 100) if total_calories > 0 else 0
        )
        if carb_ratio > 70:
            advice.append(
                "炭水化物の割合が高めです。野菜やタンパク質を増やしましょう。"
            )
            score -= 5
        elif 50 <= carb_ratio <= 65:
            score += 5

        # 脂質チェック
        fat_ratio = (total_fat * 9 / total_calories * 100) if total_calories > 0 else 0
        if fat_ratio > 35:
            advice.append("脂質の割合が高めです。調理方法を見直しましょう。")
            score -= 5
        elif 20 <= fat_ratio <= 30:
            score += 5

        # ポジティブフィードバック
        if not advice:
            advice.append("バランスの良い食事です！この調子で続けましょう。")

        analysis["advice"] = advice
        analysis["score"] = max(0, min(100, score))

        # 分析履歴に追加
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "created_at": datetime.now().isoformat(),
                "preferences": {},
                "restrictions": [],
                "goals": [],
            }

        if "meal_analyses" not in self.user_profiles[user_id]:
            self.user_profiles[user_id]["meal_analyses"] = []

        self.user_profiles[user_id]["meal_analyses"].append(analysis)
        self.user_profiles[user_id]["meal_analyses"] = self.user_profiles[user_id][
            "meal_analyses"
        ][
            -30:
        ]  # 最新30件のみ保持
        self._save_user_profiles()

        return analysis

    def get_daily_tip(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """今日のワンポイントアドバイスを取得"""
        # 日付ベースでランダムにカテゴリを選択
        import random

        random.seed(datetime.now().date().toordinal())

        categories = [
            cat
            for cat in self.knowledge_base.keys()
            if cat not in ["unknown", "greetings"]
        ]
        selected_category = random.choice(categories)
        category_data = self.knowledge_base[selected_category]

        tip = {
            "date": datetime.now().date().isoformat(),
            "category": selected_category,
            "title": self._get_category_title(selected_category),
            "content": category_data["responses"][0],
            "tips": category_data.get("tips", []),
        }

        return tip

    def _get_category_title(self, category: str) -> str:
        """カテゴリ名を日本語タイトルに変換"""
        titles = {
            "protein": "タンパク質の重要性",
            "carbohydrates": "炭水化物の上手な摂り方",
            "fat": "脂質との付き合い方",
            "vitamins": "ビタミンで体を整える",
            "minerals": "ミネラルの役割",
            "weight_loss": "健康的なダイエット",
            "weight_gain": "体重を増やすコツ",
            "allergies": "食物アレルギー対策",
            "diabetes": "血糖値管理",
            "hydration": "水分補給の大切さ",
            "meal_timing": "食事のタイミング",
            "exercise": "運動と栄養",
            "sleep": "睡眠と食事",
            "stress": "ストレス管理と栄養",
            "pregnancy": "妊娠・授乳期の栄養",
            "elderly": "高齢者の栄養管理",
        }
        return titles.get(category, "栄養アドバイス")

    def generate_meal_plan(self, user_id: str, preferences: Dict) -> Dict[str, Any]:
        """食事プランを提案"""
        # ユーザープロファイルを取得または作成
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "created_at": datetime.now().isoformat(),
                "preferences": {},
                "restrictions": [],
                "goals": [],
            }

        user_profile = self.user_profiles[user_id]

        # 目標カロリーを計算
        target_calories = preferences.get("target_calories")
        if not target_calories:
            # デフォルト値（成人平均）
            target_calories = 2000

        # 1日の食事配分
        breakfast_ratio = 0.25
        lunch_ratio = 0.35
        dinner_ratio = 0.30
        snack_ratio = 0.10

        meal_plan = {
            "date": datetime.now().date().isoformat(),
            "target_calories": target_calories,
            "target_protein": target_calories * 0.15 / 4,  # 15%をタンパク質
            "target_carbs": target_calories * 0.55 / 4,  # 55%を炭水化物
            "target_fat": target_calories * 0.30 / 9,  # 30%を脂質
            "meals": {
                "breakfast": {
                    "target_calories": target_calories * breakfast_ratio,
                    "suggestions": [
                        "玄米ご飯（茶碗1杯）+ 焼き魚 + 味噌汁 + 納豆",
                        "全粒粉パン（2枚）+ スクランブルエッグ + サラダ + ヨーグルト",
                        "オートミール + バナナ + ナッツ + 豆乳",
                    ],
                    "tips": [
                        "タンパク質と炭水化物をバランスよく",
                        "果物でビタミンを補給",
                    ],
                },
                "lunch": {
                    "target_calories": target_calories * lunch_ratio,
                    "suggestions": [
                        "鶏胸肉のグリル + 玄米 + 温野菜サラダ",
                        "サーモン丼 + 海藻サラダ + 味噌汁",
                        "パスタ（全粒粉）+ チキンとブロッコリー + スープ",
                    ],
                    "tips": [
                        "活動エネルギー源として炭水化物を摂取",
                        "野菜をたっぷり取り入れる",
                    ],
                },
                "dinner": {
                    "target_calories": target_calories * dinner_ratio,
                    "suggestions": [
                        "豆腐ハンバーグ + 雑穀米 + 野菜スープ",
                        "白身魚の蒸し料理 + 玄米 + 野菜炒め",
                        "鶏肉と野菜の煮物 + 麦ごはん + サラダ",
                    ],
                    "tips": ["消化に良い食材を選ぶ", "脂質は控えめに"],
                },
                "snacks": {
                    "target_calories": target_calories * snack_ratio,
                    "suggestions": [
                        "ヨーグルト + ベリー類",
                        "ナッツ（アーモンド10粒程度）",
                        "りんご + チーズ",
                    ],
                    "tips": ["午後3時頃が最適", "糖質と脂質のバランスに注意"],
                },
            },
            "hydration": {
                "target_water": 2000,  # ml
                "tips": [
                    "起床後にコップ1杯の水",
                    "食事前30分に水分補給",
                    "運動前後は多めに摂取",
                ],
            },
            "general_advice": [],
        }

        # ユーザーの目標に応じたアドバイス
        goals = preferences.get("goals", user_profile.get("goals", []))
        if "weight_loss" in goals:
            meal_plan["general_advice"].append(
                "減量中は総カロリーを目標より10〜20%減らしましょう"
            )
            meal_plan["general_advice"].append("野菜を先に食べて満腹感を得ましょう")
        elif "muscle_gain" in goals:
            meal_plan["general_advice"].append(
                "筋肉増強にはタンパク質を体重1kgあたり1.6〜2.0g摂取しましょう"
            )
            meal_plan["general_advice"].append(
                "運動後30分以内にタンパク質を補給しましょう"
            )

        # 制限事項に応じたアドバイス
        restrictions = preferences.get(
            "restrictions", user_profile.get("restrictions", [])
        )
        if "diabetes" in restrictions:
            meal_plan["general_advice"].append(
                "血糖値の急上昇を防ぐため、低GI食品を選びましょう"
            )
        if "allergy" in restrictions:
            meal_plan["general_advice"].append(
                "アレルゲンを含まない代替食材を選びましょう"
            )

        if not meal_plan["general_advice"]:
            meal_plan["general_advice"].append("バランスの良い食事を心がけましょう")
            meal_plan["general_advice"].append("規則正しい食事時間を守りましょう")

        return meal_plan

    def update_user_profile(
        self, user_id: str, profile_updates: Dict
    ) -> Dict[str, Any]:
        """ユーザープロファイルを更新"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "created_at": datetime.now().isoformat(),
                "preferences": {},
                "restrictions": [],
                "goals": [],
            }

        # プロファイルを更新
        profile = self.user_profiles[user_id]

        if "preferences" in profile_updates:
            profile["preferences"].update(profile_updates["preferences"])

        if "restrictions" in profile_updates:
            profile["restrictions"] = profile_updates["restrictions"]

        if "goals" in profile_updates:
            profile["goals"] = profile_updates["goals"]

        profile["updated_at"] = datetime.now().isoformat()

        self._save_user_profiles()

        return profile

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """ユーザープロファイルを取得"""
        return self.user_profiles.get(user_id)

    def clear_chat_history(self, user_id: str) -> bool:
        """チャット履歴をクリア"""
        if user_id in self.chat_history:
            self.chat_history[user_id] = []
            self._save_chat_history()
            return True
        return False
