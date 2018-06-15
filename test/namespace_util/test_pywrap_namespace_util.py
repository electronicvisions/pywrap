import unittest

class ConverterTest(unittest.TestCase):

    def test_import(self):
        """Check direct submodule import"""
        import namespace_utiltestmodule.A1

    def test_import2(self):
        """Check direct submodule import"""
        from namespace_utiltestmodule.A1.A2 import A3

    def test_namespace(self):
        """Check that everything is there and in the right namespace"""
        import namespace_utiltestmodule as mod

        mod.A1
        mod.A1.A2.A3
        mod.A1.in_a1
        mod.A1.A2.A3.in_a3

        mod.B1
        mod.B1.in_b1
        mod.B1.enum_0
        mod.B1.enum_1

        mod.in_global_a
        mod.in_global_b

if __name__ == '__main__':
        unittest.main()
