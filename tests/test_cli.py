import unittest

from click.testing import CliRunner

from meme_manager import cli
from meme_manager import __version__


class TestGeneralOptions(unittest.TestCase):
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(__version__, result.output)
