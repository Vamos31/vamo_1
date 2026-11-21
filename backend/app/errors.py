"""共通エラー。すべてのエラーを {"error": {"code", "message", "details"}} の形で返す。"""
import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """アプリで想定したエラー。Service / 依存関数から送出する。"""

    def __init__(self, status_code: int, code: str, message: str, details: Any = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def error_response(status_code: int, code: str, message: str, details: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details}},
    )


# FastAPI / Starlette 自身が出す HTTP エラー (存在しないパスなど) の変換用
_HTTP_ERROR_CODES = {
    401: ("UNAUTHENTICATED", "ログインが必要です"),
    403: ("FORBIDDEN", "この操作はできません"),
    404: ("NOT_FOUND", "見つかりません"),
    405: ("METHOD_NOT_ALLOWED", "許可されていないメソッドです"),
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        return error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        details = [
            {
                # loc の先頭は "body" / "query" などの入力元なので除く
                "field": ".".join(str(p) for p in err["loc"][1:]),
                "message": err["msg"],
            }
            for err in exc.errors()
        ]
        return error_response(422, "VALIDATION_ERROR", "入力内容が正しくありません", details)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException):
        code, message = _HTTP_ERROR_CODES.get(exc.status_code, ("HTTP_ERROR", "エラーが発生しました"))
        return error_response(exc.status_code, code, message)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        # 詳細はログだけに残し、レスポンスには出さない
        logger.exception("unhandled error: %s %s", request.method, request.url.path)
        return error_response(500, "INTERNAL_ERROR", "サーバーでエラーが発生しました")
