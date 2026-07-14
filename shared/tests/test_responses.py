from veloai_shared.responses import ErrorResponse, PaginationMeta, SuccessResponse


def test_success_response_defaults() -> None:
    response = SuccessResponse(message="ok", data={"id": 1})

    assert response.success is True
    assert response.message == "ok"
    assert response.data == {"id": 1}
    assert response.meta is None


def test_success_response_with_pagination_meta() -> None:
    meta = PaginationMeta(page=1, page_size=20, total=45, pages=3)
    response = SuccessResponse(message="ok", data=[1, 2, 3], meta=meta)

    dumped = response.model_dump()

    assert dumped["meta"] == {"page": 1, "page_size": 20, "total": 45, "pages": 3}


def test_error_response_never_includes_traceback_field() -> None:
    response = ErrorResponse(message="Não encontrado.", code="NOT_FOUND", trace_id="abc")

    dumped = response.model_dump()

    assert dumped["success"] is False
    assert "traceback" not in dumped
    assert dumped["errors"] == []
