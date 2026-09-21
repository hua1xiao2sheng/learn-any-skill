"""Package/frontmatter/schema checks, separate from live host evaluations."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts._common import DataError, load_json
from scripts.validate_repo import markdown_links_exist, parse_yaml, validate_frontmatter, validate_progress, validate_repo


class RepositoryTests(unittest.TestCase):
    def test_repository_is_consistent(self):
        self.assertTrue(validate_repo(ROOT, allow_name_mismatch=True)['valid'])

    def test_frontmatter_accepts_current_skill(self):
        content = (ROOT/'SKILL.md').read_text(encoding='utf-8')
        self.assertEqual(validate_frontmatter(content, 'learn-any-skill')['name'], 'learn-any-skill')

    def test_frontmatter_rejects_directory_mismatch(self):
        with self.assertRaisesRegex(DataError, 'does not match'):
            validate_frontmatter((ROOT/'SKILL.md').read_text(encoding='utf-8'), 'wrong-name')

    def test_explicit_archive_audit_can_ignore_directory_name(self):
        front = validate_frontmatter((ROOT/'SKILL.md').read_text(encoding='utf-8'), 'learn-any-skill-main', True)
        self.assertEqual(front['name'], 'learn-any-skill')

    def test_frontmatter_rejects_missing_delimiter(self):
        with self.assertRaises(DataError): validate_frontmatter('name: a', 'a')

    def test_frontmatter_rejects_unclosed_header(self):
        with self.assertRaises(DataError): validate_frontmatter('---\nname: a', 'a')

    def test_frontmatter_rejects_empty_description(self):
        with self.assertRaises(DataError):
            validate_frontmatter('---\nname: a\ndescription: ""\n---\nbody', 'a')

    def test_frontmatter_rejects_invalid_name(self):
        with self.assertRaises(DataError):
            validate_frontmatter('---\nname: a--b\ndescription: text\n---\nbody', 'a--b')

    def test_frontmatter_rejects_nonstring_metadata(self):
        with self.assertRaises(DataError):
            validate_frontmatter('---\nname: a\ndescription: text\nmetadata:\n  version: 2\n---\nbody','a')

    def test_yaml_rejects_duplicate_keys(self):
        with self.assertRaisesRegex(DataError, 'duplicate YAML'):
            parse_yaml('name: a\nname: b','demo')

    def test_yaml_cannot_construct_python_objects(self):
        with self.assertRaises(DataError):
            parse_yaml('!!python/object/apply:os.system ["echo unsafe"]', 'untrusted')

    def test_progress_initial_state_is_not_mastery(self):
        sample = ROOT/'examples/python-testing'
        state = load_json(sample/'progress.json')
        validate_progress(state, load_json(sample/'plan.json'))
        self.assertTrue(all(x['status'] == 'not_started' for x in state['lesson_status']))

    def test_progress_rejects_pass_without_evidence(self):
        sample = ROOT/'examples/python-testing'; state = load_json(sample/'progress.json')
        state['lesson_status'][0]['status'] = 'passed'
        with self.assertRaisesRegex(DataError, 'without assessment evidence'):
            validate_progress(state, load_json(sample/'plan.json'))

    def test_progress_rejects_unknown_current_lesson(self):
        sample = ROOT/'examples/python-testing'; state = load_json(sample/'progress.json')
        state['current_lesson_id'] = 'invented'
        with self.assertRaises(DataError): validate_progress(state, load_json(sample/'plan.json'))

    def test_progress_rejects_duplicate_lesson(self):
        sample = ROOT/'examples/python-testing'; state = load_json(sample/'progress.json')
        state['lesson_status'].append(copy.deepcopy(state['lesson_status'][0]))
        with self.assertRaises(DataError): validate_progress(state, load_json(sample/'plan.json'))

    def test_relative_markdown_link_is_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); readme = root/'README.md'
            readme.write_text('[missing](absent.md)', encoding='utf-8')
            with self.assertRaisesRegex(DataError,'broken/escaping'):
                markdown_links_exist(readme, root)

    def test_fenced_example_is_not_treated_as_real_link(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); readme = root/'README.md'
            readme.write_text(chr(96)*3 + 'md\n[placeholder](not-a-real-file.md)\n' + chr(96)*3,
                              encoding='utf-8')
            markdown_links_exist(readme, root)

    def test_schemas_reject_boolean_numeric_scores(self):
        from jsonschema import Draft202012Validator
        schema = load_json(ROOT/'schemas/resources.schema.json')
        sample = load_json(ROOT/'examples/resources.example.json')
        sample['resources'][0]['scores']['authority'] = True
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(sample)))

    def test_progress_schema_rejects_false_pass(self):
        from jsonschema import Draft202012Validator
        schema = load_json(ROOT/'schemas/progress.schema.json')
        sample = load_json(ROOT/'examples/python-testing/progress.json')
        sample['lesson_status'][0]['status'] = 'passed'
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(sample)))


if __name__ == '__main__':
    unittest.main()
