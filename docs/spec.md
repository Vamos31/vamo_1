# サッカーチーム運営管理アプリ 仕様書

草サッカー・フットサルチームの幹事が、日程・出欠・会費・成績をまとめて管理するための Web アプリ。
PC ブラウザでの利用を主とする。学習目的で、認証・認可・DB 設計などサーバー側を重視する。

## 1. 技術構成

| 層 | 技術 |
|---|---|
| フロント | Next.js (TypeScript) |
| バックエンド | FastAPI + SQLAlchemy (+ Alembic でマイグレーション) |
| DB | PostgreSQL |
| 実行環境 | Docker Compose |

## 2. 基本方針

- 認証は **メールアドレス + パスワード** のみ。最初から実装する。
- 1 人のユーザーは **複数チームに所属可能**。
- 権限は「ユーザー」ではなく **「チーム内での役割」** で決める。同じ人がチームごとに異なる役割を持てる。
- 役割は 2 種類: **幹事 (admin)** と **選手 (member)**。幹事は 1 チームに複数人いてよい。
- 同じチームのメンバーは同じ画面を見る。役割によって操作ボタンや管理画面の表示が変わる。
- 会費は決済機能を持たず、**収支の記録** (帳簿) として管理する。

## 3. ユーザーの流れ

```
ログイン
  ├─ 所属チームなし → 「チームを作る」or「招待リンクで参加」
  ├─ 所属チーム 1 つ → そのチームのホームへ直行
  └─ 複数所属       → チーム選択画面 → チームのホームへ
```

チーム内の URL は `/teams/{team_id}/...`。API は毎回「ログインユーザーがそのチームのメンバーか」「役割は何か」を検査する。

## 4. 権限表

| 機能 | 選手 | 幹事 | フェーズ |
|---|---|---|---|
| 日程・出欠の閲覧 | ○ | ○ | 1 |
| 自分の出欠回答 (締切前) | ○ | ○ | 1 |
| 日程の作成・編集・削除 | × | ○ | 1 |
| 他メンバーの出欠の代理入力・締切後の変更 | × | ○ | 1 |
| メンバーの招待・役割変更・退会処理 | × | ○ | 1 |
| 試合結果・成績の閲覧 | ○ | ○ | 2 |
| 試合結果・成績の登録 | × | ○ | 2 |
| 自分の会費の支払い状況の閲覧 | ○ | ○ | 2 |
| 収支・全員の会費の管理 | × | ○ | 2 |
| お知らせの閲覧 | ○ | ○ | 3 |
| お知らせの投稿 | × | ○ | 3 |
| 助っ人 (ゲスト) の追加 | × | ○ | 3 |

### 制約

- チームには常に 1 人以上の幹事がいる。最後の幹事は、降格も退会もできない。
- チームを作ったユーザーは最初の幹事になる。
- 自分が所属していないチームのデータは、存在も分からないようにする (403 ではなく 404 を返す)。

## 5. フェーズ

| フェーズ | 内容 |
|---|---|
| **1 (MVP)** | 認証、チーム作成、招待、メンバー管理、日程、出欠 (締切つき) |
| **2** | 会費・収支管理、試合結果・成績 (得点ランキング・出場回数) |
| **3** | お知らせ、助っ人 (ゲスト)、スタメン/フォーメーションボード |

## 6. フェーズ 1 の画面

