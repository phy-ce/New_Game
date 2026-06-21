# New Game — 온라인 2인 대전 카드 게임

[English](README.md) · [日本語](README.ja.md) · **한국어**

[도미니언(Dominion)](https://ko.wikipedia.org/wiki/%EB%8F%84%EB%AF%B8%EB%8B%88%EC%96%B8)
에서 영감을 받은 실시간 2인 대전 웹 카드 게임입니다.
두 플레이어가 브라우저로 같은 로비에 입장해 실시간으로 대전합니다.
덱을 만들고, 에너지를 써서 카드를 내고, 공용 마켓에서 카드를 사고, 유닛을 소환해
상대의 HP를 0으로 만들면 승리합니다.

> ⚠️ **상태:** 두 명이 함께 만든 사이드 프로젝트로, 2026년에 개발했고 2026년 4월에 개발을 중단했습니다.
> 동작하는 프로토타입이며, 운영 환경용으로 견고화된 서비스는 아닙니다
> (인증 없음, 상태는 메모리에만 저장).

---

## ✨ 특징

- **실시간 1대1 대전** — WebSocket으로 모든 행동이 양쪽 플레이어에게 즉시 브로드캐스트됩니다.
- **덱 빌딩 게임플레이** — 작은 덱으로 시작해 매 턴 새 카드를 구매합니다.
- **전술적 전투 레이어** — 에너지 비용, 방어(block), 공격력(strength),
  지속 피해 계열 상태이상(*burn / plate armour / thorn / growth / arson*).
- **필드 유닛과 챔피언** — 매 턴 공격하는 지속 유닛이며, 일부는 피해를 흡수합니다.
- **세 종류의 상점** — 기본 마켓, 교체되는 **레어** 마켓, 그리고 패시브 강화를 위한 **유물(relic)** 마켓.
- **로비 시스템** — 게임을 만들면 6자리 코드가 발급되고, 이를 공유하면 상대가 입장합니다.
- **자동 재접속** — 새로고침하거나 연결이 끊겨도 같은 게임에 다시 들어갈 수 있습니다
  (이름 + 코드를 `localStorage`에 저장).
- **플레이어별 상태 전송** — 서버는 각 플레이어가 볼 수 있는 정보만 보냅니다
  (내 손패는 상대에게 보이지 않음).

---

## 🛠️ 기술 스택

| 레이어 | 기술 |
|-------|-----------|
| **백엔드** | Python 3.12+, [Flask](https://flask.palletsprojects.com/) 3.1, [Flask-SocketIO](https://flask-socketio.readthedocs.io/) 5.6, [eventlet](https://eventlet.readthedocs.io/) |
| **프런트엔드** | JavaScript, [React](https://react.dev/) 19, [Vite](https://vite.dev/) 8, [socket.io-client](https://socket.io/) 4.8 |
| **통신** | WebSocket (실시간 양방향) |
| **상태 관리** | 메모리 내 Python dict (데이터베이스 없음) |
| **도구** | [uv](https://docs.astral.sh/uv/) (Python 의존성), npm (프런트엔드) |

---

## 🏗️ 아키텍처

서버는 전체 게임 상태를 메모리에 보관하고, **행동이 일어날 때마다 (플레이어별로 필터링된)
전체 상태를 브로드캐스트**합니다 (변경분만 보내지 않음). React 클라이언트는 가장 최신 상태를
그대로 렌더링합니다. 덕분에 클라이언트는 가벼워지고, 서버가 신뢰할 수 있는 단일 권한
(authoritative) 주체가 됩니다.

```
┌───────────┐   WebSocket    ┌──────────────────┐
│ 브라우저 A │ ◀────────────▶ │  Flask +         │
└───────────┘   game_state   │  Flask-SocketIO  │   메모리 내
┌───────────┐   브로드캐스트   │  (eventlet)      │   games = { CODE: {...} }
│ 브라우저 B │ ◀────────────▶ │                  │
└───────────┘                └──────────────────┘
```

### 프로젝트 구조

```
backend/
  run.py                       # 진입점 — 포트 5000에서 socketio.run
  pyproject.toml               # uv로 관리하는 의존성
  app/
    __init__.py                # 앱 팩토리. 빌드된 SPA와 템플릿용 REST 엔드포인트 제공
    models/
      cards.py                 # 카드 템플릿, 시작 덱·마켓 생성
      units.py                 # 필드 유닛 템플릿
      relics.py                # 유물 템플릿과 유물 마켓
    services/
      game_manager.py          # 로비: 생성/참가/재접속, 메모리 내 games dict
      game_logic.py            # start_game, play_card, buy_card/rare/relic, resolve_choice, end_turn
      effects.py               # 카드/유물 효과, 피해 및 상태이상 처리
      serializer.py            # 플레이어별 상태 필터링 (상대 손패·덱 숨김)
    sockets/
      __init__.py              # 핸들러 등록
      lobby.py                 # create_game, join_game, reconnect_game
      game.py                  # 게임 진행 이벤트 + broadcast_state
      debug.py                 # 디버그 전용 이벤트

frontend/
  vite.config.js               # 개발 프록시: /socket.io (ws)와 /api → Flask :5000
  index.html
  src/
    main.jsx, App.jsx
    context/GameContext.jsx    # 로비 코드, 플레이어 이름, 게임 상태, 오류
    hooks/useSocket.jsx        # 단일 소켓 연결과 모든 emit 래퍼
    pages/
      LobbyPage.jsx            # 생성 / 참가 / 재접속 / 대기 화면
      GamePage.jsx             # 게임 보드 구성
    components/                # Card, Hand, Market, Field, UnitCard, PlayArea,
                               # TurnStats, PlayerInfo, DeckPile, DiscardPile,
                               # GameLog, ChoiceModal, FloatingDamage, ...
    styles/                    # 컴포넌트별 CSS

dev.sh                         # 편의 스크립트: 백엔드와 프런트엔드를 함께 실행
```

---

## 🚀 시작하기

### 사전 준비물

- **Python 3.12+** 와 [**uv**](https://docs.astral.sh/uv/getting-started/installation/)
- **Node.js** (npm 포함)

### 방법 A — 한 번에 실행 (권장)

프로젝트 루트에서:

```bash
./dev.sh
```

백엔드(Flask `:5000`)와 프런트엔드(Vite `:5173`)를 함께 띄웁니다.
기존에 실행 중인 프로세스가 있으면 먼저 종료합니다. 코드 수정 후 다시 실행하면 됩니다.

> `dev.sh` 는 Bash 스크립트입니다. Linux / macOS / WSL / Git Bash 에서 실행하세요.

### 방법 B — 터미널 두 개 (수동)

```bash
# 터미널 1 — 백엔드
cd backend
uv run python run.py

# 터미널 2 — 프런트엔드 (핫 리로드)
cd frontend
npm install      # 최초 1회만
npm run dev
```

**http://localhost:5173** 을 엽니다. Vite가 WebSocket과 `/api` 요청을 Flask(`:5000`)로 프록시합니다.

### 프로덕션 빌드

프런트엔드를 빌드하면 Flask가 하나의 포트에서 모든 것을 제공합니다:

```bash
cd frontend && npm run build      # frontend/dist 에 출력
cd ../backend && uv run python run.py
```

**http://localhost:5000** 을 엽니다. 빌드된 SPA와 WebSocket이 동일 출처(origin)에서 제공됩니다.

> 환경 변수로 설정 가능: `PORT`(기본값 `5000`)와 `FLASK_DEBUG`(`true`/`false`).

---

## 🎮 플레이 방법

1. **플레이어 1** 이 앱을 열고 게임을 생성 → **6자리 로비 코드**를 받습니다.
2. **플레이어 2** 가 같은 화면에서 그 코드를 입력해 참가합니다.
3. 두 명이 모두 들어오면 둘 중 한 명이 게임을 시작합니다.
4. 내 턴: 에너지를 얻고 손패를 뽑은 뒤 **카드를 내고**(에너지 소모), 마켓에서
   **구매**(골드 소모)한 다음 **턴을 종료**합니다.
5. 먼저 상대의 HP를 **0** 으로 만든 쪽이 승리합니다.

### 게임 메커니즘 (요약)

- **HP와 승리 조건** — 각 플레이어는 80 HP로 시작. 상대를 0으로 만들면 승리.
- **에너지** — 매 턴 회복. 대부분의 액션 카드는 사용 시 에너지를 소모합니다.
- **골드와 구매** — 보물 카드(Copper / Silver / Gold)가 골드를 만들어 카드와 유물을 구매합니다.
- **상태이상** — block, strength, burn, plate armour, thorn, growth, arson.
- **필드 유닛과 챔피언** — 매 턴 공격하는 지속 유닛이며, 일부는 들어오는 피해를 흡수합니다.
- **마켓** — 기본 마켓, 레어 마켓, 유물(패시브 강화) 마켓.
- **덱 순환** — 덱 → 손패 → 사용 → 버린 더미. 덱이 떨어지면 다시 섞습니다.

---

## 🔌 WebSocket API

| 방향 | 이벤트 |
|-----------|--------|
| 클라이언트 → 서버 | `create_game`, `join_game`, `reconnect_game`, `start_game`, `play_card`, `buy_card`, `buy_rare_card`, `buy_relic`, `resolve_choice`, `end_turn` |
| 서버 → 클라이언트 | `game_created`, `game_joined`, `lobby_ready`, `game_state`, `state_updated`, `error` |

카드 이미지와 메타데이터를 불러오기 위한 읽기 전용 REST 엔드포인트도 있습니다:
`/api/card-templates`, `/api/unit-templates`, `/api/relic-templates`, `/api/passive-info`.

---

## 👥 만든 사람 · 참고

- **[@phy-ce](https://github.com/phy-ce)** 와 **[@jather](https://github.com/jather)** 가 개발했습니다.
- **[Claude Code](https://claude.com/claude-code)** 를 활용해 개발했습니다.
- 공개 전환일: **2026-06-22**.

---

[English](README.md) · [日本語](README.ja.md) · **한국어**
