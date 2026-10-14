
# Local AI Chat

Python / Django / Ollamaを使用して開発した、ローカル環境で動作するAIチャットWebアプリケーションです。

Windows 11とWSL2上に開発環境を構築し、ローカルLLMとの通信、会話履歴の管理、ログイン認証などを実装しました。

## 主な機能

- ローカルLLM（Qwen3）とのチャット
- AIの回答をリアルタイムに表示（ストリーミング）
- SQLiteによる会話履歴の保存
- 会話の新規作成・切り替え・削除
- 会話タイトルの編集・自動生成
- ユーザーのログイン・ログアウト
- スマートフォン対応のレスポンシブデザイン
- Caddyを利用したローカルネットワーク内のHTTPS接続

## 使用技術

### バックエンド
- Python
- Django
- SQLite

### フロントエンド
- HTML
- CSS
- JavaScript

### AI・開発環境
- Ollama
- Qwen3 4B Instruct
- Windows 11
- WSL2 / Ubuntu
- Visual Studio Code
- Caddy
- Git

## システム構成

ブラウザからDjangoにリクエストを送り、DjangoがOllama APIを通じてローカルLLMと通信します。

AIの回答はストリーミング形式でブラウザに表示し、会話履歴はSQLiteに保存します。

HTTPS接続にはCaddyをリバースプロキシとして使用しています。

## 開発で取り組んだこと

- DjangoによるWebアプリケーションの構築
- JavaScriptのFetch APIを使ったストリーミング表示
- データベースを利用した会話履歴管理
- Django標準認証によるアクセス制限
- PC・スマートフォン向けの画面調整
- WindowsとWSL2間のネットワーク連携
- HTTPS証明書を利用したローカル通信の暗号化

## 動作環境と注意事項

本アプリケーションは個人開発・ローカルネットワーク内での利用を想定しています。

現在はDjangoの開発用サーバーを使用しており、インターネット上での公開運用は想定していません。

会話履歴、秘密鍵、個人の環境設定ファイルはGitの管理対象から除外しています。

## 今後の改善予定

- 環境設定の整理
- セットアップ手順の整備
- 自動テストの追加
- コードの整理と保守性の改善

## セットアップ

### 前提条件

- Pythonとpipが使用できること
- Ollamaがインストールされていること
- Ollamaに `qwen3:4b-instruct` モデルが導入されていること
- DjangoからOllama API（`http://localhost:11434`）へ接続できること

開発時はWindows 11とWSL2 Ubuntuを使用し、OllamaをWindows側、DjangoをWSL2側で実行しています。

WSL2からWindows側のOllamaへ接続するため、WSL2のmirroredネットワークモードを利用しています。

### Python環境の準備（WSL2 Ubuntu）

プロジェクトのルートディレクトリで、以下を実行します。

```bash
# 仮想環境を作成
python3 -m venv ~/.venvs/local_ai

# 仮想環境を有効化
source ~/.venvs/local_ai/bin/activate

# 必要なライブラリをインストール
python -m pip install -r requirements.txt

# Djangoの設定ファイルを作成
cp config/settings.example.py config/settings.py
```

仮想環境はプロジェクト外のホームディレクトリに作成します。

`settings.py` はGitの管理対象から除外されています。次の手順で秘密鍵などの環境設定を行います。

### Djangoの環境変数

Djangoの秘密鍵はソースコードに直接記述せず、環境変数で管理します。

仮想環境を有効にしたUbuntuのターミナルで、以下を実行します。

```bash
# Djangoの秘密鍵を生成して環境変数に設定
export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"

# 開発用のデバッグ設定
export DJANGO_DEBUG=True
```

秘密鍵は実行時に自動生成されるため、GitHubに登録する必要はありません。

これらの環境変数は現在のターミナルセッションでのみ有効です。新しいターミナルを開いた場合は再設定が必要です。

`DJANGO_DEBUG=True` はローカル開発用です。外部公開する環境では使用しないでください。

### データベースの初期化

Djangoの設定と環境変数を準備したら、以下を実行します。

```bash
# データベースを作成
python manage.py migrate

# ログイン用の管理者アカウントを作成
python manage.py createsuperuser
```

ユーザー名とパスワードは、画面の案内に従って設定してください。

### Djangoの起動

Windows側でOllamaが起動していることを確認し、Ubuntuで以下を実行します。

```bash
python manage.py runserver 127.0.0.1:8000
```

ブラウザで次のURLにアクセスします。

http://127.0.0.1:8000/

作成したアカウントでログインすると、AIチャットを利用できます。

この起動方法はローカル開発用です。外部ネットワークへの公開には、別途適切なセキュリティ設定が必要です。

### HTTPS接続（ローカルネットワーク内）

Windows側でCaddyを起動し、HTTPS通信をWSL2上のDjangoへ転送します。

通信の流れ：

ブラウザ → HTTPS → Caddy → Django → Ollama

構成：

- Caddy：Windows 11上で動作
- Django：WSL2 Ubuntu上で動作
- HTTPSポート：8443
- Djangoポート：8000
- 証明書：Caddyのローカル認証局（`tls internal`）を使用

PCでは `https://localhost:8443/` からアクセスできます。

iPhoneでは、同じLAN内のPCのIPv4アドレスを指定して接続します。iPhone側にもCaddyのルート証明書をインストールし、信頼設定を行う必要があります。

Caddyの設定ファイルと秘密鍵はローカル環境で管理し、GitHubには公開しません。

また、Djangoではリバースプロキシ経由のHTTPS通信を認識するため、`SECURE_PROXY_SSL_HEADER` を設定しています。

この構成は個人開発用です。Djangoの開発サーバーをインターネットへ直接公開することは想定していません。

### Caddyのセットアップ

WindowsにCaddyをインストールしたあと、PowerShellでプロジェクトのフォルダを開き、以下を実行します。

```powershell
# 設定ファイルの見本をコピー
Copy-Item Caddyfile.example Caddyfile

# Caddyを起動
caddy run --config .\Caddyfile --adapter caddyfile
```

ブラウザから以下にアクセスします。

https://localhost:8443/

初回起動時は、Caddyが生成するローカル認証局の証明書を信頼する設定が必要です。

iPhoneから利用する場合は、CaddyfileにPCのLAN内IPv4アドレスを追加し、iPhone側でも証明書の信頼設定を行います。

この設定例はローカル開発用であり、インターネットへの公開運用を想定していません。