| 画面 | パス | 内容 | 権限 |
|---|---|---|---|
| ユーザー登録 | `/signup` | 名前・メール・パスワード | 未ログイン |
| ログイン | `/login` | メール・パスワード | 未ログイン |
| チーム選択 | `/teams` | 所属チーム一覧、チーム作成への導線 | ログイン |
| チーム作成 | `/teams/new` | チーム名を入力 | ログイン |
| 招待リンクで参加 | `/invite/{token}` | チーム名を確認して参加 | ログイン |
| チームホーム | `/teams/{id}` | 直近の日程と自分の出欠状況 | メンバー |
| 日程一覧 | `/teams/{id}/events` | 日程の一覧、出欠の回答状況 | メンバー |
| 日程詳細 | `/teams/{id}/events/{eid}` | 出欠回答、参加者一覧と集計 | メンバー |
| 日程作成・編集 | `/teams/{id}/events/new` ほか | 種別・日時・場所・締切を入力 | 幹事 |
| メンバー一覧 | `/teams/{id}/members` | 一覧。幹事は役割変更・退会処理 | メンバー (操作は幹事) |
| 招待リンク管理 | `/teams/{id}/invitations` | 招待リンクの発行・無効化 | 幹事 |

## 7. データモデル (フェーズ 1)

```
users 1 ─── n team_members n ─── 1 teams
  │                                  │
  │                                  └── 1 ─── n invitations
  │                                  │
  └── 1 ─── n attendances n ─── 1 events ─── n ─── 1 teams
```

### users
| カラム | 型 | 備考 |
|---|---|---|
| id | bigint PK | |
| email | text | UNIQUE、小文字に正規化して保存 |
| password_hash | text | argon2 または bcrypt |
| name | text | 表示名 |
| created_at | timestamptz | |

### teams
| カラム | 型 | 備考 |
|---|---|---|
| id | bigint PK | |
| name | text | |
| created_at | timestamptz | |

### team_members
| カラム | 型 | 備考 |
|---|---|---|
| id | bigint PK | |
| team_id | FK teams | |
| user_id | FK users | |
| role | enum('admin','member') | |
| joined_at | timestamptz | |

UNIQUE (team_id, user_id)。退会は物理削除ではなく `left_at` を持たせるか、フェーズ 1 では物理削除にするかを実装時に決める (未決事項)。

### invitations
| カラム | 型 | 備考 |
|---|---|---|
| id | bigint PK | |
| team_id | FK teams | |
| token | text | UNIQUE、推測不能なランダム文字列 |
| created_by | FK users | |
| expires_at | timestamptz | 発行から 7 日 |
| revoked_at | timestamptz null | 無効化した時刻 |

### events
| カラム | 型 | 備考 |
|---|---|---|
| id | bigint PK | |
| team_id | FK teams | |
| type | enum('match','practice','other') | 試合 / 練習 / その他 |
| title | text | |
| starts_at | timestamptz | |
| ends_at | timestamptz null | |
| location | text null | |
| note | text null | |
| attendance_deadline | timestamptz null | 未設定なら締切なし |
| created_by | FK users | |

### attendances
| カラム | 型 | 備考 |
|---|---|---|
| id | bigint PK | |
| event_id | FK events | |
| user_id | FK users | |
| status | enum('yes','maybe','no') | ○ △ × |
| comment | text null | |
| updated_by | FK users | 本人か、代理入力した幹事 |
| updated_at | timestamptz | |

UNIQUE (event_id, user_id)。未回答は行を持たず、「メンバー − 回答済み」で算出する。

## 8. API (フェーズ 1)

認証が必要なものは、すべてログイン済みであることを検査する。`{team_id}` を含むものは、さらにチームのメンバーであることを検査する。

