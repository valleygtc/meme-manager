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
    def test_import_file_normal(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            Path('testimage.jpg').touch()
            result = runner.invoke(cli, ['import', 'testimage.jpg', 'testdb.sqlite'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('done', result.output)

    def test_import_dir_contain_files(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            Path('testdir').mkdir()
            Path('testdir/img1.jpg').touch()
            Path('testdir/img2.jpg').touch()
            result = runner.invoke(cli, ['import', 'testdir', 'testdb.sqlite'])
            self.assertEqual(result.exit_code, 0)

    def test_import_dir_contain_dirs_and_files(self):
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
            self.assertEqual(result.exit_code, 0)
            self.assertIn('Error', result.output)
    
    def test_import_db_not_exists(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path('testimage.jpg').touch()
            result = runner.invoke(cli, ['import', 'testimage.jpg', 'testdb.sqlite'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('Error', result.output)


class TestExport(unittest.TestCase):
    def test_normal(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(cli, ['initdb', 'testdb.sqlite'])
            Path('testdir').mkdir()
            result = runner.invoke(cli, ['export', 'testdb.sqlite', 'testdir'])
            self.assertEqual(result.exit_code, 0)
