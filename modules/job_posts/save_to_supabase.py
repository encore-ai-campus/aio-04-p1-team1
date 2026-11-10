"""수집 JSON을 public.job_posting_mj에 저장하고 같은 트랜잭션에서 검증합니다.

python -m modules.job_posts.save_to_supabase
"""

import argparse
import json
import os
from dataclasses import fields
from datetime import date
from pathlib import Path
from uuid import UUID

from modules.job_posts.model import WantedJobPost
from modules.job_posts.service import _canonical_url


MODULE_DIR = Path(__file__).resolve().parent
COLUMNS = tuple(field.name for field in fields(WantedJobPost))


def read_records(path: Path):
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not records:
        raise ValueError("저장할 공고의 JSON 배열이 필요합니다.")
    seen_urls, seen_ids = set(), set()
    for row in records:
        if not isinstance(row, dict) or set(row) != set(COLUMNS):
            raise ValueError("공고 컬럼이 현재 모델과 다릅니다. 크롤링 결과를 다시 생성하세요.")
        UUID(row["id"])
        if row["region_id"] is not None:
            UUID(row["region_id"])
        if _canonical_url(row["source_url"]) != row["source_url"]:
            raise ValueError("공고 URL을 정규화하세요.")
        if row["source_url"] in seen_urls or row["id"] in seen_ids:
            raise ValueError("공고 ID 또는 URL이 중복되었습니다.")
        seen_urls.add(row["source_url"])
        seen_ids.add(row["id"])
        if row["deadline_date"] is not None:
            value = date.fromisoformat(row["deadline_date"])
            if value.isoformat() != row["deadline_date"]:
                raise ValueError("deadline_date는 YYYY-MM-DD 형식이어야 합니다.")
    return records


def save_records(records, database_url: str):
    import psycopg
    from psycopg import sql
    from psycopg.rows import dict_row

    # source_url로 갱신하므로 기존 내부 ID와 이미 매핑한 region_id는 보존합니다.
    updates = [
        sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(name), sql.Identifier(name))
        for name in COLUMNS if name not in {"id", "source_url", "region_id"}
    ]
    updates.append(sql.SQL("region_id = COALESCE(EXCLUDED.region_id, job_posting_mj.region_id)"))
    statement = sql.SQL("INSERT INTO public.job_posting_mj ({}) VALUES ({}) ON CONFLICT (source_url) DO UPDATE SET {}").format(
        sql.SQL(", ").join(map(sql.Identifier, COLUMNS)),
        sql.SQL(", ").join(sql.Placeholder() for _ in COLUMNS),
        sql.SQL(", ").join(updates),
    )
    with psycopg.connect(database_url, sslmode="require", connect_timeout=10, row_factory=dict_row) as connection:
        connection.execute("SET LOCAL statement_timeout = '30s'")
        connection.execute((MODULE_DIR / "job_posting_mj.sql").read_text(encoding="utf-8"))
        with connection.cursor() as cursor:
            cursor.executemany(statement, [tuple(row[name] for name in COLUMNS) for row in records])
        saved = connection.execute(
            "SELECT * FROM public.job_posting_mj WHERE source_url = ANY(%s)",
            ([row["source_url"] for row in records],),
        ).fetchall()
        by_url = {row["source_url"]: row for row in saved}
        if len(saved) != len(records):
            raise RuntimeError("저장 후 공고 건수가 일치하지 않아 롤백합니다.")
        for record in records:
            actual = by_url[record["source_url"]]
            for name in COLUMNS:
                if name == "id" or (name == "region_id" and record[name] is None):
                    continue
                value = actual[name]
                if isinstance(value, (date, UUID)):
                    value = str(value)
                if value != record[name]:
                    raise RuntimeError(f"저장 후 {name} 검증에 실패해 롤백합니다.")
    return {"table": "public.job_posting_mj", "verified_rows": len(saved),
            "dated_rows": sum(row["deadline_date"] is not None for row in saved)}


def main():
    parser = argparse.ArgumentParser(description="수집한 공고를 Supabase에 저장합니다.")
    parser.add_argument("--input", type=Path, default=MODULE_DIR / "results/job_postings.json")
    args = parser.parse_args()
    try:
        records = read_records(args.input)
        from dotenv import load_dotenv
        load_dotenv(MODULE_DIR.parents[1] / ".env", override=False)
        database_url = os.environ.get("DATABASE_URL", "").strip()
        if not database_url:
            parser.exit(1, "저장 실패: .env에 DATABASE_URL을 설정하세요.\n")
        result = save_records(records, database_url)
    except ImportError:
        parser.exit(1, "저장 실패: python -m pip install -r requirements.txt 를 실행하세요.\n")
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(1, f"저장 실패: {exc}\n")
    except Exception as exc:
        # 연결 문자열이나 비밀번호가 포함될 수 있어 DB 예외 전문은 출력하지 않습니다.
        parser.exit(1, f"DB 저장 실패: {type(exc).__name__} (SQLSTATE={getattr(exc, 'sqlstate', None)})\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
