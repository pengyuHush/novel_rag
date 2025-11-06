"""自定义测试断言工具."""

from typing import Any


def assert_novel_equal(actual: dict, expected: dict, check_fields: list[str] = None):
    """断言小说数据相等.

    Args:
        actual: 实际数据
        expected: 期望数据
        check_fields: 需要检查的字段列表，如果为None则检查所有字段
    """
    if check_fields is None:
        check_fields = ["title", "author", "description", "tags"]

    for field in check_fields:
        assert actual.get(field) == expected.get(field), (
            f"字段 '{field}' 不匹配: {actual.get(field)} != {expected.get(field)}"
        )


def assert_chapter_equal(actual: dict, expected: dict, check_fields: list[str] = None):
    """断言章节数据相等.

    Args:
        actual: 实际数据
        expected: 期望数据
        check_fields: 需要检查的字段列表，如果为None则检查所有字段
    """
    if check_fields is None:
        check_fields = [
            "chapter_number",
            "title",
            "start_position",
            "end_position",
            "word_count",
        ]

    for field in check_fields:
        assert actual.get(field) == expected.get(field), (
            f"字段 '{field}' 不匹配: {actual.get(field)} != {expected.get(field)}"
        )


def assert_response_success(response: Any, expected_status: int = 200):
    """断言API响应成功.

    Args:
        response: HTTP响应对象
        expected_status: 期望的状态码
    """
    assert response.status_code == expected_status, (
        f"状态码不匹配: {response.status_code} != {expected_status}\n"
        f"响应内容: {response.text}"
    )


def assert_response_error(response: Any, expected_status: int = 400):
    """断言API响应错误.

    Args:
        response: HTTP响应对象
        expected_status: 期望的错误状态码
    """
    assert response.status_code == expected_status, (
        f"状态码不匹配: {response.status_code} != {expected_status}\n"
        f"响应内容: {response.text}"
    )
    
    # 检查是否包含错误信息
    data = response.json()
    assert "detail" in data or "message" in data, "响应中缺少错误信息"


def assert_pagination(data: dict, expected_page: int = 1, expected_size: int = 10):
    """断言分页数据正确.

    Args:
        data: 响应数据
        expected_page: 期望的页码
        expected_size: 期望的每页大小
    """
    assert "pagination" in data, "响应中缺少分页信息"
    
    pagination = data["pagination"]
    assert pagination["page"] == expected_page, (
        f"页码不匹配: {pagination['page']} != {expected_page}"
    )
    assert pagination["size"] == expected_size, (
        f"每页大小不匹配: {pagination['size']} != {expected_size}"
    )
    assert "total" in pagination, "分页信息中缺少总数"
    assert "pages" in pagination, "分页信息中缺少总页数"

