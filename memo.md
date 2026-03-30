# Memo

## #001 디버그 소켓 이벤트 — 보안 취약점

`debug_cmd` 소켓 이벤트는 인증 없이 누구나 실행할 수 있다. 현재 서버에는 인증 시스템이 없기 때문에, 상대 플레이어가 브라우저 콘솔에서 `debug_cmd`를 직접 emit하면 자기 골드를 99로 올리거나, 상대에게 즉사 데미지를 넣는 등 게임을 마음대로 조작할 수 있다.

현재는 로컬 테스트 전용이라 문제없지만, 외부 배포 시 반드시 아래 중 하나를 적용해야 한다:
- 디버그 핸들러 자체를 제거하거나 환경변수 플래그로 비활성화
- 관리자 인증(토큰, 비밀번호 등)을 추가하여 일반 플레이어가 호출 못하게 차단

## #002 디버그 소켓 사용법

브라우저 콘솔에서 `debug_cmd` 소켓 이벤트로 게임 상태를 조작할 수 있다.

### 사용법

```js
// 카드 손패에 추가 (cid로 지정)
socket.emit('debug_cmd', {lobby_code: "ABCD", cmd: "add_card", cid: 6})

// 플레이어 스탯 변경 (hp, max_hp, energy, max_energy, gold, block, strength)
socket.emit('debug_cmd', {lobby_code: "ABCD", cmd: "set_stat", stat: "gold", value: 99})

// 상대에게 데미지
socket.emit('debug_cmd', {lobby_code: "ABCD", cmd: "deal_damage", amount: 25})
```

### 카드 cid 목록

`cid_table.csv` 참고.
