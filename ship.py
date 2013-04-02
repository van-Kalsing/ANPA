from bge                  import logic
from mathutils            import Vector, Euler
from abc                  import ABCMeta, abstractmethod
from optimization.machine import StateSpaceCoordinate, \
									State,             \
									StateSpace,        \
									MetricStateSpace,  \
									Machine
import math





#!!!!! 1. Добавить проверки параметров при присвоении





#!!!!! Магические константы
#????? Перенести в конфигурационный файл (или модель - много параметров)
ship_initial_position           = [0.0, 0.0, -5.0]
ship_initial_orientation        = [0.0, 0.0, 0.0]
ship_initial_angular_velocity   = [0.0, 0.0, 0.0]
ship_initial_linear_velocity    = [0.0, 0.0, 0.0]
ship_left_engine_initial_force  = 0.0
ship_right_engine_initial_force = 0.0
ship_top_engine_initial_force   = 0.0



# Получение объектов модели
scene             = logic.getCurrentScene()
environment       = scene.objects["Environment"]
ship              = scene.objects["Ship"]
ship_left_engine  = scene.objects["Left_engine"]
ship_right_engine = scene.objects["Right_engine"]
ship_top_engine   = scene.objects["Top_engine"]





class Parameter(object):
	__metaclass__ = ABCMeta
	
	
	@abstractmethod
	def get_current_value(self):
		pass
		
	@abstractmethod
	def set_value(self, value):
		pass
		
		
		
		
		
class ShipPosition(StateSpaceCoordinate, Parameter):
	def get_current_value(self):
		return ship.worldPosition
		
	def set_value(self, value):
		ship.worldPosition = value
		
		
class ShipOrientation(StateSpaceCoordinate, Parameter):
	def get_current_value(self):
		return ship.worldOrientation.to_euler()
		
	def set_value(self, value):
		ship.worldOrientation = Euler(value).to_matrix()
		
		
class ShipAngularVelocity(StateSpaceCoordinate, Parameter):
	def get_current_value(self):
		return ship.angularVelocity
		
	def set_value(self, value):
		ship.angularVelocity = value
		
		
class ShipLinearVelocity(StateSpaceCoordinate, Parameter):
	def get_current_value(self):
		return ship.linearVelocity
		
	def set_value(self, value):
		ship.linearVelocity = value
		
		
class ShipLeftEngineForce(StateSpaceCoordinate, Parameter):
	def get_current_value(self):
		relative_force = \
			ship_left_engine["force"] \
				/ ship_left_engine["force_upper_limit"]
				
		return relative_force
		
	def set_value(self, relative_force):
		ship_left_engine["force"] = \
			relative_force \
				* ship_left_engine["force_upper_limit"]
				
				
class ShipRightEngineForce(StateSpaceCoordinate, Parameter):
	def get_current_value(self):
		relative_force = \
			ship_right_engine["force"] \
				/ ship_right_engine["force_upper_limit"]
				
		return relative_force
		
	def set_value(self, relative_force):
		ship_right_engine["force"] = \
			relative_force \
				* ship_right_engine["force_upper_limit"]
				
				
class ShipTopEngineForce(StateSpaceCoordinate, Parameter):
	def get_current_value(self):
		relative_force = \
			ship_top_engine["force"] \
				/ ship_top_engine["force_upper_limit"]
				
		return relative_force
		
	def set_value(self, relative_force):
		ship_top_engine["force"] = \
			relative_force \
				* ship_top_engine["force_upper_limit"]
				
				
				
				
				
class ShipControlsStateSpace(StateSpace):
	def __init__(self):
		super(ShipControlsStateSpace, self).__init__()
		
		
		state_space_coordinates = \
			[
				ShipLeftEngineForce(),
				ShipRightEngineForce(),
				ShipTopEngineForce()
			]
			
		self.__state_space_coordinates = \
			frozenset(
				state_space_coordinates
			)
			
			
	@property
	def state_space_coordinates(self):
		return self.__state_space_coordinates
		
		
class ShipTargetsStateSpace(MetricStateSpace):
	def __init__(self):
		super(ShipTargetsStateSpace, self).__init__()
		
		
		state_space_coordinates = \
			[
				ShipPosition()
			]
			
		self.__state_space_coordinates = \
			frozenset(
				state_space_coordinates
			)
			
			
	@property
	def state_space_coordinates(self):
		return self.__state_space_coordinates
		
		
	def _compute_distance(self, first_state, second_state):
		first_position  = Vector(first_state[ShipPosition()])
		second_position = Vector(second_state[ShipPosition()])
		
		return (second_position - first_position).magnitude
		
		
