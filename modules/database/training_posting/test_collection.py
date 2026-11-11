import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from modules.database.training_posting.collect import JOB_RULES, assign_jobs, collect, match_jobs, normalize_course, write_outputs
from modules.database.training_posting.schemas import TrainingSearchResult
from modules.database.training_posting.save_to_supabase import validate_records
from modules.database.training_posting.work24_client import Work24APIError


def course(key, title, **extra):
    return dict(trprId=key, title=title, titleLink=f'https://www.work24.go.kr/course?id={key}',
                subTitle='테스트 교육원', address='서울', traStartDate='20261109', traEndDate='2026-12-01', **extra)


class TrainingCollectionTests(unittest.TestCase):
    def test_mapping_and_missing_optional_fields(self):
        row = normalize_course(course('1', '백엔드 개발'))
        self.assertEqual(row['training_start_dt'], '2026-11-09')
        self.assertIsNone(row['id'])
        self.assertEqual(row['use_yn'], 'Y')
        self.assertEqual(set(row), {'id', 'work24_training_id', 'source_url', 'title', 'center_name', 'center_address', 'training_start_dt', 'training_end_dt', 'use_yn'})
        validate_records([row])
        with self.assertRaises(ValueError):
            validate_records([row, row])
        with self.assertRaises(ValueError):
            normalize_course(dict(trprId='1', title='회계', titleLink=''))

    def test_job_evidence_and_false_positive_exclusions(self):
        self.assertIn('데이터 분석가', match_jobs('Python 데이터 분석 및 SQL 실무'))
        self.assertNotIn('개발자', match_jobs('Python 데이터 분석 실무'))
        self.assertIn('기획자', match_jobs('서비스 기획 실무'))
        self.assertNotIn('총무', match_jobs('부동산 자산관리'))
        self.assertNotIn('마케팅', match_jobs('광고 영상편집 실무'))
        self.assertEqual(match_jobs('요양보호사 양성'), {})
        self.assertIn('인사', match_jobs('ERP정보관리사 인사2급 자격 취득'))
        self.assertIn('생산관리', match_jobs('ERP정보관리사 생산1급'))
        self.assertIn('기획자', match_jobs('경영기획과 사업계획서 작성'))
        self.assertNotIn('기획자', match_jobs('영상편집 및 콘텐츠 기획서'))

    def test_resume_reuses_existing_candidates_without_network(self):
        def fetch(**params):
            rows = [course(params['keyword'], params['keyword'] + ' 실무')]
            root = ET.Element('HRDNet')
            for name, value in [('scn_cnt', '1'), ('pageNum', '1'), ('pageSize', '100')]:
                ET.SubElement(root, name).text = value
            node = ET.SubElement(ET.SubElement(root, 'srchList'), 'scn_list')
            for key, value in rows[0].items():
                ET.SubElement(node, key).text = value
            return TrainingSearchResult(1, 1, 100, rows), ET.tostring(root, encoding='unicode'), {}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            rows, report = collect(api_key='test', start='20261109', end='20270509', quota=1, fetch=fetch, interval=0, output_dir=path)
            write_outputs(path, rows, report)
            def no_network(**params):
                self.fail('목표를 이미 충족한 캐시가 있는데 API를 호출했습니다.')
            resumed, summary = collect(api_key='test', start='20261109', end='20270509', quota=1, fetch=no_network, interval=0, output_dir=path, resume=True)
            self.assertEqual(summary['api_calls'], 0)
            self.assertEqual(summary['api_calls_all_runs'], 8)
            self.assertEqual({r['work24_training_id'] for r in resumed}, {r['work24_training_id'] for r in rows})

    def test_overlap_reallocation_and_quotas(self):
        pool = {
            'shared': dict(matches={'개발자': ['SQL'], '데이터 분석가': ['SQL']}),
            'developer-only': dict(matches={'개발자': ['Java']}),
        }
        assignments = assign_jobs(pool, quota=1)
        self.assertEqual(assignments['데이터 분석가'], ['shared'])
        self.assertEqual(assignments['개발자'], ['developer-only'])
        self.assertEqual(len(set(key for values in assignments.values() for key in values)), 2)

    def test_stops_at_target_and_queries_only_missing_roles(self):
        calls = []
        keywords = {terms[0]: role for role, terms in JOB_RULES.items()}
        def fetch(**params):
            calls.append(params)
            role = keywords[params['keyword']]
            rows = [course(f'{role}-{i}', f'{params["keyword"]} 실무 {i}') for i in range(4)]
            return TrainingSearchResult(4, 1, 100, rows), '<unused/>', {}
        rows, report = collect(api_key='test', start='20261109', end='20270509', quota=2, fetch=fetch, interval=0)
        self.assertEqual(len(rows), 16)
        self.assertEqual(report['status'], 'complete')
        self.assertEqual(len(calls), 8)
        self.assertTrue(all(n == 2 for n in report['job_counts'].values()))
        self.assertEqual(len({r['work24_training_id'] for r in rows}), 16)

    def test_duplicates_and_unrelated_rows_are_not_filled(self):
        def fetch(**params):
            rows = [course('same', 'Java 웹개발'), course('same', 'Java 웹개발'), course('offtopic', '요양보호사')]
            return TrainingSearchResult(3, 1, 100, rows), '<unused/>', {}
        rows, report = collect(api_key='test', start='20261109', end='20270509', quota=2, max_calls=2, fetch=fetch, interval=0)
        self.assertEqual(len(rows), 1)
        self.assertEqual(report['api_calls'], 2)
        self.assertEqual(report['status'], 'partial')
        self.assertGreater(report['rejected_counts']['duplicate_course_id'], 0)
        self.assertGreater(report['rejected_counts']['no_job_title_match'], 0)

    def test_service_error_stops_after_one_call(self):
        def fetch(**params):
            raise Work24APIError('승인 오류', '<GO24><error>승인 오류</error></GO24>')
        with tempfile.TemporaryDirectory() as folder:
            rows, report = collect(api_key='test', start='20261109', end='20270509', quota=2, fetch=fetch, interval=0, output_dir=Path(folder))
            self.assertEqual(rows, [])
            self.assertEqual(report['status'], 'failed')
            self.assertEqual(report['api_calls'], 1)
            self.assertTrue((Path(folder) / 'training_error.xml').exists())


if __name__ == '__main__':
    unittest.main()
