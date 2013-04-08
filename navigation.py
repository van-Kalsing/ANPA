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
from utilities.lattice       import Lattice
from bge                     import logic
from mathutils               import Vector, Matrix

import math
import random





#!!!!!
targets_x_limits = -30, 30
targets_y_limits = -30, 30
targets_z_limits = -15, 15

ship_x_limits = -90,  90
ship_y_limits = -90,  90
ship_z_limits = -90, -30





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
		
		
		
		
		
class ShipNavigation(Navigation):
	__navigation = \
		logic.getCurrentScene() \
			.objects["Navigation"]
			
			
			
	def __init__(self,
					targets_accounting_depth,
					ship,
					initial_position):
		if targets_accounting_depth <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		super(ShipNavigation, self).__init__()
		
		
		self.__target_marker = \
			logic.getCurrentScene() \
				.addObject("Target_marker", "Target_marker")
				
		self.__initial_position           = initial_position
		self.__initial_orientation        = [0.0, 0.0, 0.0]
		self.__initial_angular_velocity   = [0.0, 0.0, 0.0]
		self.__initial_linear_velocity    = [0.0, 0.0, 0.0]
		self.__left_engine_initial_force  = 0.0
		self.__right_engine_initial_force = 0.0
		self.__top_engine_initial_force   = 0.0
		
		self.__ship                     = ship
		self.__targets_accounting_depth = targets_accounting_depth
		
		
		
	@property
	def machine(self):
		return self.__ship
		
		
	@property
	def targets_accounting_depth(self):
		return self.__targets_accounting_depth
		
		
	@property
	def complex_controls_arguments_space(self):
		controls_arguments_names = \
			[
				"ship_x_world_position",
				"ship_y_world_position",
				"ship_z_world_position",
				# "ship_x_world_orientation",
				# "ship_y_world_orientation",
				# "ship_z_world_orientation",
				# "horizontal_angle",
			]
			
		for target_number in range(self.__targets_accounting_depth):
			controls_arguments_names += \
				[
					"target_%s_x_local_position" % target_number,
					"target_%s_y_local_position" % target_number,
					"target_%s_z_local_position" % target_number
				]
				
				
		return frozenset(controls_arguments_names)
		
		
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
		ship_position    = self.__ship.ship.worldPosition
		# ship_orientation = self.__ship.ship.worldOrientation.to_euler()
		# ship_orientation = Vector([ship_orientation.x, ship_orientation.y, ship_orientation.z])
		
		# horizontal_angle = math.asin(local_target_course.x / local_target_course.magnitude)
		# if local_target_course.y < 0:
		# 	if horizontal_angle >= 0:
		# 		horizontal_angle = math.pi - horizontal_angle
		# 	else:
		# 		horizontal_angle = -math.pi - horizontal_angle
				
		arguments = \
			{
				"ship_x_world_position"    : ship_position.x,
				"ship_y_world_position"    : ship_position.y,
				"ship_z_world_position"    : ship_position.z,
				# "ship_x_world_orientation" : ship_orientation.x,
				# "ship_y_world_orientation" : ship_orientation.y,
				# "ship_z_world_orientation" : ship_orientation.z,
				# "horizontal_angle"        : horizontal_angle,
			}
			
			
		for target_number in range(self.__targets_accounting_depth):
			target = targets_source_view.get_target(target_number)[ShipPosition()]
			distance, _, local_target_course = self.__ship.ship.getVectTo(target)
			target_position  = distance * local_target_course
			
			arguments["target_%s_x_local_position" % target_number] = target_position.x
			arguments["target_%s_y_local_position" % target_number] = target_position.y
			arguments["target_%s_z_local_position" % target_number] = target_position.z
			
			
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
											controls_evolution_parameters,
											controls_arguments_space):
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
	
	
controls_evolution_parameters = \
	ControlsEvolutionParameters(
		selected_controls_number     = 5,
		reproduced_controls_number   = 10,
		control_mutation_probability = 0.3
	)
	
	
max_control_depth = 15





optimizer_0_ship_navigations = []
optimizer_1_ship_navigations = []


lattice = \
	Lattice([
		ship_x_limits,
		ship_y_limits,
		ship_z_limits
	])
	
optimization = \
	logic.getCurrentScene() \
		.objects["Optimization"]
		
for _ in range(optimization["ships_number"]):
	ship             = Ship()
	initial_position = lattice.generate_node()
	
	optimizer_0_ship_navigations.append(
		ShipNavigation(
			targets_accounting_depth = 1,
			ship                     = ship,
			initial_position         = initial_position
		)
	)
	
	optimizer_1_ship_navigations.append(
		ShipNavigation(
			targets_accounting_depth = 2,
			ship                     = ship,
			initial_position         = initial_position
		)
	)
	
	
optimizer_0_iterations_numbers = 10
optimizer_0                    = \
	FreeTimeMovementControlsOptimizer(
		navigation                    = optimizer_0_ship_navigations,
		controls_evolution_parameters = controls_evolution_parameters,
		control_tests_number          = 3,
		finishing_absolute_movement   = 30.0,
		interrupting_time             = 60.0
	)
	
	
optimizer_1_iterations_numbers = 10
optimizer_1                    = \
	FreeTimeMovementControlsOptimizer(
		navigation                    = optimizer_1_ship_navigations,
		controls_evolution_parameters = controls_evolution_parameters,
		control_tests_number          = 3,
		finishing_absolute_movement   = 90.0,
		interrupting_time             = 180.0
	)
	
	
	
controls_optimizers = \
	[
		optimizer_0,
		optimizer_1
	]
	
	
controls_optimizers_iterations_numbers = \
	{
		optimizer_0: optimizer_0_iterations_numbers,
		optimizer_1: optimizer_1_iterations_numbers
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
			arguments_space = \
				optimizer_0_ship_navigations[0] \
					.complex_controls_arguments_space
					
			conveyor.buffer_controls_complex_population = \
				generate_controls_complex_population(
					max_control_depth,
					controls_evolution_parameters,
					arguments_space
				)
		else:
			is_iterated = True
			
			
			
			
			
def update_model():
	navigate_ship()
	Ship.update_ships_forces()
	