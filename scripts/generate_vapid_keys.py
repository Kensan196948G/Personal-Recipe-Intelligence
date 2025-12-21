#!/usr/bin/env python3
"""
VAPID Keys Generator
Web Push用のVAPIDキーペアを生成するスクリプト
"""

import sys
import os
from pathlib import Path

try:
  from py_vapid import Vapid
except ImportError:
  print("Error: py-vapid is not installed")
  print("Please install it with: pip install py-vapid")
  sys.exit(1)


def generate_vapid_keys(output_dir: str = None):
  """
  VAPIDキーペアを生成して保存

  Args:
    output_dir: 出力ディレクトリ（デフォルト: config/）
  """
  # 出力ディレクトリの設定
  if output_dir is None:
    # スクリプトの親ディレクトリ（プロジェクトルート）を取得
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "config"
  else:
    output_dir = Path(output_dir)

  # ディレクトリが存在しない場合は作成
  output_dir.mkdir(parents=True, exist_ok=True)

  # VAPIDキーペアを生成
  vapid = Vapid()
  vapid.generate_keys()

  # 秘密鍵と公開鍵を取得
  private_key = vapid.private_key.private_bytes(
    encoding=vapid.private_key.private_bytes.__func__.__defaults__[0],
    format=vapid.private_key.private_bytes.__func__.__defaults__[1],
    encryption_algorithm=vapid.private_key.private_bytes.__func__.__defaults__[
      2
    ],
  )

  # より簡単な方法で鍵を取得
  private_key_pem = vapid.private_pem()
  public_key_urlsafe = vapid.public_key.public_bytes_urlsafe_base64()

  # ファイルに保存
  private_key_file = output_dir / "vapid_private_key.pem"
  public_key_file = output_dir / "vapid_public_key.txt"

  # 秘密鍵を保存（PEM形式）
  with open(private_key_file, "wb") as f:
    f.write(private_key_pem)

  # 公開鍵を保存（Base64 URL-safe形式）
  with open(public_key_file, "w") as f:
    f.write(public_key_urlsafe)

  # パーミッションを設定（秘密鍵は読み取り専用）
  os.chmod(private_key_file, 0o600)
  os.chmod(public_key_file, 0o644)

  print("✓ VAPID keys generated successfully!")
  print(f"\nPrivate key saved to: {private_key_file}")
  print(f"Public key saved to: {public_key_file}")
  print(f"\nPublic key (for frontend):")
  print(f"  {public_key_urlsafe}")
  print(f"\n⚠️  IMPORTANT:")
  print(
    f"  - Keep the private key ({private_key_file.name}) secret and secure!"
  )
  print(f"  - Add {private_key_file.name} to .gitignore")
  print(
    f"  - Use the public key ({public_key_urlsafe}) in your frontend application"
  )

  # .env ファイルのサンプルを出力
  print(f"\n📝 Add these to your .env file:")
  print(f"VAPID_PRIVATE_KEY_FILE=config/vapid_private_key.pem")
  print(f"VAPID_PUBLIC_KEY={public_key_urlsafe}")
  print(f"VAPID_CLAIM_EMAIL=mailto:your-email@example.com")

  # .gitignore に追加する内容を提案
  gitignore_file = output_dir.parent / ".gitignore"
  if gitignore_file.exists():
    with open(gitignore_file, "r") as f:
      gitignore_content = f.read()

    if "vapid_private_key.pem" not in gitignore_content:
      print(f"\n📝 Add to .gitignore:")
      print(f"config/vapid_private_key.pem")


def main():
  """メイン関数"""
  import argparse

  parser = argparse.ArgumentParser(
    description="Generate VAPID keys for Web Push notifications"
  )
  parser.add_argument(
    "-o",
    "--output",
    type=str,
    default=None,
    help="Output directory (default: config/)",
  )

  args = parser.parse_args()

  try:
    generate_vapid_keys(output_dir=args.output)
  except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
  main()
