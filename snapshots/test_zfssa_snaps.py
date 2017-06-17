import unittest
import sys
from zfssa_snaps import create_parser, main


CREATEOUTPUT = """###############################################################################
Creating snapshots from test_snaps.csv
###############################################################################
CREATE - SUCCESS - Snapshot 'backup', filesystem 'fs01', project 'unittest', pool 'pool_0'
===============================================================================
"""

LISTOUTPUT = "LIST - PRESENT - Snapshot 'backup',\
 filesystem 'fs01', project 'unittest', pool 'pool_0'"

DELETEOUTPUT = """###############################################################################
Deleting snapshots
###############################################################################
DELETE - SUCCESS - Snapshot 'backup', filesystem 'fs01', project 'unittest', pool 'pool_0'
===============================================================================
"""


class TestOS86(unittest.TestCase):
    """Test with ZFSSA OS8.6 simulator, needs to be run in buffered mode"""

    def test_00_main_create_snap(self):
        """Test main with arguments to use create_snap function"""
        parser = create_parser()
        args = parser.parse_args(['-s', 'serverOS86.yml', '-f', 'test_snaps.csv', '-c'])
        main(args)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip().split("\n")[:-2]  # remove (duration)
        self.assertEqual(output, CREATEOUTPUT.split("\n")[:-2])

    def test_01_main_list_snap(self):
        """Test main with arguments to use list_snap function"""
        parser = create_parser()
        args = parser.parse_args(['-s', 'serverOS86.yml', '-f', 'test_snaps.csv', '-l'])
        main(args)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip().split("\n")[3][:88]  # just part of the line
        self.assertEqual(output, LISTOUTPUT)

    def test_02_main_delete_snap(self):
        """Test main with arguments to use delete_snap function"""
        parser = create_parser()
        args = parser.parse_args(['-s', 'serverOS86.yml', '-f', 'test_snaps.csv', '-d'])
        main(args)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip().split("\n")[:-2]  # remove (duration)
        self.assertEqual(output, DELETEOUTPUT.split("\n")[:-2])


class TestOS87(unittest.TestCase):
    """Test with ZFSSA OS8.7 simulator, needs to be run in buffered mode"""

    def test_00_main_create_snap(self):
        """Test main with arguments to use create_snap function"""
        parser = create_parser()
        args = parser.parse_args(['-s', 'serverOS87.yml', '-f', 'test_snaps.csv', '-c'])
        main(args)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip().split("\n")[:-2]  # remove (duration)
        self.assertEqual(output, CREATEOUTPUT.split("\n")[:-2])

    def test_01_main_list_snap(self):
        """Test main with arguments to use list_snap function"""
        parser = create_parser()
        args = parser.parse_args(['-s', 'serverOS87.yml', '-f', 'test_snaps.csv', '-l'])
        main(args)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip().split("\n")[3][:88]  # just part of the line
        self.assertEqual(output, LISTOUTPUT)

    def test_02_main_delete_snap(self):
        """Test main with arguments to use delete_snap function"""
        parser = create_parser()
        args = parser.parse_args(['-s', 'serverOS87.yml', '-f', 'test_snaps.csv', '-d'])
        main(args)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip().split("\n")[:-2]  # remove (duration)
        self.assertEqual(output, DELETEOUTPUT.split("\n")[:-2])


if __name__ == "__main__":
    unittest.main()

