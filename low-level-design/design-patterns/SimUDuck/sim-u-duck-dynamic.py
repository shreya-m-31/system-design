from abc import ABC, abstractmethod


class Duck(ABC):
    def __init__(self):
        self.fly_behavior = None
        self.quack_behavior = None

    def set_fly_behavior(self, fly_behavior):
        self.fly_behavior = fly_behavior

    def set_quack_behavior(self, quack_behavior):
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

class FlyRocketPowered(FlyBehavior):
    def fly(self):
        print("I'm flying with a rocket!")

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
        super().__init__()
        self.set_fly_behavior(FlyWithWings())
        self.set_quack_behavior(Quack())

class RubberDuck(Duck):
    def __init__(self):
        super().__init__()
        self.set_fly_behavior(FlyNoWay())
        self.set_quack_behavior(Squeak())

class DecoyDuck(Duck):
    def __init__(self):
        super().__init__()
        self.set_fly_behavior(FlyNoWay())
        self.set_quack_behavior(MuteQuack())

class MallardDuck(Duck):
    def __init__(self):
        super().__init__()
        self.set_fly_behavior(FlyWithWings())
        self.set_quack_behavior(Quack())

class ModelDuck(Duck):
    def __init__(self):
        super().__init__()
        self.set_fly_behavior(FlyNoWay())
        self.set_quack_behavior(Quack())

    def display(self):
        print("I'm a model duck")

if __name__ == "__main__":
    mallard = MallardDuck()
    mallard.quack()
    mallard.fly()

    model = ModelDuck()
    model.quack()
    model.fly()

    model.set_fly_behavior(FlyRocketPowered())
    model.fly()