"""신입 경력과 마감 날짜 변환 회귀 테스트. 네트워크/DB 사용 없음."""
import json
import unittest
from dataclasses import asdict
from .wanted_crawler import parse_job
from .save_to_supabase import validate_records


class PostingFieldsTest(unittest.TestCase):
    def parse(self, career, due=None, address=None):
        job = {'id': 123, 'position': '개발자', 'company': {'company_name': '검증회사'},
               'address': {'location': '서울', 'district': '강남구'} if address is None else address,
               'career': career, 'due_time': due, 'status': 'active'}
        html = '<script id="__NEXT_DATA__">' + json.dumps({'props': {'pageProps': {'initialData': job}}}) + '</script>'
        return asdict(parse_job(html, 'https://www.wanted.co.kr/wd/123', '개발자'))

    def test_newbie_upper_is_null(self):
        record = self.parse({'annual_from': 0, 'annual_to': 1, 'is_newbie': True, 'is_expert': True})
        self.assertEqual(record['career_type'], '신입')
        self.assertIsNone(record['max_experience_years'])
        validate_records([record])

    def test_mixed_career_keeps_upper(self):
        record = self.parse({'annual_from': 0, 'annual_to': 5, 'is_newbie': True, 'is_expert': True})
        self.assertEqual(record['career_type'], '신입·경력')
        self.assertEqual(record['max_experience_years'], 5)

    def test_experienced_keeps_upper(self):
        record = self.parse({'annual_from': 3, 'annual_to': 5, 'is_newbie': False, 'is_expert': True})
        self.assertEqual(record['max_experience_years'], 5)

    def test_timestamp_becomes_source_calendar_date(self):
        record = self.parse({}, '2026-12-31T23:59:59-05:00')
        self.assertEqual(record['deadline_date'], '2026-12-31')
        validate_records([record])

    def test_date_only_is_preserved(self):
        record = self.parse({}, '2026-12-31')
        self.assertEqual(record['deadline_date'], '2026-12-31')
        validate_records([record])

    def test_unknown_deadline_is_null(self):
        self.assertIsNone(self.parse({})['deadline_date'])

    def test_overseas_region_uses_actual_full_location(self):
        record = self.parse({}, address={'country': '기타', 'location': None,
                                        'district': None, 'full_location': '중국 상하이'})
        self.assertEqual(record['region_name'], '중국 상하이')
        validate_records([record])

    def test_missing_region_is_rejected(self):
        with self.assertRaises(ValueError):
            self.parse({}, address={})

    def test_validator_rejects_newbie_upper_and_timestamps(self):
        record = self.parse({'annual_from': 0, 'annual_to': 1, 'is_newbie': True, 'is_expert': True})
        with self.assertRaises(ValueError):
            validate_records([{**record, 'max_experience_years': 1}])
        with self.assertRaises(ValueError):
            validate_records([{**record, 'deadline_date': '2026-12-31T23:59:59+09:00'}])

class CollectionWorkflowTest(unittest.TestCase):
    def test_all_mode_routes_to_full_collection(self):
        from unittest.mock import patch
        from . import collect
        with patch('sys.argv', ['collect', '--all', '--save']), patch.object(collect, 'collect_all') as full:
            collect.main()
        full.assert_called_once_with()

    def test_check_mode_cannot_save(self):
        import contextlib
        import io
        from unittest.mock import patch
        from . import collect
        with patch('sys.argv', ['collect', '--check', '--save']), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                collect.main()
        self.assertEqual(raised.exception.code, 2)

    def test_full_collection_skips_saved_and_verifies_checkpoint(self):
        import contextlib
        import io
        import tempfile
        from pathlib import Path
        from dataclasses import replace
        from types import SimpleNamespace
        from unittest.mock import patch
        from . import collect, save_to_supabase
        from .schemas import JobPosting
        first = PostingFieldsTest().parse({})
        first['id'] = '00000000-0000-0000-0000-000000000001'
        second = replace(JobPosting(**first), source_url='https://www.wanted.co.kr/wd/124', id=None)
        stored = {**second.__dict__, 'id': '00000000-0000-0000-0000-000000000002'}
        initial = {first['source_url']: first}
        final = {**initial, second.source_url: stored}
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(collect, 'MODULE_DIR', Path(folder)), \
                patch.object(collect, 'read_sources', return_value={'개발자': list(final)}), \
                patch.object(collect, 'read_saved', side_effect=[initial, final]), \
                patch.object(collect, 'fetch', return_value=SimpleNamespace(text='HTML')) as request, \
                patch.object(collect, 'parse_job', return_value=second), \
                patch.object(collect.time, 'sleep'), \
                patch.object(collect, 'write_records') as output, \
                patch.object(collect, 'write_validation_report') as report, \
                patch.object(save_to_supabase, 'load_database_url', return_value='unused'), \
                patch.object(save_to_supabase, 'save_records', return_value=([stored], {})) as save:
            collect.collect_all()
        self.assertEqual(request.call_count, 1)
        self.assertEqual(request.call_args.args[1], second.source_url)
        self.assertEqual(save.call_count, 1)
        self.assertEqual(output.call_args.args[0], [first, stored])
        self.assertTrue(report.call_args.args[0]['database']['complete'])
        self.assertEqual(report.call_args.args[0]['database']['remaining_urls'], 0)


if __name__ == '__main__':
    unittest.main()
