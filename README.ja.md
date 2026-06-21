# New Game — オンライン2人対戦カードゲーム

[English](README.md) · **日本語** · [한국어](README.ko.md)

[Dominion（ドミニオン）](https://ja.wikipedia.org/wiki/%E3%83%89%E3%83%9F%E3%83%8B%E3%82%AA%E3%83%B3)
にインスパイアされた、リアルタイム2人対戦のWebカードゲームです。
2人のプレイヤーが同じロビーにブラウザから参加し、リアルタイムで対戦します。
デッキを構築し、エネルギーを消費してカードをプレイし、共有マーケットから購入し、
ユニットを召喚して、相手のHPを0にすれば勝利です。

> ⚠️ **ステータス:** 個人のポートフォリオ用プロジェクトで、2026年に開発し2026年4月に開発を停止しました。
> 動作するプロトタイプであり、本番運用向けに堅牢化されたサービスではありません
> （認証なし・状態はメモリ上のみ）。フルスタックとリアルタイム構成のデモが目的です。

---

## ✨ 特徴

- **リアルタイム1対1対戦** — WebSocket経由で、すべての操作が両プレイヤーに即時ブロードキャストされます。
- **デッキ構築型のゲーム性** — 小さなデッキから始め、毎ターン新しいカードを購入します。
- **戦術的な戦闘レイヤー** — エネルギーコスト、ブロック、攻撃力（strength）、
  継続ダメージ系の状態異常（*burn / plate armour / thorn / growth / arson*）。
- **フィールドユニットとチャンピオン** — 毎ターン攻撃する永続ユニット。ダメージを吸収するものもあります。
- **3種類の供給元** — 基本マーケット、入れ替わる**レア**マーケット、パッシブ強化用の**レリック**マーケット。
- **ロビーシステム** — ゲームを作成すると6文字のコードが発行され、共有して相手が参加します。
- **自動再接続** — 更新や切断後も同じゲームに再参加できます（名前＋コードを`localStorage`に保存）。
- **プレイヤーごとの状態** — サーバーは各プレイヤーが見てよい情報のみを送信します
  （自分の手札は相手から見えません）。

---

## 🛠️ 技術スタック

| レイヤー | 技術 |
|-------|-----------|
| **バックエンド** | Python 3.12+、[Flask](https://flask.palletsprojects.com/) 3.1、[Flask-SocketIO](https://flask-socketio.readthedocs.io/) 5.6、[eventlet](https://eventlet.readthedocs.io/) |
| **フロントエンド** | JavaScript、[React](https://react.dev/) 19、[Vite](https://vite.dev/) 8、[socket.io-client](https://socket.io/) 4.8 |
| **通信** | WebSocket（リアルタイム・双方向） |
| **状態管理** | メモリ上のPython dict（データベースなし） |
| **ツール** | [uv](https://docs.astral.sh/uv/)（Python依存関係）、npm（フロントエンド） |

---

## 🏗️ アーキテクチャ

サーバーはゲーム状態全体をメモリ上に保持し、**操作のたびに（プレイヤーごとにフィルタした）
完全な状態をブロードキャスト**します（差分送信はありません）。Reactクライアントは
最新の状態をそのまま描画します。これによりクライアントは薄く、サーバーが信頼できる
唯一の情報源（authoritative）になります。

```
┌───────────┐   WebSocket    ┌──────────────────┐
│ ブラウザA  │ ◀────────────▶ │  Flask +         │
└───────────┘   game_state   │  Flask-SocketIO  │   メモリ上
┌───────────┐   ブロードキャスト │  (eventlet)      │   games = { CODE: {...} }
│ ブラウザB  │ ◀────────────▶ │                  │
└───────────┘                └──────────────────┘
```

### プロジェクト構成

```
backend/
  run.py                       # エントリポイント — ポート5000でsocketio.run
  pyproject.toml               # uvで管理する依存関係
  app/
    __init__.py                # アプリファクトリ。ビルド済みSPAとテンプレート用RESTを提供
    models/
      cards.py                 # カードテンプレート、初期デッキ・マーケット生成
      units.py                 # フィールドユニットのテンプレート
      relics.py                # レリックのテンプレートとレリックマーケット
    services/
      game_manager.py          # ロビー: 作成/参加/再接続、メモリ上のgames dict
      game_logic.py            # start_game, play_card, buy_card/rare/relic, resolve_choice, end_turn
      effects.py               # カード/レリックの効果、ダメージと状態異常の処理
      serializer.py            # プレイヤーごとの状態フィルタ（相手の手札・山札を隠す）
    sockets/
      __init__.py              # ハンドラ登録
      lobby.py                 # create_game, join_game, reconnect_game
      game.py                  # ゲーム進行イベント + broadcast_state
      debug.py                 # デバッグ専用イベント

frontend/
  vite.config.js               # 開発用プロキシ: /socket.io (ws) と /api → Flask :5000
  index.html
  src/
    main.jsx, App.jsx
    context/GameContext.jsx    # ロビーコード、プレイヤー名、ゲーム状態、エラー
    hooks/useSocket.jsx        # 単一のソケット接続とすべてのemitラッパー
    pages/
      LobbyPage.jsx            # 作成 / 参加 / 再接続 / 待機画面
      GamePage.jsx             # ゲーム盤面の組み立て
    components/                # Card, Hand, Market, Field, UnitCard, PlayArea,
                               # TurnStats, PlayerInfo, DeckPile, DiscardPile,
                               # GameLog, ChoiceModal, FloatingDamage, ...
    styles/                    # コンポーネントごとのCSS

dev.sh                         # 便利スクリプト: バックエンドとフロントエンドを同時起動
```

---

## 🚀 はじめに

### 前提条件

- **Python 3.12+** と [**uv**](https://docs.astral.sh/uv/getting-started/installation/)
- **Node.js**（npm 付き）

### 方法A — ワンコマンド（推奨）

プロジェクトルートで:

```bash
./dev.sh
```

バックエンド（Flask `:5000`）とフロントエンド（Vite `:5173`）を同時に起動します。
既存のプロセスがあれば先に終了します。コード変更後は再実行してください。

> `dev.sh` はBashスクリプトです。Linux / macOS / WSL / Git Bash から実行してください。

### 方法B — 2つのターミナル（手動）

```bash
# ターミナル1 — バックエンド
cd backend
uv run python run.py

# ターミナル2 — フロントエンド（ホットリロード）
cd frontend
npm install      # 初回のみ
npm run dev
```

**http://localhost:5173** を開きます。ViteがWebSocketと`/api`をFlask（`:5000`）にプロキシします。

### 本番ビルド

フロントエンドをビルドすると、Flaskが1つのポートからすべてを配信します:

```bash
cd frontend && npm run build      # frontend/dist に出力
cd ../backend && uv run python run.py
```

**http://localhost:5000** を開きます。ビルド済みSPAとWebSocketが同一オリジンで配信されます。

> 環境変数で設定可能: `PORT`（既定 `5000`）と `FLASK_DEBUG`（`true`/`false`）。

---

## 🎮 遊び方

1. **プレイヤー1** がアプリを開いてゲームを作成 → **6文字のロビーコード**を受け取ります。
2. **プレイヤー2** が同じ画面でそのコードを入力して参加します。
3. 2人が揃ったら、どちらかがゲームを開始します。
4. 自分のターン: エネルギーを得て手札を引き、**カードをプレイ**（エネルギー消費）し、
   マーケットから**購入**（ゴールド消費）して、**ターンを終了**します。
5. 先に相手のHPを **0** にしたほうが勝ちです。

### ゲームの仕組み（概要）

- **HPと勝利条件** — 各プレイヤーは80HPで開始。相手を0にすれば勝利。
- **エネルギー** — 毎ターン回復。多くのアクションカードはプレイにエネルギーを消費します。
- **ゴールドと購入** — トレジャーカード（Copper / Silver / Gold）がゴールドを生み、カードやレリックを購入します。
- **状態異常** — block, strength, burn, plate armour, thorn, growth, arson。
- **フィールドユニットとチャンピオン** — 毎ターン攻撃する永続ユニット。被ダメージを吸収するものもあります。
- **マーケット** — 基本マーケット、レアマーケット、レリック（パッシブ強化）マーケット。
- **デッキの循環** — 山札 → 手札 → プレイ → 捨て札。山札が尽きたら再シャッフル。

---

## 🔌 WebSocket API

| 方向 | イベント |
|-----------|--------|
| クライアント → サーバー | `create_game`, `join_game`, `reconnect_game`, `start_game`, `play_card`, `buy_card`, `buy_rare_card`, `buy_relic`, `resolve_choice`, `end_turn` |
| サーバー → クライアント | `game_created`, `game_joined`, `lobby_ready`, `game_state`, `state_updated`, `error` |

カードの画像やメタデータを読み込むための読み取り専用RESTエンドポイントもあります:
`/api/card-templates`, `/api/unit-templates`, `/api/relic-templates`, `/api/passive-info`。

---

## 👥 作者・備考

- **[@phy-ce](https://github.com/phy-ce)** と **[@jather](https://github.com/jather)** が開発。
- **[Claude Code](https://claude.com/claude-code)** を活用して開発しました。
  リポジトリの規約は [`CLAUDE.md`](CLAUDE.md) を参照してください。
- 公開日: **2026-06-22**。

---

[English](README.md) · **日本語** · [한국어](README.ko.md)
