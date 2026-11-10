"""고용24 목록 API 응답 필드와 training_posting_mj 저장 모델."""

from dataclasses import dataclass
from typing import Dict, List, Optional


FIELD_DESCRIPTIONS = {
    "address": "주소", "certificate": "자격증", "contents": "컨텐츠",
    "courseMan": "수강비", "eiEmplCnt3": "고용보험 3개월 취업인원 수",
    "eiEmplCnt3Gt10": "취업누적인원 10인 이하 여부 (제공 중단, 빈 값)",
    "eiEmplRate3": "고용보험 3개월 취업률", "eiEmplRate6": "고용보험 6개월 취업률",
    "grade": "등급", "instCd": "훈련기관 코드", "ncsCd": "NCS 코드",
    "realMan": "실제 훈련비", "regCourseMan": "수강신청 인원", "stdgScor": "만족도 점수",
    "subTitle": "부 제목", "subTitleLink": "부 제목 링크", "telNo": "전화번호",
    "title": "제목", "titleIcon": "제목 아이콘", "titleLink": "제목 링크",
    "traEndDate": "훈련종료일자", "traStartDate": "훈련시작일자",
    "trainTarget": "훈련대상", "trainTargetCd": "훈련구분", "trainstCstId": "훈련기관 ID",
    "trngAreaCd": "지역코드(중분류)", "trprDegr": "훈련과정 순차", "trprId": "훈련과정 ID",
    "wkendSe": "주말/주중 구분", "yardMan": "정원",
}

NCS_CATEGORIES = dict(zip(
    (f"{code:02d}" for code in range(1, 25)),
    ["사업관리", "경영/회계/사무", "금융/보험", "교육/자연/사회과학", "법률/경찰/소방/교도/국방",
     "보건/의료", "사회복지/종교", "문화/예술/디자인/방송", "운전/운송", "영업판매", "경비/청소",
     "이용/숙박/여행/오락/스포츠", "음식서비스", "건설", "기계", "재료", "화학/바이오", "섬유/의복",
     "전기/전자", "정보통신", "식품가공", "인쇄/목재/가구/공예", "환경/에너지/안전", "농림어업"],
))


@dataclass(frozen=True)
class TrainingPosting:
    training_id: str
    source_url: str
    title: str
    center_name: Optional[str]
    center_address: Optional[str]
    training_start_dt: Optional[str]
    training_end_dt: Optional[str]
    use_yn: str = "Y"
    id: Optional[str] = None


@dataclass(frozen=True)
class TrainingSearchResult:
    total_count: int
    page_num: int
    page_size: int
    courses: List[Dict[str, str]]

    def inspect(self):
        """누락된 필드와 존재하지만 비어 있는 필드를 구분합니다."""
        return [{
            "course": course,
            "fields": [{
                "field": name, "description": description,
                "present": name in course, "value": course.get(name),
            } for name, description in FIELD_DESCRIPTIONS.items()],
            "extra_fields": {k: v for k, v in course.items() if k not in FIELD_DESCRIPTIONS},
        } for course in self.courses]
