from bge       import logic
from mathutils import Vector
import math



# Получение объектов модели
scene             = logic.getCurrentScene()
environment       = scene.objects["Environment"]
ship              = scene.objects["Ship"]
ship_left_engine  = scene.objects["Left_engine"]
ship_right_engine = scene.objects["Right_engine"]
ship_top_engine   = scene.objects["Top_engine"]



# История состояний аппарата
ship_history_max_depth = 2
ship_history           = []


def update_ship_history():
	if len(ship_history) > ship_history_max_depth:
		ship_history.pop()
		
	ship_position = ship.worldPosition
	ship_rotation = ship.worldOrientation.to_euler()
	
	ship_history.insert(0, {
		"position":    (ship_position.x, ship_position.y, ship_position.z),
		"orientation": (ship_rotation.x, ship_rotation.y, ship_rotation.z)
	})
	
	
def get_ship_state(depth):
	if depth <= ship_history_max_depth:
		if depth < len(ship_history):
			ship_state = ship_history[depth]
		else:
			ship_state = ship_history[0]
			
		return ship_state
	else:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
update_ship_history()



# Управление двигателями
def set_ship_engine_force(engine, relative_force):
	# Проверка границ относительной силы двигателя
	if relative_force < -1 or relative_force > 1:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	# Обновление значения силы вырабатываемой двигателем
	engine_force          = relative_force * engine["force_upper_limit"]
	engine_delta_rotation = [0, 0, engine["rotation_force_dependence"] * engine_force]
	
	engine["force"]                            = engine_force
	engine["rotation_toggle"]                  = 0
	engine.actuators["rotation_actuator"].dRot = engine_delta_rotation
	engine["rotation_toggle"]                  = 1
	
	
set_ship_right_engine_force, switch_off_ship_right_engine_force = \
	lambda relative_force: (set_ship_engine_force(ship_right_engine, relative_force)), \
		lambda: (set_ship_engine_force(ship_right_engine, 0))
		
set_ship_left_engine_force, switch_off_ship_left_engine_force = \
	lambda relative_force: (set_ship_engine_force(ship_left_engine, relative_force)), \
		lambda: (set_ship_engine_force(ship_left_engine, 0))
		
set_ship_top_engine_force, switch_off_ship_top_engine_force = \
	lambda relative_force: (set_ship_engine_force(ship_top_engine, relative_force)), \
		lambda: (set_ship_engine_force(ship_top_engine, 0))
		
		
		
# Вычисление характеристик движения
def compute_parameter_derivative(parameter_history, parameter_derivative_depth):
	if parameter_derivative_depth < len(parameter_history):
		parameter_derivative_history = parameter_history[:]
			
			
		parameter_history_max_depth = parameter_derivative_depth
		
		while parameter_history_max_depth > 0:
			parameter_history_depth = 0
			
			while parameter_history_depth < parameter_history_max_depth:
				parameter_derivative_value, parameter_derivative_previous_value = \
					parameter_derivative_history[parameter_history_depth], \
						parameter_derivative_history[parameter_history_depth + 1]
						
				parameter_derivative_history[parameter_history_depth] = \
					(parameter_derivative_value - parameter_derivative_previous_value) \
						* logic.getPhysicsTicRate()
						
				parameter_history_depth = parameter_history_depth + 1
				
			parameter_history_max_depth = parameter_history_max_depth - 1
			
			
		return parameter_derivative_history[0]
	else:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
def get_ship_movement_parameters_derivative(depth):
	ship_x_position_history, ship_y_position_history, ship_z_position_history = \
		[], [], []
		
		
	ship_history_depth = 0
	
	while ship_history_depth <= ship_history_max_depth:
		ship_x_position, ship_y_position, ship_z_position = \
			(get_ship_state(ship_history_depth))["position"]
			
		ship_x_position_history.append(ship_x_position)
		ship_y_position_history.append(ship_y_position)
		ship_z_position_history.append(ship_z_position)
		
		ship_history_depth = ship_history_depth + 1
		
		
	try:
		ship_movement_parameters_derivative = \
			compute_parameter_derivative(ship_x_position_history, depth), \
				compute_parameter_derivative(ship_y_position_history, depth), \
				compute_parameter_derivative(ship_z_position_history, depth)
	except:
		raise Exception() #!!!!! Создавать внятные исключения
	else:
		return ship_movement_parameters_derivative
		
		
