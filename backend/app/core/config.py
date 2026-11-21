from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """環境変数 (大文字小文字は区別しない) から読み込む設定。"""

    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/postgres"
    # CORS の許可元。書き込み系リクエストの Origin 検査 (CSRF 対策) の照合先にもなる
    frontend_origin: str = "http://localhost:3000"
    # Cookie の Secure 属性。開発 (http) は false、本番 (https) は true
    cookie_secure: bool = False
    # セッションの有効日数 (最終利用から)
    session_ttl_days: int = 14
    # 招待リンクの有効日数 (発行から)
    invitation_ttl_days: int = 7


settings = Settings()
