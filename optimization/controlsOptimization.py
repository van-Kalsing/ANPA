from abc \
	import ABCMeta, \
				abstractmethod, \
				abstractproperty
				
from optimization.controls.constructing \
	import ControlsConstructingParameters, \
				cast_control
				
from optimization.controlsEvolution \
	import ControlsPopulation, \
				ControlsComplexPopulation, \
				ControlsComplexPopulationRating, \
				ControlsEvolutionParameters, \
				evolve_complex_controls_population
				
from optimization.tests \
	import TimeComplexControlTest, \
				FixedTimeMovementComplexControlTest, \
				FreeTimeMovementComplexControlTest
				
from optimization.controls.arguments     import ArgumentsSpace
from optimization.controls.controls      import ComplexControl
from optimization.evolution.criterions   import Minimization, Maximization
from optimization.machine                import StateSpace, MetricStateSpace
from optimization.navigation             import Navigation
from random                              import randint





#!!!!! Временно
from ship import ShipLeftEngineForce,ShipRightEngineForce,ShipTopEngineForce
test_number = 0





#!!!!! Не проверяется controls_constructing_parameters
class ControlsOptimizer(metaclass = ABCMeta):
	@staticmethod
	def check_controls_optimizers_compatibility(first_controls_optimizer,
													second_controls_optimizer):
		are_controls_optimizers_compatible = True
		
		
		# Размеры популяций должны быть равными
		first_population_size, second_population_size = \
			first_controls_optimizer.__controls_evolution_parameters.population_size, \
				second_controls_optimizer.__controls_evolution_parameters.population_size
				
		are_controls_optimizers_compatible &= \
			first_population_size == second_population_size
			
			
		# Состав функций управления
		first_state_space, second_state_space = \
			first_controls_optimizer.__complex_controls_state_space, \
				second_controls_optimizer.__complex_controls_state_space
				
		are_controls_optimizers_compatible &= \
			first_state_space == second_state_space
			
			
		# Состав аргументов функций управления
		first_arguments_space, second_arguments_space = \
			first_controls_optimizer.__complex_controls_arguments_space, \
				second_controls_optimizer.__complex_controls_arguments_space
				
		are_controls_optimizers_compatible &= \
			first_arguments_space <= second_arguments_space
			
			
		return are_controls_optimizers_compatible
		
		
		
	def __init__(self,
					navigations,
					controls_evolution_parameters,
					controls_constructing_parameters,
					control_tests_number):
		super(ControlsOptimizer, self).__init__()
		
		
		if control_tests_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if (navigations) == 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		first_navigation = navigations[0]
		
		self.__complex_controls_state_space = \
			first_navigation.complex_controls_state_space
			
		self.__complex_controls_arguments_space = \
			first_navigation.complex_controls_arguments_space
			
		self.__targets_state_space = \
			first_navigation.targets_state_space
			
		self.__confirming_distance = \
			first_navigation.confirming_distance
			
			
			
		are_navigations_compatible = True
		
		for navigation in navigations:
			are_navigations_compatible &= \
				self.__complex_controls_state_space \
					== navigation.complex_controls_state_space
					
			are_navigations_compatible &= \
				self.__complex_controls_arguments_space \
					== navigation.complex_controls_arguments_space
					
			are_navigations_compatible &= \
				self.__targets_state_space \
					== navigation.targets_state_space
					
			are_navigations_compatible &= \
				self.__confirming_distance \
					== navigation.confirming_distance
					
					
			if not are_navigations_compatible:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
				
		self.__navigations                      = list(navigations)
		self.__controls_evolution_parameters    = controls_evolution_parameters
		self.__controls_constructing_parameters = controls_constructing_parameters #!!!!!
		self.__control_tests_number             = control_tests_number
		
		
		
		controls_populations = dict()
		
		state_space_coordinates = \
			self.__complex_controls_state_space \
				.state_space_coordinates
				
		for state_space_coordinate in state_space_coordinates:
			controls_population = \
				ControlsPopulation(
					self.__complex_controls_arguments_space,
					[]
				)
				
			controls_populations[state_space_coordinate] = controls_population
			
			
		self.__buffer_controls_complex_population = \
			ControlsComplexPopulation(
				controls_populations
			)
			
		self.__controls_complex_population = \
			ControlsComplexPopulation(
				controls_populations
			)
			
			
			
		self.__controls_complex_population_rating = None
		self.__complex_control_tests              = set()
		self.__vacant_navigations                 = set(self.__navigations)
		self.__vacant_controls                    = None
		self.__has_vacant_controls                = None
		
		
		
	@abstractmethod
	def _create_complex_control_test(self, navigation, test_complex_control):
		pass
		
		
		
	@property
	def navigations(self):
		return self.__navigations
		
		
	@property
	def controls_evolution_parameters(self):
		return self.__controls_evolution_parameters
		
		
	@property
	def controls_constructing_parameters(self):
		return self.__controls_constructing_parameters
		
		
	@property
	def control_tests_number(self):
		return self.__control_tests_number
		
		
	@abstractproperty
	def improvement_direction(self):
		pass
		
		
		
	@property
	def buffer_controls_complex_population(self):
		return self.__buffer_controls_complex_population
		
		
	@buffer_controls_complex_population.setter
	def buffer_controls_complex_population(self, controls_complex_population):
		is_controls_complex_population_compatible = True
		
		
		is_controls_complex_population_compatible &= \
			controls_complex_population.state_space \
				== self.__complex_controls_state_space
				
		is_controls_complex_population_compatible &= \
			controls_complex_population.controls_arguments_space \
				== self.__complex_controls_arguments_space
				
				
		if is_controls_complex_population_compatible:
			self.__buffer_controls_complex_population = \
				controls_complex_population
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
	@property
	def controls_complex_population(self):
		return self.__controls_complex_population
		
		
		
	@property
	def is_iteration_active(self):
		return self.__controls_complex_population_rating is not None
		
		
	def start_iteration(self):
		if self.is_iteration_active:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		if self.__check_controls_complex_population_completeness():
			is_controls_complex_population_completeness = True
		else:
			self.__replenish_controls_complex_population()
			
			is_controls_complex_population_completeness = \
				self.__check_controls_complex_population_completeness()
				
				
				
		if is_controls_complex_population_completeness:
			state_space_coordinates = \
				self.__complex_controls_state_space \
					.state_space_coordinates
					
					
			self.__controls_complex_population_rating = \
				ControlsComplexPopulationRating(
					self.__controls_complex_population
				)
				
			self.__vacant_controls      = dict()
			self.__has_vacant_controls  = True
			
			
			for state_space_coordinate in state_space_coordinates:
				controls_population = \
					self.__controls_complex_population \
						.get_controls_population(
							state_space_coordinate
						)
						
				self.__vacant_controls[state_space_coordinate] = \
					controls_population.controls \
						* self.__control_tests_number
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
	def iterate(self, delta_time):
		if not self.is_iteration_active:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		for navigation in set(self.__vacant_navigations):
			if self.__has_vacant_controls:
				test_controls = dict()
				
				
				vacant_controls         = self.__vacant_controls
				state_space_coordinates = \
					self.__complex_controls_state_space \
						.state_space_coordinates
						
				for state_space_coordinate in state_space_coordinates:
					controls       = vacant_controls[state_space_coordinate]
					control_number = randint(0, len(controls) - 1)
					
					test_controls[state_space_coordinate] = \
						controls.pop(
							control_number
						)
						
					if len(controls) == 0:
						self.__has_vacant_controls = False
						
						
				test_complex_control = ComplexControl(test_controls)
				
				complex_control_test = \
					self._create_complex_control_test(
						navigation,
						test_complex_control
					)
					
				self.__complex_control_tests.add(complex_control_test)
				self.__vacant_navigations.remove(navigation)
			else:
				break
				
				
				
		for complex_control_test in set(self.__complex_control_tests):
			if complex_control_test.is_initialized:
				complex_control_test.iterate(delta_time)
			else:
				complex_control_test.initialize()
				
				
			if complex_control_test.is_finished:
				self.__controls_complex_population_rating \
					.rate_complex_control(
						complex_control_test.complex_control,
						complex_control_test.result
					)
					
					
				self.__vacant_navigations.add(
					complex_control_test.navigation
				)
				
				self.__complex_control_tests.remove(
					complex_control_test
				)
				#!!!!! <Временно>
				# global test_number
				# test_number += 1
				# if complex_control_test.result is not None:
				# 	print("\n\n\n-------------------------------------------")
				# 	print("Номер испытания: %s\n" % str(test_number))
				# 	print("Левый двигатель:")
				# 	print(complex_control_test.complex_control[ShipLeftEngineForce()])
				# 	print("\nПравый двигатель:")
				# 	print(complex_control_test.complex_control[ShipRightEngineForce()])
				# 	print("\nДвигатель вертикальной тяги:")
				# 	print(complex_control_test.complex_control[ShipTopEngineForce()])
				# 	print(
				# 		"\nРезультат испытания: %s" \
				# 			% str(complex_control_test.result)
				# 	)
				#!!!!! </Временно>
				
				
				
		if not bool(self.__complex_control_tests):
			if not self.__has_vacant_controls:
				self.__controls_complex_population = \
					evolve_complex_controls_population(
						self.__controls_complex_population_rating,
						self.improvement_direction,
						self.__controls_evolution_parameters,
						self.__controls_constructing_parameters
					)
					
				self.__controls_complex_population_rating = None
				self.__vacant_controls                    = None
				
				
				
	def __check_controls_complex_population_completeness(self):
		is_controls_complex_population_full = True
		
		
		needed_controls_population_size = \
			self.__controls_evolution_parameters.population_size
			
		state_space_coordinates = \
			self.__complex_controls_state_space \
				.state_space_coordinates
				
		for state_space_coordinate in state_space_coordinates:
			controls_population = \
				self.__controls_complex_population.get_controls_population(
					state_space_coordinate
				)
				
			if controls_population.count != needed_controls_population_size:
				is_controls_complex_population_full = False
				break
				
				
		return is_controls_complex_population_full
		
		
	def __replenish_controls_complex_population(self):
		buffer_controls_populations = dict()
		controls_populations        = dict()
		
		
		needed_controls_population_size = \
			self.__controls_evolution_parameters.population_size
			
		arguments_space = \
			self.__complex_controls_arguments_space
			
		state_space_coordinates = \
			self.__complex_controls_state_space \
				.state_space_coordinates
				
				
		for state_space_coordinate in state_space_coordinates:
			buffer_controls_population = \
				self.__buffer_controls_complex_population \
					.get_controls_population(
						state_space_coordinate
					)
					
			controls_population = \
				self.__controls_complex_population \
					.get_controls_population(
						state_space_coordinate
					)
					
			buffer_controls = buffer_controls_population.controls
			controls        = controls_population.controls
			
			
			while len(controls) != needed_controls_population_size:
				if len(buffer_controls) != 0:
					controls.append(
						buffer_controls.pop()
					)
				else:
					break
					
					
			buffer_controls_populations[state_space_coordinate] = \
				ControlsPopulation(arguments_space, buffer_controls)
				
			controls_populations[state_space_coordinate] = \
				ControlsPopulation(arguments_space, controls)
				
				
		self.__buffer_controls_complex_population = \
			ControlsComplexPopulation(
				buffer_controls_populations
			)
			
		self.__controls_complex_population = \
			ControlsComplexPopulation(
				controls_populations
			)
			
			
			
