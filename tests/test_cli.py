import unittest
from pathlib import Path

from click.testing import CliRunner

from meme_manager import cli
from meme_manager import __version__


class TestGeneralOptions(unittest.TestCase):
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(__version__, result.output)


class TestInitdb(unittest.TestCase):
    def test_normal(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            self.assertEqual(result.exit_code, 0)
    
    def test_db_already_exists(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path('testdb.sqlite').touch()
            result = runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('Error', result.output)


class TestImport(unittest.TestCase):
    def test_import_file_default(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            Path('testimage.jpg').touch()
            result = runner.invoke(cli, ['import', 'testimage.jpg', 'testdb.sqlite'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('done', result.output)
    
    def test_import_file_with_group_option(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            Path('testimage.jpg').touch()
            result = runner.invoke(cli, ['import', '--group', 'testGroup', 'testimage.jpg', 'testdb.sqlite'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('done', result.output)

    def test_import_flat_dir(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            Path('testdir').mkdir()
            Path('testdir/img1.jpg').touch()
            Path('testdir/img2.jpg').touch()
            result = runner.invoke(cli, ['import', '--group', 'testGroup', 'testdir', 'testdb.sqlite'])
            self.assertEqual(result.exit_code, 0)
    
    def test_import_struct_dir(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            Path('testdir').mkdir()
            Path('testdir/group1').mkdir()
            Path('testdir/group1/img1.jpg').touch()
            Path('testdir/group1/img2.jpg').touch()
            Path('testdir/group2').mkdir()
            Path('testdir/group2/img1.jpg').touch()
            Path('testdir/group2/img2.jpg').touch()
            Path('testdir/img1.jpg').touch()
            result = runner.invoke(cli, ['import', 'testdir', 'testdb.sqlite'])
            self.assertEqual(result.exit_code, 0)
    
    def test_import_src_not_exists(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            result = runner.invoke(cli, ['import', 'notexistsSrc', 'testdb.sqlite'])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn('Error', result.output)
    
    def test_import_db_not_exists(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path('testimage.jpg').touch()
            result = runner.invoke(cli, ['import', 'testimage.jpg', 'testdb.sqlite'])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn('Error', result.output)


class TestExport(unittest.TestCase):
    def test_export_all(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            Path('testdir').mkdir()
            result = runner.invoke(cli, ['export', 'testdb.sqlite', 'testdir'])
            self.assertEqual(result.exit_code, 0)
    
    def test_export_db_not_exists(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path('testdir').mkdir()
            result = runner.invoke(cli, ['export', 'testdb.sqlite', 'testdir'])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn('Error', result.output)
    
    def test_export_dest_not_exists(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            result = runner.invoke(cli, ['export', 'testdb.sqlite', 'testdir'])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn('Error', result.output)
    
    # TODO: 得想法子搞定单元测试的 setUp tearDown 数据库初始化。
    # def test_export_group(self):
    #     runner = CliRunner()
    #     with runner.isolated_filesystem():
    #         runner.invoke(cli, ['initdb', 'testdb.sqlite'])
    #         Path('testdir').mkdir()
    #         result = runner.invoke(cli, ['export', '--group', 'testGroup', 'testdb.sqlite', 'testdir'])
    #         self.assertEqual(result.exit_code, 0)

    def test_export_name_pattern_not_support(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            Path('testdir').mkdir()
            result = runner.invoke(cli, ['export', '--name-pattern=illegalvalue', 'testdb.sqlite', 'testdir'])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn('Error', result.output)

    def test_export_explict_use_tag_as_filename(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            Path('testdir').mkdir()
            result = runner.invoke(cli, ['export', '--name-pattern=tag', 'testdb.sqlite', 'testdir'])
            self.assertEqual(result.exit_code, 0)

    def test_export_use_id_as_filename(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            Path('testdir').mkdir()
            result = runner.invoke(cli, ['export', '--name-pattern=id', 'testdb.sqlite', 'testdir'])
            self.assertEqual(result.exit_code, 0)
