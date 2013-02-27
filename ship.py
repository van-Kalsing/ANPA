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

water_density            = 1000
gravity_factor           = 9.8



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
	# Вычисление сил двигателей
	def compute_engine_forces(engine, engine_force_local_direction):
		if engine.worldPosition.z < 0.1:
			engine_force_magnitude = engine["force"]
		else:
			engine_force_magnitude = 0
			
		engine_offset, engine_world_direction, _ = engine.getVectTo(ship.worldPosition)
		ship_inverted_world_orientation          = ship.worldOrientation.copy()
		ship_inverted_world_orientation.invert()
		
		engine_local_radius_vector = \
			- engine_offset * ship_inverted_world_orientation * engine_world_direction
			
		return (
			engine_force_magnitude * engine_force_local_direction,
			engine_force_magnitude * engine_local_radius_vector.cross(engine_force_local_direction)
		)
		
		
	right_engine_force, right_engine_torque = \
		compute_engine_forces(ship_right_engine, Vector([0, 1, 0]))
		
	left_engine_force, left_engine_torque = \
		compute_engine_forces(ship_left_engine, Vector([0, 1, 0]))
		
	top_engine_force, top_engine_torque = \
		compute_engine_forces(ship_top_engine, Vector([0, 0, 1]))
		
		
	# Реактивный момент вызванный двигателем вертикальной тяги
	top_engine_reaction_torque = \
		Vector([0, 0, - math.copysign(1, ship_top_engine["rotation_force_dependence"])]) \
			* ship["top_engine_reaction_torque_factor"] \
			* ship_top_engine["force"]
			
	top_engine_torque = top_engine_torque + top_engine_reaction_torque
	
	
	
	# Вычисление сил трения
	def compute_friction_force_component(velocity_component, friction_factor_component):
		return (
			- math.copysign(1, velocity_component)
				* friction_factor_component
				* (velocity_component ** 2)
		)
		
	linear_velocity       = Vector(ship.getLinearVelocity(True))
	linear_friction_force = \
		Vector([
			compute_friction_force_component(linear_velocity.x, ship["x_linear_friction_factor"]),
			compute_friction_force_component(linear_velocity.y, ship["y_linear_friction_factor"]),
			compute_friction_force_component(linear_velocity.z, ship["z_linear_friction_factor"])
		])
		
	angular_velocity        = Vector(ship.getAngularVelocity(True))
	angular_friction_torque = \
		Vector([
			compute_friction_force_component(angular_velocity.x, ship["x_angular_friction_factor"]),
			compute_friction_force_component(angular_velocity.y, ship["y_angular_friction_factor"]),
			compute_friction_force_component(angular_velocity.z, ship["z_angular_friction_factor"])
		])
		
		
		
	# Вычисление силы выталкивания
	immersed_volume  = ship_volume * (0.5 - ship.position.z / ship_edge_length)
	
	if immersed_volume < 0:
		immersed_volume = 0
	elif immersed_volume > ship_volume:
		immersed_volume = ship_volume
		
	ship_world_orientation = ship.worldOrientation.copy()
	
	buoyancy_force_magnitude       = gravity_factor * water_density * immersed_volume
	buoyancy_force_local_direction = Vector([0, 0, 1]) * ship_world_orientation
	
	ship_center_local_radius_vector = Vector([0, 0, 0.1])
		
	buoyancy_force  = buoyancy_force_magnitude * buoyancy_force_local_direction
	buoyancy_torque = \
		buoyancy_force_magnitude \
			* ship_center_local_radius_vector.cross(buoyancy_force_local_direction)
			
			
			
	# Вычисление силы притяжения Земли
	gravitation_force = Vector([0, 0, - gravity_factor * ship.mass])
	
	
	
	# Применение вычисленных сил
	ship.applyTorque(
		buoyancy_torque
			+ angular_friction_torque
			+ right_engine_torque
			+ left_engine_torque
			+ top_engine_torque,
		True
	)
	
	ship.applyForce(
		buoyancy_force
			+ linear_friction_force
			+ right_engine_force
			+ left_engine_force
			+ top_engine_force,
		True
	)
	
	ship.applyForce(gravitation_force)
	