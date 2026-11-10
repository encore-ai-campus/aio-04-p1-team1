"""python -m modules.training_posts.import_training_posts로 명시적으로 실행할 때만 저장합니다."""
from datetime import datetime, timedelta, timezone
from modules.training_posts.repository import replace_snapshot
from modules.training_posts.service import fetch_all

def main():
    today = datetime.now(timezone(timedelta(hours=9))).date()
    result = replace_snapshot(fetch_all(today-timedelta(days=365), today+timedelta(days=365)))
    print("Saved:", result["total"], "courses")
    for code, count in sorted(result["categories"].items()):
        print(code, count)

if __name__ == "__main__":
    main()
