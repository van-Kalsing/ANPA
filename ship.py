#!!!!! 1. Добавить проверки параметров при присвоении

from optimization.machine \
	import StateSpaceCoordinate, \
				State, \
				StateSpace, \
				MetricStateSpace, \
				Machine
				
from abc       import ABCMeta, abstractmethod
from bge       import logic
from mathutils import Vector, Euler

import math







class Parameter(metaclass = ABCMeta):
	@abstractmethod
	def get_current_value(self, ship):
		pass
		
	@abstractmethod
	def set_value(self, ship, value):
		pass
		
		
		
		
		
class ShipPosition(StateSpaceCoordinate, Parameter):
	def get_current_value(self, ship):
		return list(ship.ship.worldPosition)
		
	def set_value(self, ship, value):
		ship.ship.worldPosition = list(value)
		
		
class ShipOrientation(StateSpaceCoordinate, Parameter):
	def get_current_value(self, ship):
		return ship.ship.worldOrientation.to_euler() #!!!!! Проверить
		
	def set_value(self, ship, value):
		ship.ship.worldOrientation = Euler(value).to_matrix() #!!!!! Проверить
		
		
class ShipAngularVelocity(StateSpaceCoordinate, Parameter):
	def get_current_value(self, ship):
		return list(ship.ship.angularVelocity)
		
	def set_value(self, ship, value):
		ship.ship.angularVelocity = list(value)
		
		
class ShipLinearVelocity(StateSpaceCoordinate, Parameter):
	def get_current_value(self, ship):
		return list(ship.ship.linearVelocity)
		
	def set_value(self, ship, value):
		ship.ship.linearVelocity = list(value)
		
		
class ShipLeftEngineForce(StateSpaceCoordinate, Parameter):
	def get_current_value(self, ship):
		relative_force = \
			ship.ship_left_engine["force"] \
				/ ship.ship_left_engine["force_upper_limit"]
				
		return relative_force
		
	def set_value(self, ship, relative_force):
		ship.ship_left_engine["force"] = \
			relative_force \
				* ship.ship_left_engine["force_upper_limit"]
				
				
class ShipRightEngineForce(StateSpaceCoordinate, Parameter):
	def get_current_value(self, ship):
		relative_force = \
			ship.ship_right_engine["force"] \
				/ ship.ship_right_engine["force_upper_limit"]
				
		return relative_force
		
	def set_value(self, ship, relative_force):
		ship.ship_right_engine["force"] = \
			relative_force \
				* ship.ship_right_engine["force_upper_limit"]
				
				
class ShipTopEngineForce(StateSpaceCoordinate, Parameter):
	def get_current_value(self, ship):
		relative_force = \
			ship.ship_top_engine["force"] \
				/ ship.ship_top_engine["force_upper_limit"]
				
		return relative_force
		
	def set_value(self, ship, relative_force):
		ship.ship_top_engine["force"] = \
			relative_force \
				* ship.ship_top_engine["force_upper_limit"]
				
				
				
				
				
class ShipFullStateSpace(StateSpace):
	def __init__(self, *args, **kwargs):
		super(ShipFullStateSpace, self).__init__(*args, **kwargs)
		
		self.__state_space_coordinates = \
			frozenset([
				ShipPosition(),
				ShipOrientation(),
				ShipAngularVelocity(),
				ShipLinearVelocity(),
				ShipLeftEngineForce(),
				ShipRightEngineForce(),
				ShipTopEngineForce()
			])
			
			
			
	@property
	def state_space_coordinates(self):
		return self.__state_space_coordinates
		
		
		
		
		
