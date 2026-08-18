from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self) -> None:
        pass

class Subject():
    def __init__(self) -> None:
        self.observers = []

    def register_observer(self, observer: Observer) -> None:
        self.observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        if observer in self.observers:
            self.observers.remove(observer)
        else:
            raise ValueError(f"Observer {observer} not found")

    def notify_observer(self) -> None:
        for observer in self.observers:
            observer.update()


class WeatherData(Subject):
    def __init__(self, temperature, humidity, pressure) -> None:
        super().__init__()
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure

    def get_temperature(self) -> float:
        return self.temperature

    def get_humidity(self) -> float:
        return self.humidity

    def get_pressure(self) -> float:
        return self.pressure

    def measurements_changed(self, temperature: float, humidity: float, pressure: float) -> None:
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.notify_observer()


class Display(ABC):

    @abstractmethod
    def display(self) -> None:
        pass


class CurrentConditionsDisplay(Observer, Display):
    def __init__(self, weather_data: WeatherData) -> None:
        self.weather_data = weather_data

    def update(self) -> None:
        self.temperature = self.weather_data.get_temperature()
        self.humidity = self.weather_data.get_humidity()
        self.pressure = self.weather_data.get_pressure()
        self.display()

    def display(self) -> None:
        print(f"Temperature: {self.temperature}, Humidity: {self.humidity}, Pressure: {self.pressure}")

class StatisticsDisplay(Observer, Display):
    def __init__(self, weather_data: WeatherData) -> None:
        self.weather_data = weather_data

    def update(self) -> None:
        self.temperature = self.weather_data.get_temperature()
        self.display()

    def display(self) -> None:
        print(f"Average Temperature: {self.temperature}")


class ForecastDisplay(Observer, Display):
    def __init__(self, weather_data: WeatherData) -> None:
        self.weather_data = weather_data

    def update(self) -> None:
        self.humidity = self.weather_data.get_humidity()
        self.pressure = self.weather_data.get_pressure()
        self.display()

    def display(self) -> None:
        print(f"Humidity: {self.humidity}, Pressure: {self.pressure}")


if __name__ == "__main__":
    weather_data = WeatherData(20, 60, 1013)
    current_conditions_display = CurrentConditionsDisplay(weather_data)
    statistics_display = StatisticsDisplay(weather_data)
    forecast_display = ForecastDisplay(weather_data)

    weather_data.register_observer(current_conditions_display)
    weather_data.register_observer(statistics_display)
    weather_data.register_observer(forecast_display)

    weather_data.notify_observer()
    weather_data.measurements_changed(21, 65, 1014)