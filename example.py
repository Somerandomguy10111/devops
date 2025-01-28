import deptry

_ = deptry

class ExampleClass:
    def __init__(self, a : float, b : float):
        self.a : float = a
        self.b : float = b

    def sum(self) -> float:
        return self.a + self.b

    def multiply(self) -> float:
        return self.a * self.b