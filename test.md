# Run tests for All scripts

Make sure you are in zfssa-scripts path.

```text
$ pwd
~/zfssa-scripts
```

## Test Luns Script

Run common functions.

```text
$ python -m unittest -v luns.test.test_zfssa_luns.TestCommon
test_get_real_blocksize (luns.test.test_zfssa_luns.TestCommon)
Test get_real_blocksize function to convert a string to integer ... ok
test_get_real_size (luns.test.test_zfssa_luns.TestCommon)
Test get_real_size function to convert input sizes (integer and string) to integer ... ok
test_parser_complete (luns.test.test_zfssa_luns.TestCommon)
Test create_parser to get expected CLI options ... ok
test_parser_missing_group (luns.test.test_zfssa_luns.TestCommon)
Test create_parser to get missing CLI options ... expected failure
test_read_lun_file (luns.test.test_zfssa_luns.TestCommon)
Test read_lun_file function to read a test csv file ... ok
test_read_yaml_file (luns.test.test_zfssa_luns.TestCommon)
Test read_yaml_file function to read a regular yml file ... ok
test_response_size (luns.test.test_zfssa_luns.TestCommon)
Test response_size function to print human readable sizes ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.074s

OK (expected failures=1)
```

Run test TestOS86 (buffered mode required)

```text
$ python -m unittest -v --buffer luns.test.test_zfssa_luns.TestOS86
test_00_main_create_lun (luns.test.test_zfssa_luns.TestOS86)
Test main with arguments to use create_lun function ... ok
test_01_main_list_lun (luns.test.test_zfssa_luns.TestOS86)
Test main with arguments to use list_lun function ... ok
test_02_main_delete_lun (luns.test.test_zfssa_luns.TestOS86)
Test main with arguments to use delete_lun function ... ok

----------------------------------------------------------------------
Ran 3 tests in 39.651s

OK
```

Run TestCommon plus TestOS86

```text
# python -m unittest -v --buffer luns.test.test_zfssa_luns.TestCommon luns.test.test_zfssa_luns.TestOS86
test_get_real_blocksize (luns.test.test_zfssa_luns.TestCommon)
Test get_real_blocksize function to convert a string to integer ... ok
test_get_real_size (luns.test.test_zfssa_luns.TestCommon)
Test get_real_size function to convert input sizes (integer and string) to integer ... ok
test_parser_complete (luns.test.test_zfssa_luns.TestCommon)
Test create_parser to get expected CLI options ... ok
test_parser_missing_group (luns.test.test_zfssa_luns.TestCommon)
Test create_parser to get missing CLI options ... expected failure
test_read_lun_file (luns.test.test_zfssa_luns.TestCommon)
Test read_lun_file function to read a test csv file ... ok
test_read_yaml_file (luns.test.test_zfssa_luns.TestCommon)
Test read_yaml_file function to read a regular yml file ... ok
test_response_size (luns.test.test_zfssa_luns.TestCommon)
Test response_size function to print human readable sizes ... ok
test_00_main_create_lun (luns.test.test_zfssa_luns.TestOS86)
Test main with arguments to use create_lun function ... ok
test_01_main_list_lun (luns.test.test_zfssa_luns.TestOS86)
Test main with arguments to use list_lun function ... ok
test_02_main_delete_lun (luns.test.test_zfssa_luns.TestOS86)
Test main with arguments to use delete_lun function ... ok

----------------------------------------------------------------------
Ran 10 tests in 44.636s

OK (expected failures=1)
```

Run test TestOS87 (buffered mode required)

```text
$ python -m unittest -v --buffer luns.test.test_zfssa_luns.TestOS87
test_00_main_create_lun (luns.test.test_zfssa_luns.TestOS87)
Test main with arguments to use create_lun function ... ok
test_01_main_list_lun (luns.test.test_zfssa_luns.TestOS87)
Test main with arguments to use list_lun function ... ok
test_02_main_delete_lun (luns.test.test_zfssa_luns.TestOS87)
Test main with arguments to use delete_lun function ... ok

----------------------------------------------------------------------
Ran 3 tests in 65.086s

OK
```

## Test Snapshots scripts

Run TestOS86 (buffered mode required)

```text
$ python -m unittest -v --buffer snapshots.filesystems.test.test_zfssa_fs_sna
ps.TestOS86
test_00_main_create_snap (snapshots.filesystems.test.test_zfssa_fs_snaps.TestOS86)
Test main with arguments to use create_snap function ... ok
test_01_main_list_snap (snapshots.filesystems.test.test_zfssa_fs_snaps.TestOS86)
Test main with arguments to use list_snap function ... ok
test_02_main_delete_snap (snapshots.filesystems.test.test_zfssa_fs_snaps.TestOS86)
Test main with arguments to use delete_snap function ... ok

----------------------------------------------------------------------
Ran 3 tests in 9.951s

OK
```

Run TestOS87 (buffered mode required)

```text
$ python -m unittest -v --buffer snapshots.filesystems.test.test_zfssa_fs_snaps.TestOS87
test_00_main_create_snap (snapshots.filesystems.test.test_zfssa_fs_snaps.TestOS87)
Test main with arguments to use create_snap function ... ok
test_01_main_list_snap (snapshots.filesystems.test.test_zfssa_fs_snaps.TestOS87)
Test main with arguments to use list_snap function ... ok
test_02_main_delete_snap (snapshots.filesystems.test.test_zfssa_fs_snaps.TestOS87)
Test main with arguments to use delete_snap function ... ok

----------------------------------------------------------------------
Ran 3 tests in 37.937s

OK
```
