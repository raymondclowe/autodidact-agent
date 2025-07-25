# Example unit test for deep_research module
import unittest
import utils.deep_research as deep_research

class TestDeepResearch(unittest.TestCase):
    def test_lint(self):
        payload = '{"resources": [], "nodes": []}'
        result = deep_research.lint(payload)
        self.assertIsInstance(result, list)

if __name__ == "__main__":
    unittest.main()
