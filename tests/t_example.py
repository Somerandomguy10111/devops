from holytools.devtools import Unittest


class ExampleClass:
    def __init__(self, a : float, b : float):
        self.a : float = a
        self.b : float = b

    def sum(self) -> float:
        return self.a + self.b

    def multiply(self) -> float:
        return self.a * self.b

class TestExample(Unittest):
    def setUp(self):
        self.example = ExampleClass(a=2,b=3)

    def test_addition(self):
        self.assertEqual(self.example.sum(), 5)

    def test_multiplication(self):
        self.assertEqual(self.example.multiply(), 6)


if __name__ == "__main__":
    TestExample.execute_all()