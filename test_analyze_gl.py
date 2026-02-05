import unittest
import pandas as pd
import numpy as np
from analyze_gl import calculate_benford_stats

class TestBenfordAnalysis(unittest.TestCase):
    def test_benford_stats_basic(self):
        # Create synthetic data
        # 1, 10, 100 -> Leading 1 (3 times)
        # 2, 25 -> Leading 2 (2 times)
        # 500 -> Leading 5 (1 time)
        # 0 -> Ignored
        # -4 -> Leading 4 (1 time)
        data = [1, 10, 100, 2, 25, 500, 0, -4]
        series = pd.Series(data)

        results = calculate_benford_stats(series)

        # Check if results is a DataFrame
        self.assertIsInstance(results, pd.DataFrame)

        # Check index is 1-9
        self.assertListEqual(list(results.index), list(range(1, 10)))

        # Check specific counts
        # Total valid items = 7 (excluding 0)
        # 1s: 3
        # 2s: 2
        # 4s: 1
        # 5s: 1
        # Others: 0

        self.assertEqual(results.loc[1, 'Observed Count'], 3)
        self.assertEqual(results.loc[2, 'Observed Count'], 2)
        self.assertEqual(results.loc[4, 'Observed Count'], 1)
        self.assertEqual(results.loc[5, 'Observed Count'], 1)
        self.assertEqual(results.loc[3, 'Observed Count'], 0)

        # Check percentages
        self.assertAlmostEqual(results.loc[1, 'Observed %'], 3/7 * 100)
        self.assertAlmostEqual(results.loc[3, 'Observed %'], 0.0)

        # Check Expected % for 1 (approx 30.1%)
        self.assertAlmostEqual(results.loc[1, 'Expected %'], np.log10(1 + 1/1) * 100, places=4)

if __name__ == '__main__':
    unittest.main()
