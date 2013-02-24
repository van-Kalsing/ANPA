from bge       import logic
from mathutils import Vector
import math



# Получение объектов модели
scene             = logic.getCurrentScene()
ship              = scene.objects["Ship"]
ship_left_engine  = scene.objects["Left_engine"]
ship_right_engine = scene.objects["Right_engine"]
ship_top_engine   = scene.objects["Top_engine"]



# Параметры корабля и среды (!!!!! Перенести в модель)
ship_volume              = 0.001
ship_edge_length         = 0.1

ship_right_engine_offset = 0.5
ship_left_engine_offset  = 0.5
ship_right_engine_angle  = 0.79
ship_left_engine_angle   = 0.79

water_density            = 1000
gravity_factor           = 9.8
linear_friction_factor   = 0.1
angular_friction_factor  = 0.1



# Управление массой
delta_ship_mass       = 0.1
ship_mass_lower_limit = 0.1
ship_mass_upper_limit = 10


def change_ship_mass(direction):
	if direction == 1 or direction == -1:
		controller = logic.getCurrentController()
		ship       = controller.owner
		
		for sensor in controller.sensors:
			if sensor.triggered and sensor.positive:
				mass = ship.mass + delta_ship_mass * direction
				
				if mass < ship_mass_lower_limit:
					ship.mass = ship_mass_lower_limit
				elif mass > ship_mass_upper_limit:
					ship.mass = ship_mass_upper_limit
				else:
					ship.mass = mass
					
				break
	else:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
# Управление двигателями
def set_ship_engine_force(engine, relative_force):
	# Проверка входных данных
	if relative_force < -1 or relative_force > 1:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	# Обновление значения силы вырабатываемой двигателем
	engine_force          = relative_force * engine["force_upper_limit"]
	engine_delta_rotation = [0, 0, engine["rotation_force_dependence"] * engine_force]
	
	engine["force"]                            = engine_force
	engine["rotation_toggle"]                  = 0
	engine.actuators["rotation_actuator"].dRot = engine_delta_rotation
	engine["rotation_toggle"]                  = 1
	
	
set_ship_right_engine_force = \
	lambda relative_force: (set_ship_engine_force(ship_right_engine, relative_force))
	
set_ship_left_engine_force = \
	lambda relative_force: (set_ship_engine_force(ship_left_engine, relative_force))
	
set_ship_top_engine_force = \
	lambda relative_force: (set_ship_engine_force(ship_top_engine, relative_force))
	
	
	
# Расчет сил действующих на корабль
def update_ship_forces():
	# Вычисление параметров корабля
	mass             = ship.mass
	linear_velocity  = Vector(ship.getLinearVelocity(True))
	angular_velocity = Vector(ship.getAngularVelocity(True))
	immersed_volume  = ship_volume * (0.5 - ship.position.z / ship_edge_length)
	
	if immersed_volume < 0:
		immersed_volume = 0
	elif immersed_volume > ship_volume:
		immersed_volume = ship_volume
		
		
	# Вычисление действующих на корабль сил
	if immersed_volume > 0.1 * ship_volume:
		right_engine_force  = ship_right_engine["force"] * Vector([0, 1, 0])
		right_engine_torque = \
			ship_right_engine["force"] * ship_right_engine_offset \
				* math.sin(ship_right_engine_angle) \
				* Vector([0, 0, 1])
				
		left_engine_force  = ship_left_engine["force"] * Vector([0, 1, 0])
		left_engine_torque = \
			ship_left_engine["force"] * ship_left_engine_offset \
				* math.sin(ship_left_engine_angle) \
				* Vector([0, 0, -1])
				
		top_engine_force = Vector([0, 0, ship_top_engine["force"]])
	else:
		right_engine_force  = Vector([0, 0, 0])
		right_engine_torque = Vector([0, 0, 0])
		
		left_engine_force  = Vector([0, 0, 0])
		left_engine_torque = Vector([0, 0, 0])
		
		top_engine_force = Vector([0, 0, 0])
		
	angular_friction_torque = - angular_friction_factor * angular_velocity.magnitude * angular_velocity
	linear_friction_force   = - linear_friction_factor * linear_velocity.magnitude * linear_velocity
	gravitation_force       = Vector([0, 0, - gravity_factor * mass])
	buoyancy_force          = Vector([0, 0, gravity_factor * water_density * immersed_volume])
	
	
	# Применение вычисленных сил
	ship.applyTorque(angular_friction_torque + right_engine_torque + left_engine_torque, True)
	ship.applyForce(
		linear_friction_force
			+ right_engine_force
			+ left_engine_force
			+ top_engine_force,
		True
	)
	ship.applyForce(buoyancy_force + gravitation_force)
	