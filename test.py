import unittest
# import "main.py" ????

class TestConfigLang(unittest.TestCase):
    def test_consts(self):
        config_lang = ConfigLang()
        config_lang.parse('(define X 10)')
        self.assertEqual(config_lang.consts['X'], 10)

    def test_exprs(self):
        config_lang = ConfigLang()
        config_lang.parse('@{10 + 20}')
        self.assertEqual(config_lang.eval('10 + 20'), 30)

    def test_arrays(self):
        config_lang = ConfigLang()
        config_lang.parse('(1 2 3)')
        self.assertEqual(config_lang.parse('(1 2 3)'), '[1, 2, 3]')

    def test_dicts(self):
        config_lang = ConfigLang()
        config_lang.parse('[name => "John", age => 30]')
        self.assertEqual(config_lang.parse('[name => "John", age => 30]'), '{"name": "John", "age": 30}')

    def test_print_func(self):
        config_lang = ConfigLang()
        config_lang.parse('print("Hello, world!")')
        self.assertEqual(config_lang.print_func('"Hello, world!"'), '"Hello, world!"')

    def test_max_func(self):
        config_lang = ConfigLang()
        config_lang.parse('max(10, 20, 30)')
        self.assertEqual(config_lang.max_func('10, 20, 30'), 30)

if __name__ == '__main__':
    unittest.main()