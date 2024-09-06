from flask import Flask, request, jsonify
from abc import ABC, abstractmethod

application = Flask(__name__)

#Определим модель данных для Дрона
class DroneModel:
    def __init__(self):
        self.height = 0  #Высота на которой находится дрон (стартовая принята за 0)
        self.velocity = 0  #Скорость движения дрона (начальная скорость равна 0)
        self.coordinates = (0, 0)  #Координаты дрона (начальные принимаем за 0,0)
        self.battery = 100  #Уровень заряда батареи (будем выражать в % от полного заряда)
    def update_coordinates(self, new_coordinates):
        self.coordinates = new_coordinates
    def update_height(self, new_height):
        self.height = new_height
    def update_velocity(self, new_velocity):
        self.velocity = new_velocity
    def reduce_battery(self, reduce):
        self.battery -= reduce

#Определеним представление Дрона
class DroneView:
    def show_status(self, model):
        return {
            "Высота:": model.height,
            "Скорость:": model.velocity,
            "Координаты": model.coordinates,
            "Заряд": model.battery
        }
    def warning(self, message):
        return {"warning": message}

#Опишем контроллер Дрона
class DroneController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.flight_strategy = None
    def regulate_position(self, new_coordinates):
        self.model.update_coordinates(new_coordinates)
        return self.view.show_status(self.model)
    def regulate_height(self, new_height):
        self.model.update_height(new_height)
        return self.view.show_status(self.model)
    def regulate_velocity(self, new_velocity):
        self.model.update_velocity(new_velocity)
        return self.view.show_status(self.model)
    def battery_control(self):
        if self.model.battery < 20:
            return self.view.warning("Низкий заряд батареи, возвращаемся на исходную позицию!")
        return {"battery_level": self.model.battery}
    def return_to_base(self):
        self.model.update_coordinates((0, 0))
        self.model.update_height(0)
        self.model.update_velocity(0)
        return self.view.warning("БПЛА успешно вернулся на исходную позицию")

#Используем Flask для создания веб-интерфейса
Drone_model = DroneModel()
Drone_view = DroneView()
Drone_controller = DroneController(Drone_model, Drone_view)


@application.route('/status', methods=['GET'])
def get_status():
    return jsonify(Drone_view.show_status(Drone_model))
@application.route('/position', methods=['POST'])
def update_position():
    data = request.get_json()
    new_coordinates = data.get('coordinates', (0, 0))
    return jsonify(Drone_controller.regulate_position(new_coordinates))
@application.route('/height', methods=['POST'])
def update_height():
    data = request.get_json()
    new_height = data.get('height', 0)
    return jsonify(Drone_controller.regulate_height(new_height))
@application.route('/velocity', methods=['POST'])
def update_velocity():
    data = request.get_json()
    new_velocity = data.get('velocity', 0)
    return jsonify(Drone_controller.regulate_velocity(new_velocity))
@application.route('/battery', methods=['GET'])
def battery_control():
    return jsonify(Drone_controller.battery_control())
@application.route('/return_to_base', methods=['POST'])
def return_to_base():
    return jsonify(Drone_controller.return_to_base())
    
# Интерфейс Стратегии полета
class FlightStrategy(ABC):
    @abstractmethod
    def fly(self, model):
        pass
class NormalFlightStrategy(FlightStrategy):
    def fly(self, model):
        model.update_velocity(10)  # Устанавливаем скорость 10 м/с
        return "Полёт в обычном режиме со скоростью 10 м/с"
class TurboModeFlightStrategy(FlightStrategy):
    def fly(self, model):
        model.update_velocity(50)  # Устанавливаем скорость 50 м/с
        return "Полёт в турбо режиме со скоростью 50 м/с"
class ScanModeFlightStrategy(FlightStrategy):
    def fly(self, model):
        model.update_velocity(1)  # Устанавливаем скорость 1 м/с
        return "Полёт в режиме сканирования местности со скоростью 1 м/с"      
#Методы управления Дроном
class EngineSystem:
    def rpm_decorator(func): #Введем декоратор для оборотов двигателя
        def iner(*args):
            if func(*args)==100:
                return f'Двигатель работает на максимальной мощности)'
            else:
                return f'Двигатель работает на частоте {*args} об./мин. ({func(*args)}% максимальной мощности)'
    return iner
    def __init__(self,max_rpm = 10000):
        self.rpm = 0
        self.max_rpm = max_rpm
    def start(self):
        self.rpm = 10
        return {"Успешный запуск двигателя"}
    def stop(self):
        self.rpm = 0
        return {"Двигатель выключен"}
    @rpm_decorator #Применим декоратор для вычисления % задействования мощности двигателя
    def set_rpm(self,rpm):
        self.rpm = rpm
        return int(rpm/self.max_rpm)
class SensorSystem:
    def __init__(self,**kwargs):
        self.sensors=kwargs
    def calibrate(self,**real_parametrs)
        for i in self.sensors:
            self.sensors[i]=real_parametrs[i]
class NavigationSystem:
    def __init__(self):
        self.start_coordX = 0 #в дальнейшем предполагается запрос от системы навигации
        self.start_coordY = 0
    def set_destination(x,y):
        self.endpointX=x
        self.endpointY=y
    def return_to_home:
        self.endpointX = self.start_coordX
        self.endpointY = self.start_coordY

#Фасад для управления Дроном
class DroneFasade:
    def __init__(self):
        self.engine_system = EngineSystem()
        self.sensor_system = SensorSystem()
        self.navigation_system = NavigationSystem()
        self.flight_strategy = FlightStrategy()
    def engine_start:
        self.engine_system.start()
        self.sensor_system.calibrate()
        self.navigation_system.set_destination()
    def go_home:
        self.flight_strategy.NormalFlightStrategy()
        self.navigation_system.return_to_home()
        self.engine_system.stop()
        
  

#Запускаем приложение (с включенным режимом отладки)
if __name__ == '__main__':
    application.run(debug=True)
