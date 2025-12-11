"""
Export/Import Service Usage Examples

エクスポート/インポート機能の使用例
"""

from datetime import datetime
from backend.services.export_service import (
    ExportService,
    export_to_file,
    import_from_file,
)


def example_export_all_recipes():
    """
    全レシピエクスポートの例
    """
    print("=== 全レシピエクスポート ===")

    # サービス初期化（実際はDBセッションを渡す）
    export_service = ExportService(db_session=None)

    # 全レシピをエクスポート
    export_data = export_service.export_all_recipes()

    print(f"エクスポート日時: {export_data['exported_at']}")
    print(f"レシピ数: {export_data['recipe_count']}")
    print(f"バージョン: {export_data['version']}")

    # ファイルに保存
    output_path = "/tmp/all_recipes_export.json"
    export_to_file(export_data, output_path)
    print(f"保存先: {output_path}")

    print()


def example_export_single_recipe():
    """
    単一レシピエクスポートの例
    """
    print("=== 単一レシピエクスポート ===")

    export_service = ExportService(db_session=None)

    recipe_id = 1

    try:
        export_data = export_service.export_single_recipe(recipe_id)

        print(f"レシピID: {recipe_id}")
        print(f"タイトル: {export_data['recipes'][0]['title']}")

        # ファイルに保存
        output_path = f"/tmp/recipe_{recipe_id}_export.json"
        export_to_file(export_data, output_path)
        print(f"保存先: {output_path}")

    except ValueError as e:
        print(f"エラー: {e}")

    print()


def example_export_batch_recipes():
    """
    バッチエクスポートの例
    """
    print("=== バッチエクスポート ===")

    export_service = ExportService(db_session=None)

    # エクスポートしたいレシピIDのリスト
    recipe_ids = [1, 2, 3, 4, 5]

    export_data = export_service.export_batch_recipes(recipe_ids)

    print(f"指定レシピ数: {len(recipe_ids)}")
    print(f"エクスポート成功: {export_data['recipe_count']}")

    # ファイルに保存
    output_path = "/tmp/batch_recipes_export.json"
    export_to_file(export_data, output_path)
    print(f"保存先: {output_path}")

    print()


def example_validate_import_data():
    """
    インポートデータバリデーションの例
    """
    print("=== インポートデータバリデーション ===")

    export_service = ExportService(db_session=None)

    # サンプルインポートデータ
    import_data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "recipe_count": 2,
        "recipes": [
            {
                "title": "テストレシピ1",
                "ingredients": [{"name": "材料A", "amount": "100", "unit": "g"}],
                "steps": ["手順1", "手順2"],
                "tags": ["簡単"],
            },
            {
                # 不正なデータ（titleが欠けている）
                "ingredients": [],
                "steps": ["手順1"],
            },
        ],
    }

    # バリデーション実行
    result = export_service.validate_import_data(import_data, check_duplicates=True)

    print(f"バリデーション結果: {'成功' if result.is_valid else '失敗'}")
    print(f"総レシピ数: {result.total_recipes}")
    print(f"有効なレシピ: {result.valid_recipes}")
    print(f"無効なレシピ: {result.invalid_recipes}")

    if result.errors:
        print("\nエラー詳細:")
        for error in result.errors:
            print(f"  - インデックス {error['index']}: {error['type']}")

    if result.warnings:
        print("\n警告:")
        for warning in result.warnings:
            print(f"  - {warning['type']}: {warning['message']}")

    if result.duplicates:
        print("\n重複:")
        for dup in result.duplicates:
            print(f"  - {dup['title']} (インデックス {dup['index']})")

    print()


def example_import_recipes():
    """
    レシピインポートの例
    """
    print("=== レシピインポート ===")

    export_service = ExportService(db_session=None)

    # インポートデータ
    import_data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "recipe_count": 3,
        "recipes": [
            {
                "title": "新レシピA",
                "source_url": "https://example.com/a",
                "ingredients": [{"name": "材料A", "amount": "100", "unit": "g"}],
                "steps": ["手順1"],
                "tags": ["簡単"],
            },
            {
                "title": "新レシピB",
                "ingredients": [{"name": "材料B", "amount": "200", "unit": "ml"}],
                "steps": ["手順1", "手順2"],
                "tags": ["時短"],
            },
            {
                "title": "新レシピC",
                "ingredients": [],
                "steps": ["手順1"],
            },
        ],
    }

    # インポート実行（重複はスキップ）
    result = export_service.import_recipes(
        import_data, skip_duplicates=True, overwrite_duplicates=False
    )

    print(f"インポート結果: {'成功' if result.success else '失敗'}")
    print(f"インポート数: {result.imported_count}")
    print(f"スキップ数: {result.skipped_count}")
    print(f"失敗数: {result.failed_count}")

    print("\n詳細:")
    for detail in result.details:
        print(f"  - {detail['title']}: {detail['status']}")
        if "recipe_id" in detail:
            print(f"    レシピID: {detail['recipe_id']}")

    print()


