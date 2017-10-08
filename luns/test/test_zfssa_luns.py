import unittest
import sys
import os
from luns.zfssa_luns import response_size, get_real_size, get_real_blocksize, read_lun_file,\
                       read_yaml_file, create_parser, main

HERE = os.path.abspath(os.path.dirname(__file__))

LUNFILEOUTPUT = [['pool_0', 'unittest', 'lun01']]

YAMLOUTPUT = {'username': 'root', 'ip': '192.168.56.150', 'password': 'password'}


class TestCommon(unittest.TestCase):
    """Test common script functions"""

    def test_response_size(self):
        """Test response_size function to print human readable sizes"""
        self.assertEqual(response_size(10240), '10 KB')
        self.assertEqual(response_size(9437184), '9 MB')
        self.assertEqual(response_size(103809024), '99 MB')
        self.assertEqual(response_size(137438953472), '128 GB')
        self.assertEqual(response_size(140737488355), '131.07 GB')

    def test_get_real_size(self):
        """Test get_real_size function to convert input sizes (integer and string) to integer"""
        self.assertEqual(get_real_size(3, 'kb'), 3072)
        self.assertEqual(get_real_size(3, 'Mb'), 3145728)
        self.assertEqual(get_real_size(3, 'gb'), 3221225472)
        self.assertEqual(get_real_size(3, 'tB'), 3298534883328)

    def test_get_real_blocksize(self):
        """Test get_real_blocksize function to convert a string to integer"""
        self.assertEqual(get_real_blocksize('512'), '512')
        self.assertEqual(get_real_blocksize('8K'), 8192)
        self.assertEqual(get_real_blocksize('128k'), 131072)
        self.assertEqual(get_real_blocksize('1M'), 1048576)

    def test_read_lun_file(self):
        """Test read_lun_file function to read a test csv file"""
        self.assertEqual(read_lun_file(os.path.join(HERE, "test_destroy_lun.csv")), LUNFILEOUTPUT)

    def test_read_yaml_file(self):
        """Test read_yaml_file function to read a regular yml file"""
        self.assertEqual(read_yaml_file(os.path.join(HERE, "serverOS86.yml")), YAMLOUTPUT)

    def test_parser_complete(self):
        """Test create_parser to get expected CLI options"""
        parser = create_parser()
        argscomplete = parser.parse_args(['-s', 'test.yml', '-f', 'test.csv', '-l'])
        result = argscomplete.server, argscomplete.file, argscomplete.list
        self.assertEqual(result, ('test.yml', 'test.csv', True))

    @unittest.expectedFailure
    def test_parser_missing_group(self):
        """Test create_parser to get missing CLI options"""
        parser = create_parser()
        argsincomplete = parser.parse_args(['-s', 'test.yml', '-f', 'test.csv'])
        result = argsincomplete.server, argsincomplete.file, argsincomplete.list
        self.assertEqual(result, ('test.yml', 'test.csv', True))


CREATEOUTPUT = """###############################################################################
Creating luns
###############################################################################
CREATE - SUCCESS - lun 'lun01' project 'unittest' pool 'pool_0'
===============================================================================
"""

LISTOUTPUT = "LIST - PRESENT - name 'lun01' project 'unittest' pool 'pool_0'"

DELETEOUTPUT = """###############################################################################
Deleting luns
###############################################################################
DELETE - SUCCESS - lun 'lun01' project 'unittest' pool 'pool_0'
===============================================================================
"""


class TestOS86(unittest.TestCase):
    """Test with ZFSSA OS8.6 simulator, needs to be run in buffered mode"""

    def test_00_main_create_lun(self):
        """Test main with arguments to use create_lun function"""
        parser = create_parser()
        serverfile = os.path.join(HERE, 'serverOS86.yml')
        lunscreatefile = os.path.join(HERE, 'test_create_lun.csv')
        args = parser.parse_args(['-s', serverfile, '-f', lunscreatefile, '-c'])
        main(args)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip().split("\n")[:-2]  # remove (duration)
        self.assertEqual(output, CREATEOUTPUT.split("\n")[:-2])

    def test_01_main_list_lun(self):
        """Test main with arguments to use list_lun function"""
        parser = create_parser()
        serverfile = os.path.join(HERE, 'serverOS86.yml')
        lunscreatefile = os.path.join(HERE, 'test_create_lun.csv')
        args = parser.parse_args(['-s', serverfile, '-f', lunscreatefile, '-l'])
        main(args)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip().split("\n")[3][:62]  # just part of the line
        self.assertEqual(output, LISTOUTPUT)

    def test_02_main_delete_lun(self):
        """Test main with arguments to use delete_lun function"""
        parser = create_parser()
        serverfile = os.path.join(HERE, 'serverOS86.yml')
        lunsdestroyfile = os.path.join(HERE, 'test_destroy_lun.csv')
        args = parser.parse_args(['-s', serverfile, '-f', lunsdestroyfile, '-d'])
        main(args)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip().split("\n")[:-2]  # remove (duration)
        self.assertEqual(output, DELETEOUTPUT.split("\n")[:-2])


class TestOS87(unittest.TestCase):
    """Test with ZFSSA OS8.7 simulator, needs to be run in buffered mode"""

    def test_00_main_create_lun(self):
        """Test main with arguments to use create_lun function"""
        parser = create_parser()
        serverfile = os.path.join(HERE, 'serverOS87.yml')
        lunscreatefile = os.path.join(HERE, 'test_create_lun.csv')
        args = parser.parse_args(['-s', serverfile, '-f', lunscreatefile, '-c'])
        main(args)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip().split("\n")[:-2]  # remove (duration)
        self.assertEqual(output, CREATEOUTPUT.split("\n")[:-2])

    def test_01_main_list_lun(self):
        """Test main with arguments to use list_lun function"""
        parser = create_parser()
        serverfile = os.path.join(HERE, 'serverOS87.yml')
        lunscreatefile = os.path.join(HERE, 'test_create_lun.csv')
        args = parser.parse_args(['-s', serverfile, '-f', lunscreatefile, '-l'])
        main(args)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip().split("\n")[3][:62]  # just part of the line
        self.assertEqual(output, LISTOUTPUT)

    def test_02_main_delete_lun(self):
        """Test main with arguments to use delete_lun function"""
        parser = create_parser()
        serverfile = os.path.join(HERE, 'serverOS87.yml')
        lunsdestroyfile = os.path.join(HERE, 'test_destroy_lun.csv')
        args = parser.parse_args(['-s', serverfile, '-f', lunsdestroyfile, '-d'])
        main(args)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip().split("\n")[:-2]  # remove (duration)
        self.assertEqual(output, DELETEOUTPUT.split("\n")[:-2])


if __name__ == "__main__":
    unittest.main()