class FixedTimeMovementControlsOptimizer(ControlsOptimizer):
	def __init__(self, 
					navigation,
					controls_evolution_parameters,
					controls_constructing_parameters,
					control_tests_number,
					finishing_time):
		try:
			super(FixedTimeMovementControlsOptimizer, self).__init__(
				navigation,
				controls_evolution_parameters,
				controls_constructing_parameters,
				control_tests_number
			)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			self.__finishing_time = finishing_time
			
			
			
	@property
	def finishing_time(self):
		return self.__finishing_time
		
		
	@property
	def improvement_direction(self):
		return Maximization()
		
		
	def _create_complex_control_test(self, navigation, test_complex_control):
		complex_control_tester = \
			FixedTimeMovementComplexControlTest(
				navigation,
				test_complex_control,
				self.__finishing_time
			)
			
		return complex_control_tester
		
		
		
class FreeTimeMovementControlsOptimizer(ControlsOptimizer):
	def __init__(self, 
					navigation,
					controls_evolution_parameters,
					controls_constructing_parameters,
					control_tests_number,
					finishing_absolute_movement,
					interrupting_time):
		# super(FreeTimeMovementControlsOptimizer, self).__init__(
		# 	navigation,
		# 	controls_evolution_parameters,
		# 	controls_constructing_parameters,
		# 	control_tests_number
		# )
		# self.__finishing_absolute_movement = finishing_absolute_movement
		# self.__interrupting_time           = interrupting_time
		try:
			super(FreeTimeMovementControlsOptimizer, self).__init__(
				navigation,
				controls_evolution_parameters,
				controls_constructing_parameters,
				control_tests_number
			)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			self.__finishing_absolute_movement = finishing_absolute_movement
			self.__interrupting_time           = interrupting_time
			
			
			
	@property
	def finishing_absolute_movement(self):
		return self.__finishing_absolute_movement
		
		
	@property
	def interrupting_time(self):
		return self.__interrupting_time
		
		
	@property
	def improvement_direction(self):
		return Maximization()
		
		
	def _create_complex_control_test(self, navigation, test_complex_control):
		complex_control_tester = \
			FreeTimeMovementComplexControlTest(
				navigation,
				test_complex_control,
				self.__finishing_absolute_movement,
				self.__interrupting_time
			)
			
		return complex_control_tester
		
		
		