def example_import_with_overwrite():
    """
    上書きモードでのインポート例
    """
    print("=== 上書きモードでのインポート ===")

    export_service = ExportService(db_session=None)

    import_data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "recipe_count": 1,
        "recipes": [
            {
                "title": "既存レシピ（更新版）",
                "source_url": "https://example.com/existing",
                "ingredients": [{"name": "材料A（新）", "amount": "150", "unit": "g"}],
                "steps": ["新しい手順1", "新しい手順2"],
                "tags": ["更新済み"],
            }
        ],
    }

    # 重複を上書き
    result = export_service.import_recipes(
        import_data, skip_duplicates=False, overwrite_duplicates=True
    )

    print(f"インポート数: {result.imported_count}")

    for detail in result.details:
        print(f"  - {detail['title']}: {detail['status']}")

    print()


def example_file_export_import():
    """
    ファイル経由でのエクスポート・インポート例
    """
    print("=== ファイル経由エクスポート・インポート ===")

    export_service = ExportService(db_session=None)

    # 1. エクスポート
    export_data = export_service.export_all_recipes()
    export_path = "/tmp/recipes_backup.json"
    export_to_file(export_data, export_path)
    print(f"エクスポート完了: {export_path}")

    # 2. ファイルから読み込み
    imported_data = import_from_file(export_path)
    print(f"ファイル読み込み完了: {imported_data['recipe_count']} レシピ")

    # 3. バリデーション
    validation_result = export_service.validate_import_data(
        imported_data, check_duplicates=True
    )
    print(f"バリデーション: {'OK' if validation_result.is_valid else 'NG'}")

    # 4. インポート
    if validation_result.is_valid:
        import_result = export_service.import_recipes(
            imported_data, skip_duplicates=True, overwrite_duplicates=False
        )
        print(f"インポート完了: {import_result.imported_count} レシピ")

    print()


def example_error_handling():
    """
    エラーハンドリングの例
    """
    print("=== エラーハンドリング ===")

    export_service = ExportService(db_session=None)

    # 1. 存在しないレシピのエクスポート
    print("1. 存在しないレシピのエクスポート:")
    try:
        export_service.export_single_recipe(99999)
    except ValueError as e:
        print(f"   エラーキャッチ: {e}")

    # 2. 不正なJSONファイルの読み込み
    print("\n2. 存在しないファイルの読み込み:")
    try:
        import_from_file("/nonexistent/path/file.json")
    except FileNotFoundError as e:
        print(f"   エラーキャッチ: {e}")

    # 3. 不正なフォーマットのインポート
    print("\n3. 不正なフォーマットのインポート:")
    invalid_data = {
        "version": "1.0",
        "recipes": [
            {
                # titleが欠けている
                "ingredients": [],
                "steps": [],
            }
        ],
    }

    validation_result = export_service.validate_import_data(
        invalid_data, check_duplicates=False
    )
    if not validation_result.is_valid:
        print("   バリデーション失敗:")
        print(f"   エラー数: {len(validation_result.errors)}")
        for error in validation_result.errors:
            print(f"     - {error['type']}")

    print()


def main():
    """
    すべての使用例を実行
    """
    print("=" * 60)
    print("Export/Import Service Usage Examples")
    print("=" * 60)
    print()

    example_export_all_recipes()
    example_export_single_recipe()
    example_export_batch_recipes()
    example_validate_import_data()
    example_import_recipes()
    example_import_with_overwrite()
    example_file_export_import()
    example_error_handling()

    print("=" * 60)
    print("すべての例を実行完了")
    print("=" * 60)


if __name__ == "__main__":
    main()