| メソッド | パス | 内容 | 権限 |
|---|---|---|---|
| POST | /auth/signup | ユーザー登録 | 公開 |
| POST | /auth/login | ログイン | 公開 |
| POST | /auth/logout | ログアウト | ログイン |
| GET | /me | ログイン中のユーザー情報 | ログイン |
| GET | /teams | 自分の所属チーム一覧 (役割つき) | ログイン |
| POST | /teams | チーム作成 (作成者を幹事にする) | ログイン |
| GET | /teams/{team_id} | チーム情報と自分の役割 | メンバー |
| GET | /teams/{team_id}/members | メンバー一覧 | メンバー |
| PATCH | /teams/{team_id}/members/{user_id} | 役割変更 | 幹事 |
| DELETE | /teams/{team_id}/members/{user_id} | 退会処理 (自分の脱退は選手も可) | 幹事 / 本人 |
| POST | /teams/{team_id}/invitations | 招待リンク発行 | 幹事 |
| GET | /teams/{team_id}/invitations | 招待リンク一覧 | 幹事 |
| DELETE | /teams/{team_id}/invitations/{id} | 招待リンク無効化 | 幹事 |
| GET | /invitations/{token} | 招待先チーム名の確認 | ログイン |
| POST | /invitations/{token}/accept | 招待を受けて参加 | ログイン |
| GET | /teams/{team_id}/events | 日程一覧 (期間で絞り込み) | メンバー |
| POST | /teams/{team_id}/events | 日程作成 | 幹事 |
| GET | /teams/{team_id}/events/{event_id} | 日程詳細 (出欠の集計つき) | メンバー |
| PATCH | /teams/{team_id}/events/{event_id} | 日程更新 | 幹事 |
| DELETE | /teams/{team_id}/events/{event_id} | 日程削除 | 幹事 |
| PUT | /teams/{team_id}/events/{event_id}/attendances/{user_id} | 出欠の回答・変更 | 本人 (締切前) / 幹事 |

## 9. 認証の方針

- パスワードは argon2 または bcrypt でハッシュ化して保存する。平文では保存・ログ出力しない。
- ログイン後はトークン (JWT またはセッション ID) を **httpOnly Cookie** で保持する。JavaScript から読めないため、XSS で盗まれにくい。
- Cookie 方式にするため、バックエンドの CORS 設定に `allow_credentials=True` が必要になる (現在の [backend/main.py](../backend/main.py) は未設定)。
- 同一メールでの重複登録は拒否する。ログイン失敗時は「メールかパスワードが違います」とだけ返し、どちらが違うかは明かさない。
- パスワードリセットとメール確認は、フェーズ 1 では実装しない。

## 10. フェーズ 2 以降の設計メモ (詳細は着手時に決める)

### 会費・収支 (フェーズ 2)
- `ledger_entries`: 収支の 1 行。種別 (収入 / 支出)、金額、カテゴリ (会費、コート代、備品など)、発生日、メモ、関連する日程 (任意)。
- `fee_charges`: 幹事が作る請求 (例: 「10 月分会費 1,000 円」「○/○ のコート代割り勘」)。
- `fee_charge_members`: 請求ごと・メンバーごとの支払い状況 (未払い / 入金済み、入金日)。入金済みにすると収入が `ledger_entries` に記録される。
- 金額は整数 (円) で持つ。小数や浮動小数点は使わない。

### 試合結果・成績 (フェーズ 2)
- `matches`: 試合の日程 (`events.type = 'match'`) に 1 対 1 で結果を紐づける。対戦相手、自チームと相手の得点。
- `match_goals`: 得点者とアシスト者。
- 出場者は、その試合の出欠 (`yes`) とは別に「実際に出場した人」を記録する (欠席予定でも急きょ参加などがあるため)。
- 得点ランキング・出場回数は集計クエリで出す。

### お知らせ・助っ人・ボード (フェーズ 3)
- `announcements`: チーム単位のお知らせ。
- 助っ人は、アカウントを持たない参加者として `guests` を作り、`attendances` が `user_id` と `guest_id` のどちらか一方を持てるようにする。
- フォーメーションボード: 試合ごとに、選手と座標を保存する。

## 11. 未決事項

- 退会時のデータの扱い (物理削除 or 退会日時を持たせて履歴は残す)。過去の出欠・成績を残したいなら後者。
- 日程の繰り返し登録 (毎週土曜の練習など) をフェーズ 1 に含めるか。
- 招待リンクの有効期限と、1 リンクで何人まで参加できるか。
- 時刻の扱い。DB は UTC、表示は日本時間 (JST) 固定でよいか。
