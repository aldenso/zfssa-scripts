Run tests for lun script
========================

Make sure you are in the luns path.

```text
$ pwd
~/zfs-scripts/luns
```

Run all test with buffered mode (required to test test_zfssa_luns.TestOS86).

```text
$ python -m unittest -v --buffer test_zfssa_luns
test_get_real_blocksize (test_zfssa_luns.TestCommon)
Test get_real_blocksize function to convert a string to integer ... ok
test_get_real_size (test_zfssa_luns.TestCommon)
Test get_real_size function to convert input sizes (integer and string) to integer ... ok
test_parser_complete (test_zfssa_luns.TestCommon)
Test create_parser to get expected CLI options ... ok
test_parser_missing_group (test_zfssa_luns.TestCommon)
Test create_parser to get missing CLI options ... expected failure
test_read_lun_file (test_zfssa_luns.TestCommon)
Test read_lun_file function to read a test csv file ... ok
test_read_yaml_file (test_zfssa_luns.TestCommon)
Test read_yaml_file function to read a regular yml file ... ok
test_response_size (test_zfssa_luns.TestCommon)
Test response_size function to print human readable sizes ... ok
test_00_main_create_lun (test_zfssa_luns.TestOS86)
Test main with arguments to use create_lun function ... ok
test_01_main_list_lun (test_zfssa_luns.TestOS86)
Test main with arguments to use list_lun function ... ok
test_02_main_delete_lun (test_zfssa_luns.TestOS86)
Test main with arguments to use delete_lun function ... ok

----------------------------------------------------------------------
Ran 10 tests in 26.283s

OK (expected failures=1)
```

Run test only for common functions.

```text
$ python -m unittest -v test_zfssa_luns.TestCommon
test_get_real_blocksize (test_zfssa_luns.TestCommon)
Test get_real_blocksize function to convert a string to integer ... ok
test_get_real_size (test_zfssa_luns.TestCommon)
Test get_real_size function to convert input sizes (integer and string) to integer ... ok
test_parser_complete (test_zfssa_luns.TestCommon)
Test create_parser to get expected CLI options ... ok
test_parser_missing_group (test_zfssa_luns.TestCommon)
Test create_parser to get missing CLI options ... expected failure
test_read_lun_file (test_zfssa_luns.TestCommon)
Test read_lun_file function to read a test csv file ... ok
test_read_yaml_file (test_zfssa_luns.TestCommon)
Test read_yaml_file function to read a regular yml file ... ok
test_response_size (test_zfssa_luns.TestCommon)
Test response_size function to print human readable sizes ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.010s

OK (expected failures=1)
```

Run test for test_zfssa_luns.TestOS86

```text
$ python -m unittest -v --buffer test_zfssa_luns.TestOS86
test_00_main_create_lun (test_zfssa_luns.TestOS86)
Test main with arguments to use create_lun function ... ok
test_01_main_list_lun (test_zfssa_luns.TestOS86)
Test main with arguments to use list_lun function ... ok
test_02_main_delete_lun (test_zfssa_luns.TestOS86)
Test main with arguments to use delete_lun function ... ok

----------------------------------------------------------------------
Ran 3 tests in 23.075s

OK
```