def get_ship_rotation_parameters_derivative(depth):
	ship_x_orientation_history, ship_y_orientation_history, ship_z_orientation_history = \
		[], [], []
		
		
	ship_history_depth = 0
	
	while ship_history_depth <= ship_history_max_depth:
		ship_x_orientation, ship_y_orientation, ship_z_orientation = \
			(get_ship_state(ship_history_depth))["orientation"]
			
		ship_x_orientation_history.append(ship_x_orientation)
		ship_y_orientation_history.append(ship_y_orientation)
		ship_z_orientation_history.append(ship_z_orientation)
		
		ship_history_depth = ship_history_depth + 1
		
		
	try:
		ship_rotation_parameters_derivative = \
			compute_parameter_derivative(ship_x_orientation_history, depth), \
				compute_parameter_derivative(ship_y_orientation_history, depth), \
				compute_parameter_derivative(ship_z_orientation_history, depth)
	except:
		raise Exception() #!!!!! Создавать внятные исключения
	else:
		return ship_rotation_parameters_derivative
		
		
		
# Расчет сил действующих на корабль
def update_ship_forces():
	# Вычисление сил двигателей
	#
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
	#
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
	#
	
	# Определение центра аппарата
	ship_center_local_radius_vector = Vector([0, 0, ship["center_offset"]])
	ship_center_world_radius_vector = ship_center_local_radius_vector * ship.worldOrientation
	ship_center_world_position      = ship_center_world_radius_vector + ship.worldPosition
	
	
	# Вычисление объема и центра погруженной части аппарата
	ship_radius = ship["radius"]
	
	if ship_center_world_position.z >= ship_radius:
		# Аппарат находится над поверхностью
		immersed_volume                     = 0
		ship_immersed_center_world_position = \
			ship_center_world_position - Vector([0, 0, ship_radius])
	elif ship_center_world_position.z <= - ship_radius:
		# Аппарат скрыт под водой
		immersed_volume                     = 4 * math.pi * ship_radius ** 3 / 3
		ship_immersed_center_world_position = ship_center_world_position
	else:
		# Аппарат на границе вода-воздух
		immersed_part_hight = ship_radius - ship_center_world_position.z
		
		
		immersed_volume = \
			math.pi / 3 \
				* immersed_part_hight ** 2 \
				* (3 * ship_radius - immersed_part_hight)
				
		ship_immersed_center_offset = \
			3 / 4 \
				* (2 * ship_radius - immersed_part_hight) ** 2 \
				/ (3 * ship_radius - immersed_part_hight)
		ship_immersed_center_world_position = \
			ship_center_world_position - Vector([0, 0, ship_immersed_center_offset])
			
			
	buoyancy_force_magnitude = \
		environment["gravity_factor"] * environment["water_density"] * immersed_volume
		
	buoyancy_force  = buoyancy_force_magnitude * Vector([0, 0, 1])
	buoyancy_torque = \
		(ship_immersed_center_world_position - ship.worldPosition).cross(
			buoyancy_force
		)
		
		
		
	# Вычисление силы притяжения Земли
	#
	gravitation_force = Vector([0, 0, - environment["gravity_factor"] * ship.mass])
	
	
	
	# Применение вычисленных сил
	#
	ship.applyTorque(
		angular_friction_torque
			+ right_engine_torque
			+ left_engine_torque
			+ top_engine_torque,
		True
	)
	
	ship.applyForce(
		linear_friction_force
			+ right_engine_force
			+ left_engine_force
			+ top_engine_force,
		True
	)
	
	ship.applyTorque(buoyancy_torque)
	ship.applyForce(gravitation_force + buoyancy_force)
	