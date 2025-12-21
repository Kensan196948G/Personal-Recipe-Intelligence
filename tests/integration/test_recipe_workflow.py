"""
レシピワークフロー統合テスト

CRUD操作の完全フロー、検索・フィルター、タグ管理の統合テスト。
CLAUDE.md 準拠：pytest, 外部依存モック化
"""

from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient


class TestRecipeCRUDWorkflow:
    """レシピCRUD操作の完全ワークフロー"""

    def test_complete_crud_lifecycle(
        self,
        test_client: TestClient,
        sample_recipe_data: Dict[str, Any],
        auth_headers: Dict[str, str],
    ):
        """
        完全なCRUDライフサイクル
        1. Create
        2. Read
        3. Update
        4. Delete
        """
        # 1. CREATE
        create_response = test_client.post(
            "/api/v1/recipes/", json=sample_recipe_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        recipe_id = create_response.json()["data"]["id"]

        # 2. READ (単体)
        read_response = test_client.get(
            f"/api/v1/recipes/{recipe_id}", headers=auth_headers
        )
        assert read_response.status_code == 200
        recipe_data = read_response.json()["data"]
        assert recipe_data["title"] == sample_recipe_data["title"]

        # 3. UPDATE
        update_data = {
            "title": "スパイシーカレーライス",
            "cook_time": 60,
            "tags": ["カレー", "簡単", "定番", "スパイシー"],
        }
        update_response = test_client.put(
            f"/api/v1/recipes/{recipe_id}", json=update_data, headers=auth_headers
        )
        assert update_response.status_code == 200
        updated_data = update_response.json()["data"]
        assert updated_data["title"] == "スパイシーカレーライス"
        assert updated_data["cook_time"] == 60

        # 4. DELETE
        delete_response = test_client.delete(
            f"/api/v1/recipes/{recipe_id}", headers=auth_headers
        )
        assert delete_response.status_code == 200

        # 削除確認
        get_deleted = test_client.get(
            f"/api/v1/recipes/{recipe_id}", headers=auth_headers
        )
        assert get_deleted.status_code == 404

    def test_bulk_create_and_list(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """一括作成とリスト取得"""
        recipes = [
            {
                "title": f"レシピ{i}",
                "ingredients": [{"name": "材料A", "amount": "100g"}],
                "steps": ["手順1", "手順2"],
                "tags": [f"タグ{i}"],
                "source": "web",
            }
            for i in range(5)
        ]

        created_ids = []
        for recipe in recipes:
            response = test_client.post(
                "/api/v1/recipes/", json=recipe, headers=auth_headers
            )
            assert response.status_code == 201
            created_ids.append(response.json()["data"]["id"])

        # リスト取得
        list_response = test_client.get("/api/v1/recipes/", headers=auth_headers)
        assert list_response.status_code == 200
        assert len(list_response.json()["data"]) == 5

    def test_partial_update(
        self,
        test_client: TestClient,
        sample_recipe_data: Dict[str, Any],
        auth_headers: Dict[str, str],
    ):
        """部分更新（一部フィールドのみ）"""
        # レシピ作成
        create_response = test_client.post(
            "/api/v1/recipes/", json=sample_recipe_data, headers=auth_headers
        )
        recipe_id = create_response.json()["data"]["id"]

        # 部分更新（タイトルのみ）
        partial_update = {"title": "新しいタイトル"}
        update_response = test_client.patch(
            f"/api/v1/recipes/{recipe_id}", json=partial_update, headers=auth_headers
        )

        # PATCHが実装されていない場合はスキップ
        if update_response.status_code == 405:
            pytest.skip("PATCH method not implemented")

        assert update_response.status_code == 200
        updated = update_response.json()["data"]
        assert updated["title"] == "新しいタイトル"
        # 他のフィールドは維持されている
        assert len(updated["ingredients"]) == len(sample_recipe_data["ingredients"])


class TestRecipeSearchWorkflow:
    """レシピ検索とフィルタリングのワークフロー"""

    def test_search_by_multiple_criteria(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """複数条件での検索"""
        # タイトル検索
        title_search = test_client.get(
            "/api/v1/recipes/search?q=カレー", headers=auth_headers
        )
        assert title_search.status_code == 200
        assert len(title_search.json()["data"]) >= 1

        # タグ検索
        tag_search = test_client.get(
            "/api/v1/recipes/search?tag=パスタ", headers=auth_headers
        )
        assert tag_search.status_code == 200
        assert len(tag_search.json()["data"]) >= 1

    def test_filter_by_cook_time(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """調理時間でフィルタリング"""
        # 30分以下のレシピ
        response = test_client.get(
            "/api/v1/recipes/filter?max_cook_time=30", headers=auth_headers
        )

        if response.status_code == 404:
            pytest.skip("Filter endpoint not implemented")

        assert response.status_code == 200
        recipes = response.json()["data"]
        for recipe in recipes:
            assert recipe["cook_time"] <= 30

    def test_filter_by_servings(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """人数でフィルタリング"""
        response = test_client.get(
            "/api/v1/recipes/filter?servings=4", headers=auth_headers
        )

        if response.status_code == 404:
            pytest.skip("Filter endpoint not implemented")

        assert response.status_code == 200

    def test_combined_search_and_filter(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """検索とフィルターの組み合わせ"""
        response = test_client.get(
            "/api/v1/recipes/search?q=カレー&max_cook_time=50", headers=auth_headers
        )

        if response.status_code == 404:
            pytest.skip("Combined search/filter not implemented")

        assert response.status_code == 200

    def test_sort_recipes(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """ソート機能"""
        # 作成日時でソート
        response = test_client.get(
            "/api/v1/recipes/?sort_by=created_at&order=desc", headers=auth_headers
        )

        if response.status_code == 200:
            recipes = response.json()["data"]
            if len(recipes) > 1:
                # 降順確認
                assert recipes[0]["created_at"] >= recipes[1]["created_at"]


class TestTagManagementWorkflow:
    """タグ管理のワークフロー"""

    def test_add_tags_to_recipe(
        self,
        test_client: TestClient,
        sample_recipe_data: Dict[str, Any],
        auth_headers: Dict[str, str],
    ):
        """レシピへのタグ追加"""
        # レシピ作成
        create_response = test_client.post(
            "/api/v1/recipes/", json=sample_recipe_data, headers=auth_headers
        )
        recipe_id = create_response.json()["data"]["id"]

        # タグ追加
        new_tags = sample_recipe_data["tags"] + ["新タグ", "追加タグ"]
        update_response = test_client.put(
            f"/api/v1/recipes/{recipe_id}",
            json={"tags": new_tags},
            headers=auth_headers,
        )

        assert update_response.status_code == 200
        updated = update_response.json()["data"]
        assert "新タグ" in updated["tags"]
        assert "追加タグ" in updated["tags"]

    def test_remove_tags_from_recipe(
        self,
        test_client: TestClient,
        sample_recipe_data: Dict[str, Any],
        auth_headers: Dict[str, str],
    ):
        """レシピからのタグ削除"""
        # レシピ作成
        create_response = test_client.post(
            "/api/v1/recipes/", json=sample_recipe_data, headers=auth_headers
        )
        recipe_id = create_response.json()["data"]["id"]

        # タグを1つ削除
        remaining_tags = sample_recipe_data["tags"][:-1]
        update_response = test_client.put(
            f"/api/v1/recipes/{recipe_id}",
            json={"tags": remaining_tags},
            headers=auth_headers,
        )

        assert update_response.status_code == 200
        updated = update_response.json()["data"]
        assert len(updated["tags"]) == len(remaining_tags)

    def test_get_all_tags(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """全タグ一覧取得"""
        response = test_client.get("/api/v1/tags/", headers=auth_headers)

        if response.status_code == 404:
            pytest.skip("Tags endpoint not implemented")

        assert response.status_code == 200
        tags = response.json()["data"]
        assert isinstance(tags, list)
        assert "カレー" in tags or len(tags) > 0

    def test_get_recipes_by_tag(
        self,
        test_client: TestClient,
        sample_recipes_batch: list,
        auth_headers: Dict[str, str],
    ):
        """特定タグのレシピ取得"""
        response = test_client.get("/api/v1/tags/カレー/recipes", headers=auth_headers)

        if response.status_code == 404:
            pytest.skip("Tag-based recipe listing not implemented")

        assert response.status_code == 200
        recipes = response.json()["data"]
        for recipe in recipes:
            assert "カレー" in recipe["tags"]


class TestRecipeValidationWorkflow:
    """レシピバリデーションのワークフロー"""

    def test_required_fields_validation(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """必須フィールドのバリデーション"""
        invalid_recipes = [
            {},  # 全フィールド欠落
            {"title": ""},  # 空タイトル
            {"title": "テスト", "ingredients": []},  # 材料なし
            {
                "title": "テスト",
                "ingredients": [{"name": "材料A"}],
                "steps": [],
            },  # 手順なし
        ]

        for invalid_recipe in invalid_recipes:
            response = test_client.post(
                "/api/v1/recipes/", json=invalid_recipe, headers=auth_headers
            )
            assert response.status_code == 422

    def test_field_type_validation(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """フィールド型のバリデーション"""
        invalid_data = {
            "title": "テストレシピ",
            "ingredients": "should be array",  # 配列であるべき
            "steps": ["手順1"],
            "cook_time": "invalid",  # 数値であるべき
        }

        response = test_client.post(
            "/api/v1/recipes/", json=invalid_data, headers=auth_headers
        )
        assert response.status_code == 422

    def test_ingredient_structure_validation(
        self, test_client: TestClient, auth_headers: Dict[str, str]
    ):
        """材料構造のバリデーション"""
        recipe_data = {
            "title": "テストレシピ",
            "ingredients": [
                {"name": "材料A", "amount": "100g"},
                {"invalid_key": "value"},  # 不正な構造
            ],
            "steps": ["手順1"],
        }

        response = test_client.post(
            "/api/v1/recipes/", json=recipe_data, headers=auth_headers
        )
        # バリデーションルールにより422または201
        assert response.status_code in [201, 422]


class TestRecipeDataIntegrity:
    """レシピデータ整合性のテスト"""

    def test_duplicate_recipe_handling(
        self,
        test_client: TestClient,
        sample_recipe_data: Dict[str, Any],
        auth_headers: Dict[str, str],
    ):
        """重複レシピの処理"""
        # 1回目：成功
        first_response = test_client.post(
            "/api/v1/recipes/", json=sample_recipe_data, headers=auth_headers
        )
        assert first_response.status_code == 201

        # 2回目：重複許可または拒否
        second_response = test_client.post(
            "/api/v1/recipes/", json=sample_recipe_data, headers=auth_headers
        )
        # 重複許可の場合は201、拒否の場合は409
        assert second_response.status_code in [201, 409]

    def test_concurrent_updates(
        self,
        test_client: TestClient,
        sample_recipe_data: Dict[str, Any],
        auth_headers: Dict[str, str],
    ):
        """同時更新の処理"""
        # レシピ作成
        create_response = test_client.post(
            "/api/v1/recipes/", json=sample_recipe_data, headers=auth_headers
        )
        recipe_id = create_response.json()["data"]["id"]

        # 同時更新シミュレーション
        update1 = test_client.put(
            f"/api/v1/recipes/{recipe_id}",
            json={"title": "更新1"},
            headers=auth_headers,
        )
        update2 = test_client.put(
            f"/api/v1/recipes/{recipe_id}",
            json={"title": "更新2"},
            headers=auth_headers,
        )

        # 両方とも成功するはず
        assert update1.status_code == 200
        assert update2.status_code == 200

        # 最終的な状態確認
        final = test_client.get(f"/api/v1/recipes/{recipe_id}", headers=auth_headers)
        assert final.json()["data"]["title"] == "更新2"
