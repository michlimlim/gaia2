import traceback


class TestCalculator:
    # :brief Encapsulate test execution.
    #
    # # Instance Variables
    #
    # - context_value: the string value of the test context
    # - num_error: the number of errors encountered
    # - num_test: the number of tests run so far
    # - tests: a list of tests in this test suite

    def __init__(self):
        # :brief Create a new TestCalculator instance
        # :return A new TestCalculator instance
        self.context_value = ""
        self.num_error = 0
        self.num_test = 0
        self.tests = []

    def add_test(self, test_fn):
        # :brief Add a test function to self.tests
        # :param test_fn a function that takes a TestCalculator instance as an
        # argument
        self.tests.append(test_fn)
        return None

    def run(self):
        # :brief Run the test suite.
        for test in self.tests:
            try:
                test(self)
                prefix = "\x1B[31m"
                if self.num_error == 0:
                    prefix = "\x1B[32m"
                if self.num_test == 1:
                    print(prefix + "In context \"" + self.context_value + "\", "
                          + str(self.num_test - self.num_error) + " of "
                          + str(self.num_test) + " test passed.\x1B[0m")
                else:
                    print(prefix + "In context \"" + self.context_value + "\", "
                          + str(self.num_test - self.num_error) + " of "
                          + str(self.num_test) + " tests passed.\x1B[0m")
            except:
                tb = traceback.format_exc()
                print("\x1B[31mUncaught exception in context \"" +
                      self.context_value + "\"!\x1B[0m")
                print("Exception value:\n" + tb)
            self.num_error = 0
            self.num_test = 0

    def context(self, str):
        # :brief Set the contents of a TestCalculator instance's context string.
        # :param str [string] the value of the new context string
        self.context_value = str

    def check(self, b):
        # :brief Check if a value is True
        # :param b [boolean] value to check
        if not b:
            self.num_error += 1
        self.num_test += 1

    def check_not(self, b):
        # :brief Check that a value is False
        # :param b [boolean] value to check
        if b:
            self.num_error += 1
        self.num_test += 1
