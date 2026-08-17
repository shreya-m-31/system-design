from abc import ABC, abstractmethod


class Duck(ABC):
    def __init__(self, fly_behavior, quack_behavior):
        self.fly_behavior = fly_behavior
        self.quack_behavior = quack_behavior

    def quack(self):
        self.quack_behavior.quack()

    def fly(self):
        self.fly_behavior.fly()

    def display(self):
        pass

    def swim(self):
        print("All ducks float, even decoys!")


class FlyBehavior(ABC):
    @abstractmethod
    def fly(self):
        pass


class QuackBehavior(ABC):
    @abstractmethod
    def quack(self):
        pass

class FlyWithWings(FlyBehavior):
    def fly(self):
        print("I'm flying!")

class FlyNoWay(FlyBehavior):
    def fly(self):
        print("I can't fly")

class Quack(QuackBehavior):
    def quack(self):
        print("Quack")

class Squeak(QuackBehavior):
    def quack(self):
        print("Squeak")

class MuteQuack(QuackBehavior):
    def quack(self):
        print("<< Silence >>")

class RedheadDuck(Duck):
    def __init__(self):
        super().__init__(FlyWithWings(), Quack())

class RubberDuck(Duck):
    def __init__(self):
        super().__init__(FlyNoWay(), Squeak())

class DecoyDuck(Duck):
    def __init__(self):
        super().__init__(FlyNoWay(), MuteQuack())

class MallardDuck(Duck):
    def __init__(self):
        super().__init__(FlyWithWings(), Quack())

class ModelDuck(Duck):
    def __init__(self):
        super().__init__(FlyNoWay(), Quack())

if __name__ == "__main__":
    mallard = MallardDuck()
    mallard.quack()
    mallard.fly()