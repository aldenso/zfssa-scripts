import unittest
from zfssa_luns import response_size

class TestCommon(unittest.TestCase):
    """Test common script functions"""

    def test_response_size(self):
        """Test response_size function to print human readable sizes"""
        self.assertEqual(response_size(10240), '10.00KB')
        self.assertEqual(response_size(9437184), '9.00MB')
        self.assertEqual(response_size(103809024), '99.00MB')
        self.assertEqual(response_size(137438953472), '128.00GB')
        self.assertEqual(response_size(140737488355), '131.07GB')

if __name__ == "__main__":
    unittest.main()
