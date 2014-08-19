from .. import unittest

from fig.config import (
    ConfigError,
    ServiceConfigSchema,
    get_config,
)


class GetConfigTest(unittest.TestCase):

    def test_get_config_valid(self):
        config = get_config('tests/fixtures/simple-figfile/fig.yml')
        self.assertEqual(config.keys(), ['simple', 'another']) 

    def test_get_config_not_a_dict(self):
        filename = 'tests/fixtures/invalid-figfile/list.yml'
        with self.assertRaises(ConfigError) as exc_context:
            get_config(filename)
        self.assertEqual('Config in "%s" is not a dict.' % filename,
                         str(exc_context.exception))

    def test_service_config_schema(self):
        config = ServiceConfigSchema().deserialize({'foo': 'bar'})
        self.assertEqual(config, '')
