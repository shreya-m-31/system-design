from abc import ABC, abstractmethod

class Beverage(ABC):
    def __init__(self, description: str):
        self.description = description

    @abstractmethod
    def cost(self) -> float:
        pass

    def get_description(self) -> str:
        return self.description

class Espresso(Beverage):
    def __init__(self):
        super().__init__(description="Espresso")

    def cost(self) -> float:
        return 1.99

class HouseBlend(Beverage):
    def __init__(self):
        super().__init__(description="House Blend")

    def cost(self) -> float:
        return 0.89

class DarkRoast(Beverage):
    def __init__(self):
        super().__init__(description="Dark Roast")

    def cost(self) -> float:
        return 0.99

class Decaf(Beverage):
    def __init__(self):
        super().__init__(description="Decaf")

    def cost(self) -> float:
        return 1.05

class Condiments(Beverage):
    def __init__(self, beverage: Beverage, description: str):
        self.beverage = beverage
        super().__init__(description)

    @abstractmethod
    def cost(self) -> float:
        pass

    def get_description(self) -> str:
        return self.beverage.get_description() + ", " + self.description

class Milk(Condiments):
    def __init__(self, beverage: Beverage):
        super().__init__(beverage, description="Milk")

    def cost(self) -> float:
        return self.beverage.cost() + 0.10

class Mocha(Condiments):
    def __init__(self, beverage: Beverage):
        super().__init__(beverage, description="Mocha")

    def cost(self) -> float:
        return self.beverage.cost() + 0.20

class Soy(Condiments):
    def __init__(self, beverage: Beverage):
        super().__init__(beverage, description="Soy")

    def cost(self) -> float:
        return self.beverage.cost() + 0.15

class Whip(Condiments):
    def __init__(self, beverage: Beverage):
        super().__init__(beverage, description="Whip")

    def cost(self) -> float:
        return self.beverage.cost() + 0.10


if __name__ == "__main__":
    beverage = Espresso()
    print(beverage.get_description() + " $" + str(beverage.cost()))

    beverage2 = DarkRoast()
    beverage2 = Mocha(beverage2)
    beverage2 = Mocha(beverage2)
    beverage2 = Whip(beverage2)
    print(beverage2.get_description() + " $" + str(beverage2.cost()))
