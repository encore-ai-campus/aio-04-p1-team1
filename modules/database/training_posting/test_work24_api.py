"""합성 XML로 파서/검색 조건/오류 처리를 검증합니다. 실제 API 과정 응답이 아닙니다."""

import unittest
from unittest.mock import patch
from urllib.error import URLError

from modules.database.training_posting.work24_client import (
    Work24APIError, build_search_params, parse_training_xml, search_training_courses,
)


SAMPLE = '''<HRDNet><scn_cnt>2</scn_cnt><pageNum>1</pageNum><pageSize>1</pageSize>
<srchList><scn_list><title>테스트 파이썬 과정</title><ncsCd>02010101</ncsCd>
<trprId>TEST-001</trprId><trprDegr>1</trprDegr><certificate/>
<contents><![CDATA[<p>테스트 내용</p>]]></contents><futureField>추가값</futureField>
</scn_list></srchList></HRDNet>'''


class Work24APITests(unittest.TestCase):
    def test_one_course_and_preserved_original_values(self):
        result = parse_training_xml(SAMPLE)
        self.assertEqual(result.total_count, 2)
        self.assertEqual(len(result.courses), 1)
        self.assertEqual(result.courses[0]['ncsCd'], '02010101')
        self.assertEqual(result.courses[0]['contents'], '<p>테스트 내용</p>')
        fields = {field['field']: field for field in result.inspect()[0]['fields']}
        self.assertTrue(fields['certificate']['present'])
        self.assertEqual(fields['certificate']['value'], '')
        self.assertFalse(fields['address']['present'])
        self.assertIsNone(fields['address']['value'])
        self.assertEqual(result.inspect()[0]['extra_fields'], {'futureField': '추가값'})

    def test_zero_results_are_not_api_failure(self):
        result = parse_training_xml('<HRDNet><scn_cnt>0</scn_cnt><pageNum>1</pageNum><pageSize>1</pageSize><srchList/></HRDNet>')
        self.assertEqual(result.courses, [])

    def test_namespace_support(self):
        result = parse_training_xml(SAMPLE.replace('<HRDNet>', '<HRDNet xmlns="urn:training">'))
        self.assertEqual(result.courses[0]['title'], '테스트 파이썬 과정')

    def test_error_response_is_not_zero_results(self):
        xml = '<GO24><error>신청하신 OpenApi 서비스가 존재하지 않습니다</error></GO24>'
        with self.assertRaisesRegex(Work24APIError, '서비스가 존재하지') as context:
            parse_training_xml(xml)
        self.assertEqual(context.exception.response_xml, xml)

    def test_invalid_or_unexpected_response(self):
        for xml in ['<html>차단</html>', 'invalid', '<HRDNet/>',
                    '<HRDNet><scn_cnt>1</scn_cnt><pageNum>1</pageNum><pageSize>1</pageSize></HRDNet>']:
            with self.subTest(xml=xml), self.assertRaises(Work24APIError):
                parse_training_xml(xml)

    def test_optional_search_filters_and_dates(self):
        params = build_search_params(keyword='파이썬', start='20261109', end='20261231', region='11')
        self.assertEqual(params['pageSize'], '1')
        self.assertEqual(params['srchTraProcessNm'], '파이썬')
        self.assertEqual(params['srchTraArea1'], '11')
        self.assertNotIn('srchTraOrganNm', params)
        self.assertNotIn('authKey', params)
        for changes in [dict(start='20260230'), dict(end='20261108'), dict(page_size=101), dict(page=0)]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                build_search_params(**{**dict(keyword='', start='20261109', end='20261231'), **changes})

    def test_key_must_not_contain_query_string(self):
        for key in ['', 'authKey=test', 'test&returnType=XML']:
            with self.subTest(key=key), self.assertRaises(ValueError):
                search_training_courses(key, keyword='', start='20261109', end='20261231')

    def test_network_errors_do_not_expose_key(self):
        with patch('modules.database.training_posting.work24_client.urlopen', side_effect=URLError('secret-test-key')):
            with self.assertRaises(Work24APIError) as context:
                search_training_courses('secret-test-key', keyword='', start='20261109', end='20261231')
        self.assertNotIn('secret-test-key', str(context.exception))


if __name__ == '__main__':
    unittest.main()