class Ship(Machine):
	__ships       = []
	__environment = None
	
	
	def __new__(ship_class, *args, **kwargs):
		if Ship.__environment is None:
			scene              = logic.getCurrentScene()
			Ship.__environment = scene.objects["Environment"]
			
			
		ship = \
			super(Ship, ship_class) \
				.__new__(ship_class, *args, **kwargs)
				
		Ship.__ships.append(ship)
		
		return ship
		
		
	@staticmethod
	def update_ships_forces():
		for ship in Ship.__ships:
			ship.__update_forces()
			
			
			
			
	def __init__(self):
		super(Ship, self).__init__()
		
		
		scene = logic.getCurrentScene()
		
		self.__target_marker = \
			scene.addObject(
				"Target_marker",
				"Target_marker"
			)
			
		self.__ship              = scene.addObject("Ship", "Ship")
		self.__ship_left_engine  = scene.addObject("Left_engine", "Left_engine")
		self.__ship_right_engine = scene.addObject("Right_engine", "Right_engine")
		self.__ship_top_engine   = scene.addObject("Top_engine", "Top_engine")
		
		self.__ship_left_engine.setParent(self.__ship)
		self.__ship_right_engine.setParent(self.__ship)
		self.__ship_top_engine.setParent(self.__ship)
		
		#!!!!! Временно
		self.f = False
		
		
		
	@property
	def ship(self):
		return self.__ship
		
		
	@property
	def ship_left_engine(self):
		return self.__ship_left_engine
		
		
	@property
	def ship_right_engine(self):
		return self.__ship_right_engine
		
		
	@property
	def ship_top_engine(self):
		return self.__ship_top_engine
		
		
		
	@property
	def _full_state_space(self):
		return ShipFullStateSpace()
		
		
	def _get_current_state(self, state_space):
		state_space_coordinates = state_space.state_space_coordinates
		current_values          = dict()
		
		for state_space_coordinate in state_space_coordinates:
			current_values[state_space_coordinate] = \
				state_space_coordinate.get_current_value(self)
				
		return State(current_values)
		
		
	def _set_state(self, state):
		engines_forces_coordinates = \
			[
				ShipLeftEngineForce(),
				ShipRightEngineForce(),
				ShipTopEngineForce()
			]
			
			
		state_space_coordinates = \
			state.state_space.state_space_coordinates
			
		for state_space_coordinate in state_space_coordinates:
			value = state[state_space_coordinate]
			
			if state_space_coordinate in engines_forces_coordinates:
				if value < -1.0:
					value = -1.0
				elif value > 1.0:
					value = 1.0
					
					
			state_space_coordinate.set_value(self, value)
			
			
			
	def set_target_marker_position(self, target_marker_position):
		#!!!!! Временно
		self.f = True
		
		self.__target_marker.worldPosition = list(target_marker_position)
		
		
		
	#!!!!! Отрефакторить
	def __update_forces(self):
		#!!!!! Временно
		if self.f:
			self.f = False
			
			self.__ship.restoreDynamics()
		else:
			self.__ship.suspendDynamics()
			
			return
			
			
		# Вычисление сил двигателей
		#
		def compute_engine_forces(engine, engine_force_local_direction):
			if engine.worldPosition.z < 0.1:
				engine_force_magnitude = engine["force"]
			else:
				engine_force_magnitude = 0
				
				
			ship_inverted_world_orientation = self.__ship.worldOrientation.copy()
			ship_inverted_world_orientation.invert()
			
			engine_world_radius_vector = \
				Vector(engine.worldPosition) \
					- Vector(self.__ship.worldPosition)
					
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
			compute_engine_forces(self.__ship_right_engine, Vector([0, 1, 0]))
			
		left_engine_force, left_engine_torque = \
			compute_engine_forces(self.__ship_left_engine, Vector([0, 1, 0]))
			
		top_engine_force, top_engine_torque = \
			compute_engine_forces(self.__ship_top_engine, Vector([0, 0, 1]))
			
			
			
		# Вычисление сил трения
		#
		def compute_friction_force_component(velocity_component, friction_factor_component):
			return (
				- math.copysign(1, velocity_component)
					* friction_factor_component
					* (velocity_component ** 2)
			)
			
		linear_velocity       = Vector(self.__ship.getLinearVelocity(True))
		linear_friction_force = \
			Vector([
				compute_friction_force_component(linear_velocity.x, self.__ship["x_linear_friction_factor"]),
				compute_friction_force_component(linear_velocity.y, self.__ship["y_linear_friction_factor"]),
				compute_friction_force_component(linear_velocity.z, self.__ship["z_linear_friction_factor"])
			])
			
		angular_velocity        = Vector(self.__ship.getAngularVelocity(True))
		angular_friction_torque = \
			Vector([
				compute_friction_force_component(angular_velocity.x, self.__ship["x_angular_friction_factor"]),
				compute_friction_force_component(angular_velocity.y, self.__ship["y_angular_friction_factor"]),
				compute_friction_force_component(angular_velocity.z, self.__ship["z_angular_friction_factor"])
			])
			
			
			
		# Вычисление силы выталкивания
		#
		
		# Определение центра аппарата
		ship_center_local_radius_vector = Vector([0, 0, self.__ship["center_offset"]])
		ship_center_world_radius_vector = ship_center_local_radius_vector * self.__ship.worldOrientation
		ship_center_world_position      = ship_center_world_radius_vector + self.__ship.worldPosition
		
		
		# Вычисление объема и центра погруженной части аппарата
		ship_radius = self.__ship["radius"]
		
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
			Ship.__environment["gravity_factor"] * Ship.__environment["water_density"] * immersed_volume
			
		buoyancy_force  = buoyancy_force_magnitude * Vector([0, 0, 1])
		buoyancy_torque = \
			(ship_immersed_center_world_position - self.__ship.worldPosition).cross(
				buoyancy_force
			)
			
			
			
		# Вычисление силы притяжения Земли
		#
		gravitation_force = Vector([0, 0, - Ship.__environment["gravity_factor"] * self.__ship.mass])
		
		
		
		# Применение вычисленных сил
		#
		self.__ship.applyTorque(
			angular_friction_torque
				+ right_engine_torque
				+ left_engine_torque
				+ top_engine_torque,
			True
		)
		
		self.__ship.applyForce(
			linear_friction_force
				+ right_engine_force
				+ left_engine_force
				+ top_engine_force,
			True
		)
		
		self.__ship.applyTorque(buoyancy_torque)
		self.__ship.applyForce(gravitation_force + buoyancy_force)
		
		
		
		# Вращение винтов
		#
		self.__ship_left_engine.actuators["rotation_actuator"].dRot = \
			[
				0,
				0,
				self.__ship_left_engine["rotation_force_dependence"] \
					* self.__ship_left_engine["force"]
			]
			
		self.__ship_right_engine.actuators["rotation_actuator"].dRot = \
			[
				0,
				0,
				self.__ship_right_engine["rotation_force_dependence"] \
					* self.__ship_right_engine["force"]
			]
			
		self.__ship_top_engine.actuators["rotation_actuator"].dRot = \
			[
				0,
				0,
				self.__ship_top_engine["rotation_force_dependence"] \
					* self.__ship_top_engine["force"]
			]
			