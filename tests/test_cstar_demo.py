import unittest

from space.cstar import transform_program, validate_program


class TransformProgramTests(unittest.TestCase):
    def test_keyword_swap_is_simultaneous(self):
        source = "ans = (a + b) - (c * d) / e;\nif (a <= b && c != d) { };"
        expected = "ans = (a - b) + (c / d) * e;\nif (a >= b || c == d) { };"
        self.assertEqual(transform_program(source, "KeywordSwap"), expected)

    def test_keyword_obf_replaces_tokens_not_identifier_substrings(self):
        source = "int gift;\nif (gift != 0) { gift = gift + 1; };"
        transformed = transform_program(source, "KeywordObf")
        self.assertIn("gift", transformed)
        self.assertIn("𐔸", transformed)
        self.assertIn("𐕀", transformed)
        self.assertIn("𐕂", transformed)
        self.assertIn("𐕐", transformed)

    def test_comments_are_not_transformed(self):
        source = "int ans; // + if !=\nans = 1 + 2;"
        transformed = transform_program(source, "KeywordObf")
        self.assertIn("// + if !=", transformed)
        self.assertIn("ans 𐕂 1 𐕐 2;", transformed)

    def test_empty_program_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Enter a C\\* program"):
            validate_program("  ")


if __name__ == "__main__":
    unittest.main()
