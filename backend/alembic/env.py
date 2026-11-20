from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.core.config import settings
from app.db import Base
import app.models  # noqa: F401  全モデルを Base.metadata に登録するため

# Alembic の Config オブジェクト。使用中の .ini ファイルの
# 値にアクセスできる。
config = context.config

# 接続先は alembic.ini ではなく、アプリの設定 (環境変数 DATABASE_URL) から読む
config.set_main_option("sqlalchemy.url", settings.database_url)

# ログ設定ファイルを解釈する。
# この行で、ロガーの設定が行われる。
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate (モデルとDBの差分からの自動生成) のために、
# モデルの MetaData オブジェクトをここで指定する
target_metadata = Base.metadata

# env.py の用途に応じて、config から他の値も取得できる。
# 例:
# my_important_option = config.get_main_option("my_important_option")
# ... など。


def run_migrations_offline() -> None:
    """'オフライン' モードでマイグレーションを実行する。

    URL だけを使って context を設定し、Engine は作らない
    (Engine を渡すこともできる)。Engine の作成を省くので、
    DBAPI (DBドライバ) が使えなくても動く。

    context.execute() への呼び出しは、SQL 文として
    スクリプトの出力に書き出される。

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """'オンライン' モードでマイグレーションを実行する。

    この場合は Engine を作成し、その接続を context に
    関連付ける必要がある。

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
