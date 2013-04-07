from optimization.controlsOptimization \
	import ControlsOptimizersConveyor,              \
				FixedTimeMovementControlsOptimizer, \
				FreeTimeMovementControlsOptimizer,  \
				TimeControlsOptimizer
				
from optimization.controlsEvolution \
	import ControlsPopulation,              \
				ControlsComplexPopulation,  \
				ControlsEvolutionParameters
				
from ship \
	import Ship,                      \
				ShipPosition,         \
				ShipOrientation,      \
				ShipAngularVelocity,  \
				ShipLinearVelocity,   \
				ShipLeftEngineForce,  \
				ShipRightEngineForce, \
				ShipTopEngineForce
				
from optimization.controls   import generate_control,reproduce_controls
from optimization.navigation import Navigation
from optimization.machine    import State, StateSpace, MetricStateSpace
from bge                     import logic
from mathutils               import Vector, Matrix

import math
import random





#!!!!!
targets_x_limits = -30, 30
targets_y_limits = -30, 30
targets_z_limits = -15, 15

ship_x_limits = -70,  70
ship_y_limits = -70,  70
ship_z_limits = -60, -30





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
	def _state_space_coordinates(self):
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
	def _state_space_coordinates(self):
		return self.__state_space_coordinates
		
		
	def _compute_distance(self, first_state, second_state):
		first_position  = Vector(first_state[ShipPosition()])
		second_position = Vector(second_state[ShipPosition()])
		
		return (second_position - first_position).magnitude
		
		
		
controls_arguments_space = \
	frozenset([
		"ship_x_world_position",
		"ship_y_world_position",
		"ship_z_world_position",
		# "ship_x_world_orientation",
		# "ship_y_world_orientation",
		# "ship_z_world_orientation",
		"target_x_local_position",
		"target_y_local_position",
		"target_z_local_position",
		# "horizontal_angle",
	])
	
	
	
	
	
class ShipNavigation(Navigation):
	__navigation = None
	
	
	@staticmethod
	def __get_initial_position():
		initial_position = \
			[
				random.uniform(*ship_x_limits),
				random.uniform(*ship_y_limits),
				random.uniform(*ship_z_limits)
			]
			
		return initial_position
		
		
		
	def __init__(self):
		super(ShipNavigation, self).__init__()
		
		
		scene = logic.getCurrentScene()
		
		if ShipNavigation.__navigation is None:
			ShipNavigation.__navigation = scene.objects["Navigation"]
			
		self.__ship          = Ship()
		self.__target_marker = scene.addObject("Target_marker", "Target_marker")
		
		self.__initial_position           = ShipNavigation.__get_initial_position()
		self.__initial_orientation        = [0.0, 0.0, 0.0]
		self.__initial_angular_velocity   = [0.0, 0.0, 0.0]
		self.__initial_linear_velocity    = [0.0, 0.0, 0.0]
		self.__left_engine_initial_force  = 0.0
		self.__right_engine_initial_force = 0.0
		self.__top_engine_initial_force   = 0.0
	# def __init__(self, targets_accounting_depth):
		# if targets_accounting_depth < 0:
			# raise Exception() #!!!!! Создавать внятные исключения
			
		# self.__targets_accounting_depth = targets_accounting_depth
		
		
		
	@property
	def machine(self):
		return self.__ship
		
		
	@property
	def targets_accounting_depth(self):
		return 1 #self.__targets_accounting_depth
		
		
	@property
	def complex_controls_arguments_space(self):
		return controls_arguments_space
		
		
	@property
	def complex_controls_state_space(self):
		return ShipControlsStateSpace()
		
		
	@property
	def targets_state_space(self):
		return ShipTargetsStateSpace()
		
		
		
	@property
	def confirming_distance(self):
		return ShipNavigation.__navigation["confirming_distance"]
		
		
		
	def generate_target(self):
		initial_position = Vector(self.__initial_position)
		
		return State({
			ShipPosition():
				[
					random.uniform(*targets_x_limits) + initial_position.x,
					random.uniform(*targets_y_limits) + initial_position.y,
					random.uniform(*targets_z_limits) + initial_position.z
				]
		})
		
		
	def reset_machine_state(self):
		initial_state = \
			State({
				ShipPosition():         self.__initial_position,
				ShipOrientation():      self.__initial_orientation,
				ShipAngularVelocity():  self.__initial_angular_velocity,
				ShipLinearVelocity():   self.__initial_linear_velocity,
				ShipLeftEngineForce():  self.__left_engine_initial_force,
				ShipRightEngineForce(): self.__right_engine_initial_force,
				ShipTopEngineForce():   self.__top_engine_initial_force
			})
			
		self.__ship.set_state(initial_state)
		
		
	def _compute_complex_control_value(self,
										complex_control,
										targets_source_view):
		target = targets_source_view.current_target[ShipPosition()]
		ship_position    = self.__ship.ship.worldPosition
		ship_orientation = self.__ship.ship.worldOrientation.to_euler()
		ship_orientation = Vector([ship_orientation.x, ship_orientation.y, ship_orientation.z])
		distance, _, local_target_course = self.__ship.ship.getVectTo(target)
		target_position  = distance * local_target_course
		
		horizontal_angle = math.asin(local_target_course.x / local_target_course.magnitude)
		if local_target_course.y < 0:
			if horizontal_angle >= 0:
				horizontal_angle = math.pi - horizontal_angle
			else:
				horizontal_angle = -math.pi - horizontal_angle
				
		arguments = \
			{
				"ship_x_world_position"    : ship_position.x,
				"ship_y_world_position"    : ship_position.y,
				"ship_z_world_position"    : ship_position.z,
				# "ship_x_world_orientation" : ship_orientation.x,
				# "ship_y_world_orientation" : ship_orientation.y,
				# "ship_z_world_orientation" : ship_orientation.z,
				"target_x_local_position" : target_position.x,
				"target_y_local_position" : target_position.y,
				"target_z_local_position" : target_position.z,
				# "horizontal_angle"        : horizontal_angle,
			}
			
			
		state_space_coordinates = complex_control.state_space.state_space_coordinates
		complex_control_values  = dict()
		
		try:
			for state_space_coordinate in state_space_coordinates:
				complex_control_values[state_space_coordinate] = \
					(complex_control[state_space_coordinate])(
						arguments
					)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
			
		return State(complex_control_values)
		
		
	def navigate(self, complex_control, targets_source_view):
		target_marker_position = \
			targets_source_view.current_target[
				ShipPosition()
			]
			
		self.__target_marker.worldPosition = list(target_marker_position)
		
		
		try:
			super(ShipNavigation, self).navigate(
				complex_control,
				targets_source_view
			)
		except Exception as exception:
			raise exception #!!!!! Создавать внятные исключения
			
			
			
			
			
