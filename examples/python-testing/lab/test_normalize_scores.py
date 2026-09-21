"""Reference tests. Write your own tests before studying these solutions."""
import unittest
from unittest.mock import Mock

from normalize_scores import mean_from_loader, normalize_scores


class NormalizeTests(unittest.TestCase):
    def test_normal_input(self):
        self.assertEqual(normalize_scores([20, 40, 100]), [.2, .4, 1.0])

    def test_boundaries(self):
        self.assertEqual(normalize_scores([0, 100]), [0.0, 1.0])

    def test_fraction(self):
        self.assertAlmostEqual(normalize_scores([12.5])[0], .125)

    def test_empty(self):
        with self.assertRaises(ValueError):
            normalize_scores([])

    def test_wrong_container(self):
        with self.assertRaises(TypeError):
            normalize_scores((30, 40))

    def test_boolean(self):
        with self.assertRaises(TypeError):
            normalize_scores([True])

    def test_string(self):
        with self.assertRaises(TypeError):
            normalize_scores(["50"])

    def test_nonfinite(self):
        for value in [float('nan'), float('inf'), float('-inf')]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_scores([value])

    def test_out_of_range(self):
        for value in [-1, 101, 10 ** 1000]:
            with self.subTest(value=str(value)[:20]), self.assertRaises(ValueError):
                normalize_scores([value])

    def test_input_unchanged(self):
        values = [25, 50]
        normalize_scores(values)
        self.assertEqual(values, [25, 50])

    def test_loader(self):
        loader = Mock(return_value=[20, 80])
        self.assertAlmostEqual(mean_from_loader(loader), .5)
        loader.assert_called_once_with()

    def test_loader_error(self):
        loader = Mock(side_effect=TimeoutError('demo timeout'))
        with self.assertRaises(TimeoutError):
            mean_from_loader(loader)
        loader.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
