import json
import os
import re
import tempfile
import unittest
from html import unescape
from dataclasses import asdict
from pathlib import Path
from uuid import UUID

from modules.database.job_posting.wanted_crawler import (
    WantedCrawlError, collect_source, parse_wanted_html,
)
from modules.database.job_posting.save_to_supabase import read_records

URL = 'https://www.wanted.co.kr/wd/123'


def page(**overrides):
    job = {
        'id': 123, 'company': {'company_name': '회사'}, 'position': '개발자',
        'address': {'location': '서울', 'district': '강남구', 'full_location': '서울 강남구 상세주소'},
        'career': {'annual_from': 3, 'annual_to': 5, 'is_newbie': False, 'is_expert': True},
        'employment_type': 'regular', 'intro': '소개\n원문', 'main_tasks': '업무',
        'requirements': '자격', 'preferred_points': '우대', 'status': 'active', 'due_time': None,
    }
    job.update(overrides)
    data = {'props': {'pageProps': {'initialData': job}}}
    return '<script id="__NEXT_DATA__" type="application/json">' + json.dumps(data) + '</script>'


class WantedCrawlerTests(unittest.TestCase):
    def test_database_input_requires_new_schema_and_valid_date(self):
        row = asdict(parse_wanted_html(page(due_time='2026-11-15T00:00:00'), URL))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'data.json'
            path.write_text(json.dumps([row]))
            self.assertEqual(read_records(path)[0]['deadline_date'], '2026-11-15')
            path.write_text(json.dumps([row, row]))
            with self.assertRaises(ValueError):
                read_records(path)
            row['deadline_date'] = '2026-02-30'
            path.write_text(json.dumps([row]))
            with self.assertRaises(ValueError):
                read_records(path)
            row['deadline_at'] = row.pop('deadline_date')
            path.write_text(json.dumps([row]))
            with self.assertRaises(ValueError):
                read_records(path)

    @unittest.skipUnless(os.environ.get('WANTED_HTML_DIR'), '실제 HTML 검증은 WANTED_HTML_DIR 지정 필요')
    def test_source_snapshots_against_visible_headers(self):
        root = Path(os.environ['WANTED_HTML_DIR'])
        source = Path(__file__).with_name('source.txt')
        urls = set(re.findall(r'https://www\.wanted\.co\.kr/wd/\d+', source.read_text()))
        for url in sorted(urls):
            with self.subTest(url=url):
                html = (root / f"{url.rsplit('/', 1)[-1]}.html").read_text()
                job = parse_wanted_html(html, url)
                title = re.search(r'<h1\b[^>]*>(.*?)</h1>', html, re.S).group(1)
                self.assertEqual(job.title, unescape(re.sub(r'<[^>]+>', '', title)))
                company = re.search(r'data-company-name="([^"]+)"', html).group(1)
                self.assertEqual(job.company_name, unescape(company))
                info = re.findall(r'<span[^>]*JobHeader_JobHeader__Tools__Company__Info[^>]*>(.*?)</span>', html, re.S)
                career = unescape(re.sub(r'<[^>]+>', '', info[1]))
                if career == '신입':
                    self.assertEqual(job.career_type, '신입')
                elif career == '신입 이상':
                    self.assertEqual(job.career_type, '신입·경력')
                elif career.startswith('신입-경력'):
                    self.assertEqual(job.career_type, '신입·경력')
                    self.assertEqual(job.min_experience_months, 0)
                    self.assertEqual(job.max_experience_months, int(re.search(r'\d+', career).group()) * 12)
                elif career.startswith('경력'):
                    self.assertEqual(job.career_type, '경력')
                    years = [int(n) for n in re.findall(r'\d+', career)]
                    self.assertEqual(job.min_experience_months, years[0] * 12)
                    if '이상' in career:
                        self.assertIsNone(job.max_experience_months)
                    elif len(years) == 2:
                        self.assertEqual(job.max_experience_months, years[1] * 12)
                else:
                    self.fail(f'확인하지 않은 헤더 경력 표현: {career}')
                self.assertTrue(job.address)
                self.assertTrue(job.main_tasks)
                self.assertTrue(job.qualifications)
                self.assertTrue(job.position_detail)

    def test_schema_and_original_text(self):
        job = parse_wanted_html(page(), URL)
        self.assertEqual(set(asdict(job)), {
            'id', 'source_url', 'title', 'company_name', 'region_id', 'address',
            'employment_type', 'career_type', 'min_experience_months', 'max_experience_months',
            'position_detail', 'main_tasks', 'qualifications', 'preferred_qualifications',
            'deadline_type', 'deadline_date', 'status',
        })
        self.assertEqual(job.position_detail, '소개\n원문')
        self.assertEqual((job.min_experience_months, job.max_experience_months), (36, 60))
        self.assertEqual(job.employment_type, '정규직')
        self.assertEqual(job.status, '모집 중')

    def test_stable_internal_uuid_and_canonical_url(self):
        one = parse_wanted_html(page(), URL)
        two = parse_wanted_html(page(), 'https://wanted.co.kr/wd/123/?x=1')
        self.assertEqual(one.id, two.id)
        self.assertEqual(str(UUID(one.id)), one.id)
        self.assertEqual(two.source_url, URL)

    def test_region_mapping_is_external(self):
        self.assertIsNone(parse_wanted_html(page(), URL).region_id)
        region = 'ab06fa20-96e9-4fa9-b81c-cb1dd4673e87'
        self.assertEqual(parse_wanted_html(page(), URL, region_ids={'서울 강남구': region}).region_id, region)
        with self.assertRaises(WantedCrawlError):
            parse_wanted_html(page(), URL, region_ids={'서울 강남구': 'not-a-uuid'})

    def test_unbounded_maximum(self):
        job = parse_wanted_html(page(career={'annual_from': 5, 'annual_to': 100, 'is_expert': True}), URL)
        self.assertEqual(job.min_experience_months, 60)
        self.assertIsNone(job.max_experience_months)

    def test_career_categories(self):
        for flags, expected in [
            ({'is_newbie': True, 'is_expert': False}, '신입'),
            ({'is_newbie': False, 'is_expert': True}, '경력'),
            ({'is_newbie': True, 'is_expert': True}, '신입·경력'),
            ({'is_newbie': False, 'is_expert': False}, '무관'),
            ({}, '미확인'),
        ]:
            with self.subTest(expected=expected):
                self.assertEqual(parse_wanted_html(page(career=flags), URL).career_type, expected)
        job = parse_wanted_html(page(career={'is_newbie': True, 'is_expert': True, 'annual_from': 0, 'annual_to': 1}), URL)
        self.assertEqual(job.career_type, '신입')

    def test_invalid_career(self):
        for career in [{'annual_from': -1}, {'annual_from': 7, 'annual_to': 3}, {'annual_from': True}]:
            with self.subTest(career=career), self.assertRaises(WantedCrawlError):
                parse_wanted_html(page(career=career), URL)

    def test_employment_and_unknown_codes(self):
        for raw, expected in [('contract', '계약직'), ('intern', '인턴'), ('new-code', None), (None, None)]:
            self.assertEqual(parse_wanted_html(page(employment_type=raw), URL).employment_type, expected)
        self.assertEqual(parse_wanted_html(page(status='closed'), URL).status, '마감')
        self.assertEqual(parse_wanted_html(page(status='new-code'), URL).status, '미확인')

    def test_deadline_date_preserves_source_calendar_day(self):
        job = parse_wanted_html(page(due_time='2026-11-15T00:00:00'), URL)
        self.assertEqual(job.deadline_type, '날짜 지정')
        self.assertEqual(job.deadline_date, '2026-11-15')
        job = parse_wanted_html(page(due_time='2026-11-15T18:00:00+09:00'), URL)
        self.assertEqual(job.deadline_date, '2026-11-15')
        job = parse_wanted_html(page(due_time='2026-11-15'), URL)
        self.assertEqual(job.deadline_date, '2026-11-15')
        job = parse_wanted_html(page(due_time='2026-11-15T00:30:00+09:00'), URL)
        self.assertEqual(job.deadline_date, '2026-11-15')
        job = parse_wanted_html(page(due_time=None), URL)
        self.assertIsNone(job.deadline_date)

    def test_deadline_label_not_body(self):
        for label, expected in [('상시채용', '상시'), ('채용 시 마감', '채용 시'), ('미정', '미확인')]:
            html = page(intro='채용 시 마감') + f'<article class="JobDueTime_test"><h2>마감일</h2><span>{label}</span></article>'
            self.assertEqual(parse_wanted_html(html, URL).deadline_type, expected)
        self.assertEqual(parse_wanted_html(page(intro='상시 채용'), URL).deadline_type, '미확인')

    def test_stale_close_time_does_not_override_status(self):
        job = parse_wanted_html(page(close_time='2020-01-01', status='active'), URL)
        self.assertEqual(job.status, '모집 중')

    def test_missing_optional_fields(self):
        job = parse_wanted_html(page(preferred_points='', address={}, intro=None), URL)
        self.assertIsNone(job.preferred_qualifications)
        self.assertIsNone(job.address)
        self.assertIsNone(job.position_detail)

    def test_invalid_html_or_wrong_post(self):
        for html in ['<html>Forbidden</html>', '<script id="__NEXT_DATA__">{bad}</script>', page(id=456), page(company=None)]:
            with self.subTest(html=html[:30]), self.assertRaises(WantedCrawlError):
                parse_wanted_html(html, URL)
        with self.assertRaises(ValueError):
            parse_wanted_html(page(), 'https://example.com/wd/123')

    def test_source_deduplication_and_partial_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source.txt'
            source.write_text(f'## 인사\n\n{URL}\n{URL}\nhttps://www.wanted.co.kr/wd/456\n', encoding='utf-8')
            (root / '123.html').write_text(page(), encoding='utf-8')
            jobs, report = collect_source(source, html_dir=root)
            self.assertEqual(len(jobs), 1)
            self.assertEqual(report['source_count'], 3)
            self.assertEqual(report['unique_count'], 2)
            self.assertEqual(report['duplicates'], {URL: 2})
            self.assertEqual(report['failure_count'], 1)
            self.assertEqual(report['failures'][0]['source_url'], 'https://www.wanted.co.kr/wd/456')


if __name__ == '__main__':
    unittest.main()
