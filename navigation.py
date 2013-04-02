from optimization.controlsOptimization \
	import ControlsOptimizersConveyor,     \
				MovementControlsOptimizer, \
				TimeControlsOptimizer
				
from optimization.controlsEvolution \
	import ControlsPopulation,              \
				ControlsComplexPopulation,  \
				ControlsEvolutionParameters
	
from ship \
	import Ship,                        \
				ShipControlsStateSpace, \
				ShipTargetsStateSpace,  \
				ShipPosition
				
from optimization.controls   import generate_control,reproduce_controls
from optimization.navigation import Navigation
from optimization.machine    import State
from bge                     import logic
from mathutils               import Vector, Matrix

import math
import random



#!!!!! Временно
targets_x_limits = -30, 30
targets_y_limits = -30, 30
targets_z_limits = -35, -5


# Получение объектов модели
scene         = logic.getCurrentScene()
ship          = scene.objects["Ship"]
navigation    = scene.objects["Navigation"]
target_marker = scene.objects["Target_marker"]





controls_arguments_space = \
	frozenset([
		"ship_x_world_position",
		"ship_y_world_position",
		"ship_z_world_position",
		"ship_x_world_orientation",
		"ship_y_world_orientation",
		"ship_z_world_orientation",
		"target_x_local_position",
		"target_y_local_position",
		"target_z_local_position",
		"horizontal_angle",
	])
	
	
	
	
	
class ShipNavigation(Navigation):
	# def __init__(self, targets_accounting_depth):
		# if targets_accounting_depth < 0:
			# raise Exception() #!!!!! Создавать внятные исключения
			
		# self.__targets_accounting_depth = targets_accounting_depth
		
		
		
	@property
	def machine(self):
		return Ship()
		
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
		return navigation["confirming_distance"]
		
		
		
	def _compute_complex_control_value(self,
										complex_control,
										targets_source_view):
		target = targets_source_view.current_target[ShipPosition()]
		ship_position    = ship.worldPosition
		ship_orientation = ship.worldOrientation.to_euler()
		ship_orientation = Vector([ship_orientation.x, ship_orientation.y, ship_orientation.z])
		distance, _, local_target_course = ship.getVectTo(target)
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
				"ship_x_world_orientation" : ship_orientation.x,
				"ship_y_world_orientation" : ship_orientation.y,
				"ship_z_world_orientation" : ship_orientation.z,
				"target_x_local_position" : target_position.x,
				"target_y_local_position" : target_position.y,
				"target_z_local_position" : target_position.z,
				"horizontal_angle"        : horizontal_angle,
			}
			
			
		state_space_coordinates = complex_control.state_space.state_space_coordinates
		complex_control_values  = dict()
		
		for state_space_coordinate in state_space_coordinates:
			complex_control_values[state_space_coordinate] = \
				(complex_control[state_space_coordinate])(
					arguments
				)
				
		return State(complex_control_values)
		
		
	def navigate(self, complex_control, targets_source_view):
		target_marker.worldPosition = \
			targets_source_view.current_target[
				ShipPosition()
			]
			
		super(ShipNavigation, self).navigate(
			complex_control,
			targets_source_view
		)
		
		
		
		
		
def generate_random_target():
	return State({
		ShipPosition():
			[
				random.uniform(*targets_x_limits),
				random.uniform(*targets_y_limits),
				random.uniform(*targets_z_limits)
			]
	})
	
	
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
	
	
max_control_depth = 15

controls_evolution_parameters = \
	ControlsEvolutionParameters(
		selected_controls_number     = 10,
		reproduced_controls_number   = 5,
		control_mutation_probability = 0.1
	)
	
	
	
	
	
optimizer_0_iterations_numbers = 300
optimizer_0                    = \
	MovementControlsOptimizer(
		navigation                    = ShipNavigation(),
		controls_evolution_parameters = controls_evolution_parameters,
		control_tests_number          = 3,
		generate_target               = generate_random_target,
		finishing_time                = 2.0
	)
	
	
optimizer_1_iterations_numbers = 150
optimizer_1                    = \
	MovementControlsOptimizer(
		navigation                    = ShipNavigation(),
		controls_evolution_parameters = controls_evolution_parameters,
		control_tests_number          = 3,
		generate_target               = generate_random_target,
		finishing_time                = 10.0
	)
	
	
optimizer_2_iterations_numbers = 75
optimizer_2                    = \
	MovementControlsOptimizer(
		navigation                    = ShipNavigation(),
		controls_evolution_parameters = controls_evolution_parameters,
		control_tests_number          = 3,
		generate_target               = generate_random_target,
		finishing_time                = 50.0
	)
	
	
optimizer_3_iterations_numbers = 38
optimizer_3                    = \
	TimeControlsOptimizer(
		navigation                         = ShipNavigation(),
		controls_evolution_parameters      = controls_evolution_parameters,
		control_tests_number               = 3,
		generate_target                    = generate_random_target,
		finishing_confirmed_targets_number = 3,
		interrupting_time                  = 250.0
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
			