class ShipFullStateSpace(StateSpace):
	def __init__(self):
		super(ShipFullStateSpace, self).__init__()
		
		
		state_space_coordinates = \
			[
				ShipPosition(),
				ShipOrientation(),
				ShipAngularVelocity(),
				ShipLinearVelocity(),
				ShipLeftEngineForce(),
				ShipRightEngineForce(),
				ShipTopEngineForce()
			]
			
		self.__state_space_coordinates = \
			frozenset(
				state_space_coordinates
			)
			
			
	@property
	def state_space_coordinates(self):
		return self.__state_space_coordinates
		
		
		
		
		
class Ship(Machine):
	@property
	def _full_state_space(self):
		return ShipFullStateSpace()
		
		
	def _get_current_state(self, state_space):
		state_space_coordinates = state_space.state_space_coordinates
		current_values          = dict()
		
		for state_space_coordinate in state_space_coordinates:
			current_values[state_space_coordinate] = \
				state_space_coordinate.get_current_value()
				
		return State(current_values)
		
		
	def _set_state(self, state):
		state_space_coordinates = \
			state.state_space.state_space_coordinates
			
		for state_space_coordinate in state_space_coordinates:
			state_space_coordinate.set_value(
				state[state_space_coordinate]
			)
			
			
	def reset_state(self):
		initial_state = \
			State({
				ShipPosition():         ship_initial_position,
				ShipOrientation():      ship_initial_orientation,
				ShipAngularVelocity():  ship_initial_angular_velocity,
				ShipLinearVelocity():   ship_initial_linear_velocity,
				ShipLeftEngineForce():  ship_left_engine_initial_force,
				ShipRightEngineForce(): ship_right_engine_initial_force,
				ShipTopEngineForce():   ship_top_engine_initial_force
			})
			
		self._set_state(initial_state)
		
		
		
		
		
# Расчет сил действующих на корабль
def update_ship_forces():
	# Вычисление сил двигателей
	#
	def compute_engine_forces(engine, engine_force_local_direction):
		if engine.worldPosition.z < 0.1:
			engine_force_magnitude = engine["force"]
		else:
			engine_force_magnitude = 0
			
			
		ship_inverted_world_orientation = ship.worldOrientation.copy()
		ship_inverted_world_orientation.invert()
		
		engine_world_radius_vector = \
			Vector(engine.worldPosition) \
				- Vector(ship.worldPosition)
				
		engine_local_radius_vector = \
			ship_inverted_world_orientation \
				* engine_world_radius_vector
				
				
		force = \
			engine_force_magnitude \
				* engine_force_local_direction
				
		torque = \
			engine_force_magnitude \
				* engine_local_radius_vector.cross(engine_force_local_direction)
				
		torque += \
			engine_force_local_direction \
				* (- math.copysign(1, engine["rotation_force_dependence"])) \
				* engine["reaction_torque_factor"] \
				* force.magnitude
				
				
		return force, torque
		
		
	right_engine_force, right_engine_torque = \
		compute_engine_forces(ship_right_engine, Vector([0, 1, 0]))
		
	left_engine_force, left_engine_torque = \
		compute_engine_forces(ship_left_engine, Vector([0, 1, 0]))
		
	top_engine_force, top_engine_torque = \
		compute_engine_forces(ship_top_engine, Vector([0, 0, 1]))
		
		
		
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
	
	
	
	# Вращение винтов
	#
	ship_left_engine.actuators["rotation_actuator"].dRot = \
		[
			0,
			0,
			ship_left_engine["rotation_force_dependence"] \
				* ship_left_engine["force"]
		]
		
	ship_right_engine.actuators["rotation_actuator"].dRot = \
		[
			0,
			0,
			ship_right_engine["rotation_force_dependence"] \
				* ship_right_engine["force"]
		]
		
	ship_top_engine.actuators["rotation_actuator"].dRot = \
		[
			0,
			0,
			ship_top_engine["rotation_force_dependence"] \
				* ship_top_engine["force"]
		]
		