def generate_controls_complex_population(max_control_depth,
											controls_evolution_parameters):
	controls_populations = dict()
	
	
	needed_controls_population_size = \
		controls_evolution_parameters.population_size
		
	state_space_coordinates = \
		ShipControlsStateSpace() \
			.state_space_coordinates
			
	for state_space_coordinate in state_space_coordinates:
		controls = []
		
		while len(controls) != needed_controls_population_size:
			control = \
				generate_control(
					max_control_depth,
					controls_arguments_space
				)
				
			controls.append(control)
			
		controls_populations[state_space_coordinate] = \
			ControlsPopulation(
				controls_arguments_space,
				controls
			)
			
			
	controls_complex_population = \
		ControlsComplexPopulation(
			controls_arguments_space,
			controls_populations
		)
		
	return controls_complex_population
	
	
scene        = logic.getCurrentScene()
optimization = scene.objects["Optimization"]

ship_navigations = \
	[ShipNavigation() for _
		in range(optimization["ships_number"])]
		
		
controls_evolution_parameters = \
	ControlsEvolutionParameters(
		selected_controls_number     = 5,
		reproduced_controls_number   = 10,
		control_mutation_probability = 0.3
	)
	
	
max_control_depth = 15





optimizer_0_iterations_numbers = 10
optimizer_0                    = \
	FreeTimeMovementControlsOptimizer(
		navigation                    = ship_navigations,
		controls_evolution_parameters = controls_evolution_parameters,
		control_tests_number          = 3,
		finishing_absolute_movement   = 30.0,
		interrupting_time             = 60.0
	)
	
	
optimizer_1_iterations_numbers = 10
optimizer_1                    = \
	FixedTimeMovementControlsOptimizer(
		navigation                    = ship_navigations,
		controls_evolution_parameters = controls_evolution_parameters,
		control_tests_number          = 3,
		finishing_time                = 2.0
	)
	
	
optimizer_2_iterations_numbers = 10
optimizer_2                    = \
	FixedTimeMovementControlsOptimizer(
		navigation                    = ship_navigations,
		controls_evolution_parameters = controls_evolution_parameters,
		control_tests_number          = 3,
		finishing_time                = 10.0
	)
	
	
optimizer_3_iterations_numbers = 10
optimizer_3                    = \
	TimeControlsOptimizer(
		navigation                         = ship_navigations,
		controls_evolution_parameters      = controls_evolution_parameters,
		control_tests_number               = 3,
		finishing_confirmed_targets_number = 3,
		interrupting_time                  = 120.0
	)
	
	
	
controls_optimizers = \
	[
		optimizer_0,
		optimizer_1,
		optimizer_2,
		optimizer_3
	]
	
	
controls_optimizers_iterations_numbers = \
	{
		optimizer_0: optimizer_0_iterations_numbers,
		optimizer_1: optimizer_1_iterations_numbers,
		optimizer_2: optimizer_2_iterations_numbers,
		optimizer_3: optimizer_3_iterations_numbers
	}
	
	
conveyor = \
	ControlsOptimizersConveyor(
		controls_optimizers,
		controls_optimizers_iterations_numbers
	)
	
	
	
	
	
def navigate_ship():
	if not conveyor.is_iteration_active:
		conveyor.start_iteration()
		
		
	is_iterated = False
	
	while not is_iterated:
		try:
			conveyor.iterate(1.0 / logic.getLogicTicRate())
		except:
			conveyor.buffer_controls_complex_population = \
				generate_controls_complex_population(
					max_control_depth,
					controls_evolution_parameters
				)
		else:
			is_iterated = True
			
			
			
			
			
def update_model():
	navigate_ship()
	Ship.update_ships_forces()
	