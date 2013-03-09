from bge       import logic
from mathutils import Vector
import math



#!!!!! Магические константы
#????? Перенести в конфигурационный файл (или модель - много параметров)
ship_initial_position        = [0.0, 0.0, -5.0]
ship_initial_orientation     = [0.0, 0.0, 0.0]
ship_initial_angularVelocity = [0.0, 0.0, 0.0]
ship_initial_linearVelocity  = [0.0, 0.0, 0.0]



# Получение объектов модели
scene             = logic.getCurrentScene()
environment       = scene.objects["Environment"]
ship              = scene.objects["Ship"]
ship_left_engine  = scene.objects["Left_engine"]
ship_right_engine = scene.objects["Right_engine"]
ship_top_engine   = scene.objects["Top_engine"]



def reset_ship_state():
	ship.position        = ship_initial_position       
	ship.orientation     = ship_initial_orientation    
	ship.angularVelocity = ship_initial_angularVelocity
	ship.linearVelocity  = ship_initial_linearVelocity 
	
	
	
# Управление двигателями
def set_ship_engine_force(engine, relative_force):
	# Проверка границ относительной силы двигателя:
	# 	relative_force должна находится в пределах
	# 		от -1 (максимальная обратная тяга)
	# 		до  1 (максимальная прямая тяга)
	if relative_force < -1 or relative_force > 1:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	# Обновление значения силы вырабатываемой двигателем
	engine["force"] = relative_force * engine["force_upper_limit"]
	
	# Вращение осуществляется вокрут оси z в локальных координатах двигателя
	# 	(отлична от 0 только третья координата dRot)
	# Скорость вращения пропорциональна силе, вырабатываемой двигателем
	engine.actuators["rotation_actuator"].dRot = \
		[0, 0, engine["rotation_force_dependence"] * engine["force"]]
		
		
#!!!!! Добавить комментарий
set_ship_right_engine_force, switch_off_ship_right_engine = \
	lambda relative_force: (set_ship_engine_force(ship_right_engine, relative_force)), \
		lambda: (set_ship_engine_force(ship_right_engine, 0))
		
set_ship_left_engine_force, switch_off_ship_left_engine = \
	lambda relative_force: (set_ship_engine_force(ship_left_engine, relative_force)), \
		lambda: (set_ship_engine_force(ship_left_engine, 0))
		
set_ship_top_engine_force, switch_off_ship_top_engine = \
	lambda relative_force: (set_ship_engine_force(ship_top_engine, relative_force)), \
		lambda: (set_ship_engine_force(ship_top_engine, 0))
		
		
		
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
	