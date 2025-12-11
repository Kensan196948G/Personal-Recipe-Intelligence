"""
QRCode Service for Recipe Sharing

レシピ共有用のQRコード生成サービス
"""

import io
import json
from typing import Optional, Dict, Any, Literal
from pathlib import Path

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image


class QRCodeService:
    """QRコード生成サービス"""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        logo_path: Optional[str] = None,
    ):
        """
        初期化

        Args:
          base_url: レシピ共有用のベースURL
          logo_path: QRコード中央に埋め込むロゴ画像のパス
        """
        self.base_url = base_url.rstrip("/")
        self.logo_path = logo_path

    def generate_recipe_url(self, recipe_id: int) -> str:
        """
        レシピ共有URLを生成

        Args:
          recipe_id: レシピID

        Returns:
          共有URL
        """
        return f"{self.base_url}/recipe/{recipe_id}"

    def generate_recipe_data(self, recipe_id: int, recipe_data: Dict[str, Any]) -> str:
        """
        レシピデータをコンパクトJSONに変換

        Args:
          recipe_id: レシピID
          recipe_data: レシピデータ

        Returns:
          JSON文字列
        """
        compact_data = {
            "id": recipe_id,
            "name": recipe_data.get("name", ""),
            "url": recipe_data.get("url", ""),
            "ingredients": recipe_data.get("ingredients", []),
            "steps": recipe_data.get("steps", []),
        }
        return json.dumps(compact_data, ensure_ascii=False, separators=(",", ":"))

    def create_qrcode(
        self,
        data: str,
        version: Optional[int] = None,
        error_correction: int = qrcode.constants.ERROR_CORRECT_H,
        box_size: int = 10,
        border: int = 4,
        fill_color: str = "black",
        back_color: str = "white",
        style: Literal["square", "rounded", "circle"] = "square",
    ) -> qrcode.QRCode:
        """
        QRCodeオブジェクトを生成

        Args:
          data: QRコードに埋め込むデータ
          version: QRコードのバージョン（1-40、Noneで自動）
          error_correction: エラー訂正レベル
          box_size: 各ボックスのピクセルサイズ
          border: ボーダーの幅（ボックス数）
          fill_color: QRコードの色
          back_color: 背景色
          style: QRコードのスタイル

        Returns:
          QRCodeオブジェクト
        """
        qr = qrcode.QRCode(
            version=version,
            error_correction=error_correction,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        return qr

    def _add_logo_to_image(
        self, qr_image: Image.Image, logo_path: str, logo_size_ratio: float = 0.3
    ) -> Image.Image:
        """
        QRコード画像にロゴを埋め込む

        Args:
          qr_image: QRコード画像
          logo_path: ロゴ画像のパス
          logo_size_ratio: QRコードサイズに対するロゴサイズの比率

        Returns:
          ロゴ埋め込み済みQRコード画像
        """
        logo = Image.open(logo_path)

        # ロゴサイズを計算
        qr_width, qr_height = qr_image.size
        logo_max_size = int(min(qr_width, qr_height) * logo_size_ratio)

        # ロゴをリサイズ（アスペクト比維持）
        logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)

        # ロゴの背景を白くする（透明度対応）
        logo_bg = Image.new("RGB", logo.size, "white")
        if logo.mode == "RGBA":
            logo_bg.paste(logo, mask=logo.split()[3])
        else:
            logo_bg.paste(logo)

        # ロゴを中央に配置
        logo_pos = (
            (qr_width - logo_bg.width) // 2,
            (qr_height - logo_bg.height) // 2,
        )
        qr_image.paste(logo_bg, logo_pos)

        return qr_image

    def generate_qrcode_image(
        self,
        data: str,
        version: Optional[int] = None,
        box_size: int = 10,
        border: int = 4,
        fill_color: str = "black",
        back_color: str = "white",
        style: Literal["square", "rounded", "circle"] = "square",
        add_logo: bool = False,
        logo_path: Optional[str] = None,
    ) -> Image.Image:
        """
        QRコード画像（PIL Image）を生成

        Args:
          data: QRコードに埋め込むデータ
          version: QRコードのバージョン
          box_size: 各ボックスのピクセルサイズ
          border: ボーダーの幅
          fill_color: QRコードの色
          back_color: 背景色
          style: QRコードのスタイル
          add_logo: ロゴを埋め込むかどうか
          logo_path: ロゴ画像のパス

        Returns:
          PIL Image オブジェクト
        """
        qr = self.create_qrcode(
            data=data,
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
        )

        # スタイルに応じた画像生成
        if style == "rounded":
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                color_mask=SolidFillColorMask(
                    back_color=back_color, front_color=fill_color
                ),
            )
        elif style == "circle":
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=CircleModuleDrawer(),
                color_mask=SolidFillColorMask(
                    back_color=back_color, front_color=fill_color
                ),
            )
        else:
            img = qr.make_image(fill_color=fill_color, back_color=back_color)

        # PIL Imageに変換
        if not isinstance(img, Image.Image):
            img = img.convert("RGB")

        # ロゴ埋め込み
        if add_logo:
            logo_file = logo_path or self.logo_path
            if logo_file and Path(logo_file).exists():
                img = self._add_logo_to_image(img, logo_file)

        return img

    def generate_qrcode_png_bytes(
        self,
        data: str,
        version: Optional[int] = None,
        box_size: int = 10,
        border: int = 4,
        fill_color: str = "black",
        back_color: str = "white",
        style: Literal["square", "rounded", "circle"] = "square",
        add_logo: bool = False,
        logo_path: Optional[str] = None,
    ) -> bytes:
        """
        QRコード画像をPNGバイトデータとして生成

        Args:
          data: QRコードに埋め込むデータ
          version: QRコードのバージョン
          box_size: 各ボックスのピクセルサイズ
          border: ボーダーの幅
          fill_color: QRコードの色
          back_color: 背景色
          style: QRコードのスタイル
          add_logo: ロゴを埋め込むかどうか
          logo_path: ロゴ画像のパス

        Returns:
          PNGバイトデータ
        """
        img = self.generate_qrcode_image(
            data=data,
            version=version,
            box_size=box_size,
            border=border,
            fill_color=fill_color,
            back_color=back_color,
            style=style,
            add_logo=add_logo,
            logo_path=logo_path,
        )

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def generate_qrcode_svg(
        self,
        data: str,
        version: Optional[int] = None,
        box_size: int = 10,
        border: int = 4,
        fill_color: str = "black",
        back_color: str = "white",
    ) -> str:
        """
        QRコード画像をSVG形式で生成

        Args:
          data: QRコードに埋め込むデータ
          version: QRコードのバージョン
          box_size: 各ボックスのピクセルサイズ
          border: ボーダーの幅
          fill_color: QRコードの色
          back_color: 背景色

        Returns:
          SVG文字列
        """
        import qrcode.image.svg

        factory = qrcode.image.svg.SvgPathImage

        qr = self.create_qrcode(
            data=data,
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
        )

        img = qr.make_image(
            image_factory=factory,
            fill_color=fill_color,
            back_color=back_color,
        )

        buffer = io.BytesIO()
        img.save(buffer)
        return buffer.getvalue().decode("utf-8")

    def generate_recipe_qrcode_url(
        self,
        recipe_id: int,
        format: Literal["png", "svg"] = "png",
        box_size: int = 10,
        border: int = 4,
        fill_color: str = "black",
        back_color: str = "white",
        style: Literal["square", "rounded", "circle"] = "square",
        add_logo: bool = False,
        logo_path: Optional[str] = None,
    ) -> bytes | str:
        """
        レシピ共有URL用QRコードを生成（URLモード）

        Args:
          recipe_id: レシピID
          format: 出力形式（png/svg）
          box_size: 各ボックスのピクセルサイズ
          border: ボーダーの幅
          fill_color: QRコードの色
          back_color: 背景色
          style: QRコードのスタイル
          add_logo: ロゴを埋め込むかどうか
          logo_path: ロゴ画像のパス

        Returns:
          PNG bytes または SVG文字列
        """
        url = self.generate_recipe_url(recipe_id)

        if format == "svg":
            return self.generate_qrcode_svg(
                data=url,
                box_size=box_size,
                border=border,
                fill_color=fill_color,
                back_color=back_color,
            )
        else:
            return self.generate_qrcode_png_bytes(
                data=url,
                box_size=box_size,
                border=border,
                fill_color=fill_color,
                back_color=back_color,
                style=style,
                add_logo=add_logo,
                logo_path=logo_path,
            )

    def generate_recipe_qrcode_data(
        self,
        recipe_id: int,
        recipe_data: Dict[str, Any],
        format: Literal["png", "svg"] = "png",
        box_size: int = 10,
        border: int = 4,
        fill_color: str = "black",
        back_color: str = "white",
        style: Literal["square", "rounded", "circle"] = "square",
        add_logo: bool = False,
        logo_path: Optional[str] = None,
    ) -> bytes | str:
        """
        レシピデータ用QRコードを生成（データモード）

        Args:
          recipe_id: レシピID
          recipe_data: レシピデータ
          format: 出力形式（png/svg）
          box_size: 各ボックスのピクセルサイズ
          border: ボーダーの幅
          fill_color: QRコードの色
          back_color: 背景色
          style: QRコードのスタイル
          add_logo: ロゴを埋め込むかどうか
          logo_path: ロゴ画像のパス

        Returns:
          PNG bytes または SVG文字列
        """
        data = self.generate_recipe_data(recipe_id, recipe_data)

        if format == "svg":
            return self.generate_qrcode_svg(
                data=data,
                box_size=box_size,
                border=border,
                fill_color=fill_color,
                back_color=back_color,
            )
        else:
            return self.generate_qrcode_png_bytes(
                data=data,
                box_size=box_size,
                border=border,
                fill_color=fill_color,
                back_color=back_color,
                style=style,
                add_logo=add_logo,
                logo_path=logo_path,
            )
