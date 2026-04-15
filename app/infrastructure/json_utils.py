"""LLM 응답에서 JSON 블록을 추출하는 공유 유틸리티."""
import json
import re


def extract_json_from_markdown(text: str) -> dict:
    """마크다운 코드 블록 또는 raw JSON 형태에서 dict를 추출한다.

    Args:
        text: LLM이 반환한 문자열

    Returns:
        파싱된 dict

    Raises:
        ValueError: JSON 블록을 찾을 수 없거나 파싱 실패 시
    """
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"\{[\s\S]+\}", text)
    if match:
        return json.loads(match.group(0))
    raise ValueError(f"JSON 블록 없음: {text[:200]}")
