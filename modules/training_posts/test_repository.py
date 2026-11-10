"""Offline checks for the shared table mapping and read-only connection."""
from datetime import date
from unittest import TestCase
from unittest.mock import MagicMock, patch
from uuid import uuid4

from modules.training_posts import repository
from modules.training_posts.service import normalize_stored_course
from modules.training_match.model import RecommendationInput
from modules.training_match.service import shortlist_courses


class SharedTrainingTableTests(TestCase):
    def test_nullable_fields_and_unavailable_facts(self):
        record_id = uuid4()
        course = normalize_stored_course((record_id, 'COURSE', 'https://www.work24.go.kr/',
                                          'SQL 입문', None, None, None, None))
        self.assertEqual(course['key'], str(record_id))
        self.assertEqual(course['courseId'], 'COURSE')
        self.assertEqual(course['categoryName'], '분야 미제공')
        self.assertEqual(course['mode'], 'unknown')
        self.assertIsNone(course['cost'])
        self.assertEqual(course['start'], '')
        self.assertEqual(course['round'], '')
        self.assertIn('SQL', course['tags'])
        preferences = RecommendationInput(job_title='SQL', job_text='SQL 데이터 조회 업무')
        self.assertEqual(shortlist_courses({'courses': [course]}, preferences), [course])
        self.assertEqual(shortlist_courses({'courses': [course]}, preferences.model_copy(update={'budget': 0})), [])
        self.assertEqual(shortlist_courses({'courses': [course]}, preferences.model_copy(update={'mode': 'online_only'})), [])

    def test_shared_connection_is_read_only_and_query_matches_schema(self):
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = [
            (uuid4(), 'COURSE', 'https://www.work24.go.kr/', 'Excel 기초',
             '교육기관', '서울', date(2026, 11, 1), date(2026, 12, 1))]

        def session():
            yield connection

        with patch.object(repository, 'get_db', session):
            result = repository.read_catalogue(date(2026, 1, 1), date(2027, 1, 1))
        statements = [call.args[0] for call in cursor.execute.call_args_list]
        self.assertEqual(statements[0], 'SET TRANSACTION READ ONLY')
        query = statements[-1]
        self.assertIn('FROM public.training_posting_mj', query)
        self.assertIn("use_yn = 'Y'", query)
        self.assertIn('training_start_dt IS NULL', query)
        self.assertNotIn('raw_payload', query)
        self.assertEqual(result['courses'][0]['provider'], '교육기관')
        self.assertEqual(result['courses'][0]['start'], '2026-11-01')
        self.assertEqual(result['courses'][0]['weeks'], 5)
