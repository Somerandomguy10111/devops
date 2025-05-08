import os
import sys
import traceback
import unittest
from unittest import case


class DirectoryLimitedLoader(unittest.TestLoader):
    def loadTestsFromModule(self, module, *, pattern=None):
        tests = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, case.TestCase) and obj not in (case.TestCase, case.FunctionTestCase):
                tests_dirpath = os.path.join(ROOT_DIRPATH, 'tests')

                if not tests_dirpath in sys.modules[obj.__module__].__file__:
                    continue

                tests.append(self.loadTestsFromTestCase(obj))

        load_tests = getattr(module, 'load_tests', None)
        # noinspection PyTypeChecker
        tests = self.suiteClass(tests)
        if load_tests is not None:
            try:
                return load_tests(self, tests, pattern)
            except Exception as e:
                error_case, error_message = _make_failed_load_tests(
                    module.__name__, e, self.suiteClass)
                self.errors.append(error_message)
                return error_case
        return tests

def _make_failed_load_tests(name, exception, suiteClass):
    message = 'Failed to call load_tests:\n%s' % (traceback.format_exc(),)
    return _make_failed_test(
        name, exception, suiteClass, message)

def _make_failed_test(methodname, exception, suiteClass, message):
    test = _FailedTest(methodname, exception)
    return suiteClass((test,)), message

class _FailedTest(case.TestCase):
    _testMethodName = None

    def __init__(self, method_name, exception):
        self._exception = exception
        super(_FailedTest, self).__init__(method_name)

    def __getattr__(self, name):
        if name != self._testMethodName:
            # noinspection PyUnresolvedReferences
            return super(_FailedTest, self).__getattr__(name)
        def testFailure():
            raise self._exception
        return testFailure


def run_unittests(start_dir : str, pattern : str):
    loader = DirectoryLimitedLoader()
    suite = loader.discover(start_dir=start_dir, pattern=pattern)
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-s', required=True)
    parser.add_argument('-p', required=True)
    parser.add_argument('-root', required=True)

    args = parser.parse_args()
    ROOT_DIRPATH = args.root
    run_unittests(start_dir=args.s, pattern=args.p)