class TimeControlsOptimizer(ControlsOptimizer):
	def __init__(self, 
					navigation,
					controls_evolution_parameters,
					controls_constructing_parameters,
					control_tests_number,
					finishing_confirmed_targets_number,
					interrupting_time):
		try:
			super(TimeControlsOptimizer, self).__init__(
				navigation,
				controls_evolution_parameters,
				controls_constructing_parameters,
				control_tests_number
			)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			self.__finishing_confirmed_targets_number = finishing_confirmed_targets_number
			self.__interrupting_time                  = interrupting_time
			
			
			
	@property
	def finishing_confirmed_targets_number(self):
		return self.__finishing_confirmed_targets_number
		
		
	@property
	def interrupting_time(self):
		return self.__interrupting_time
		
		
	@property
	def improvement_direction(self):
		return Minimization()
		
		
	def _create_complex_control_test(self, navigation, test_complex_control):
		complex_control_tester = \
			TimeComplexControlTest(
				navigation,
				test_complex_control,
				self.__finishing_confirmed_targets_number,
				self.__interrupting_time
			)
			
		return complex_control_tester
		
		
		
		
		
class ControlsOptimizersConveyor:
	def __init__(self,
					controls_optimizers,
					controls_optimizers_iterations_numbers):
		super(ControlsOptimizersConveyor, self).__init__()
		
		
		
		self.__controls_optimizers                    = list(controls_optimizers)
		self.__controls_optimizers_iterations_numbers = \
			dict(
				controls_optimizers_iterations_numbers
			)
			
			
		if not self.__controls_optimizers:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		last_controls_optimizer = None
		
		for controls_optimizer in self.__controls_optimizers:
			# Проверка совместимости оптимизаторов функций управления
			if last_controls_optimizer is not None:
				are_controls_optimizers_compatible = \
					ControlsOptimizer.check_controls_optimizers_compatibility(
						last_controls_optimizer,
						controls_optimizer
					)
					
				if not are_controls_optimizers_compatible:
					raise Exception() #!!!!! Создавать внятные исключения
					
					
			# Проверка числа итераций в серии для каждого оптимизатора
			controls_optimizer_iterations_number = \
				self.__controls_optimizers_iterations_numbers[
					controls_optimizer
				]
				
			if controls_optimizer_iterations_number <= 0:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
			last_controls_optimizer = controls_optimizer
			
			
			
		self.__iterations_numbers = []
		
		controls_optimizers_number = len(self.__controls_optimizers)
		
		for index in range(controls_optimizers_number):
			controls_optimizer = self.__controls_optimizers[index]
			iterations_number  = self.__controls_optimizers_iterations_numbers[controls_optimizer]
			
			self.__iterations_numbers.append(iterations_number)
			
			
		self.__controls_optimizer_iteration_number = None
		self.__iterable_controls_optimizer_number  = None
		
		
		
	#!!!!!
	@property
	def controls_optimizers(self):
		return self.__controls_optimizers
		
		
		
	@property
	def buffer_controls_complex_population(self):
		first_controls_optimizer = self.__controls_optimizers[0]
		
		return first_controls_optimizer.buffer_controls_complex_population
		
		
	@buffer_controls_complex_population.setter
	def buffer_controls_complex_population(self, controls_complex_population):
		first_controls_optimizer = self.__controls_optimizers[0]
		
		try:
			first_controls_optimizer.buffer_controls_complex_population = \
				controls_complex_population
		except:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
	@property
	def controls_complex_population(self):
		last_controls_optimizer = self.__controls_optimizers[-1]
		
		return last_controls_optimizer.controls_complex_population
		
		
		
	@property
	def is_iteration_active(self):
		return self.__iterable_controls_optimizer_number is not None
		
		
	def start_iteration(self):
		if self.is_iteration_active:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			self.__controls_optimizer_iteration_number = 0
			self.__iterable_controls_optimizer_number  = \
				len(self.__controls_optimizers) \
					- 1
					
					
	def iterate(self, delta_time):
		if self.is_iteration_active:
			controls_optimizer = None
			
			
			while controls_optimizer is None:
				controls_optimizer = \
					self.__controls_optimizers[
						self.__iterable_controls_optimizer_number
					]
					
				if controls_optimizer.is_iteration_active:
					controls_optimizer.iterate(delta_time)
				else:
					try:
						controls_optimizer.start_iteration()
					except:
						if self.__iterable_controls_optimizer_number != 0:
							self.__controls_optimizer_iteration_number  = 0
							self.__iterable_controls_optimizer_number  -= 1
						else:
							raise Exception() #!!!!! Создавать внятные исключения
							
					controls_optimizer = None
					
					
			if controls_optimizer.is_iteration_active:
				are_finished_controls_optimizer_iterations = False
			else:
				self.__controls_optimizer_iteration_number += 1
				
				are_finished_controls_optimizer_iterations = \
					self.__controls_optimizers_iterations_numbers[controls_optimizer] \
						== self.__controls_optimizer_iteration_number
						
						
			if are_finished_controls_optimizer_iterations:
				is_last_controls_optimizer = \
					self.__iterable_controls_optimizer_number \
						== len(self.__controls_optimizers) - 1
						
				if not is_last_controls_optimizer:
					next_controls_optimizer = \
						self.__controls_optimizers[
							self.__iterable_controls_optimizer_number \
								+ 1
						]
						
					controls_populations = dict()
					
					
					
					controls_complex_population = \
						controls_optimizer.controls_complex_population
						
					arguments_space = \
						next_controls_optimizer.controls_complex_population \
							.controls_arguments_space
							
					state_space_coordinates = \
						controls_complex_population.state_space \
							.state_space_coordinates
							
					for state_space_coordinate in state_space_coordinates:
						controls_population = \
							controls_complex_population \
								.get_controls_population(
									state_space_coordinate
								)
								
						controls = \
							[cast_control(control, arguments_space) for control
								in controls_population.controls]
								
						controls_populations[state_space_coordinate] = \
							ControlsPopulation(
								arguments_space,
								controls
							)
							
							
							
					next_controls_optimizer.buffer_controls_complex_population = \
						ControlsComplexPopulation(
							controls_populations
						)
						
						
						
					self.__controls_optimizer_iteration_number  = 0
					self.__iterable_controls_optimizer_number  += 1
				else:
					self.__controls_optimizer_iteration_number = None
					self.__iterable_controls_optimizer_number  = None
					
					
					
			# Сохранение состояния в базу данных
			if not controls_optimizer.is_iteration_active:
				self.save()
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			