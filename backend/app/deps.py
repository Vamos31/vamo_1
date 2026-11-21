"""共通チェック: ログイン確認、チームメンバー確認、幹事確認。(仕様書 4.5 節・9.5 節)"""
# TODO: 認証のステップで以下を実装する
#   get_current_user  ... Cookie(session_id) → sessions → ユーザー。なければ 401 UNAUTHENTICATED
#   get_team_context  ... 在籍メンバー (left_at IS NULL) か確認。違えば 404 NOT_FOUND (存在を隠す)
#   require_admin     ... 幹事 (role = admin) か確認。違えば 403 FORBIDDEN
