from targets import TargetsSource

import random





#!!!!! 1. Типы функций управления предыдущих оптимизаторов должны приводиться
#!!!!! 		к типам функций управления последующих.
#!!!!! 		(приведение возможно, если целевой тип имеет
#!!!!! 		более широкий набор аргументов)
#!!!!! 2. Как-то избавиться от функции генерации целей, передаваемой из вне,
#!!!!! 		т.к. она может возвращать несовместимые цели -
#!!!!! 		проверять которые не удобно (сейчас такой проверки нет,
#!!!!! 		поэтому если в тесте или навигации вылетит исключение,
#!!!!! 		то оно пойдет наверх!)





# Источники целей
class WrappedTargetsSource(TargetsSource):
	def __init__(self, generate_target):
		self.__generate_target = generate_target
		
		
	def _load_targets(self, targets_number):
		targets = []
		
		while len(targets) < targets_number:
			targets.append(
				self.__generate_target()
			)
			
		return targets
		
		
		
class RevolvingWrappedTargetsSource(TargetsSource):
	def __init__(self, generate_target):
		self.__base_targets_source = WrappedTargetsSource(generate_target)
		self.__base_target_offset  = 0
		
		
	def reset(self):
		self.__target_offset = 0
		
		
	def _load_targets(self, targets_number):
		targets = []
		
		
		targets_offsets = \
			xrange(
				self.__base_target_offset,
				self.__base_target_offset + targets_number
			)
			
		for target_offset in targets_offsets:
			targets.append(
				self.__base_targets_source.get_target(target_offset)
			)
			
		self.__base_target_offset += targets_number
		
		
		return targets
		
		
		
		
		
class ControlsOptimizer(object):
	__metaclass__ = ABCMeta
	
	
	
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
			
			
		# Управляемый аппарат должен быть один
		first_machine, second_machine = \
			first_controls_optimizer.__navigation.machine,
				second_controls_optimizer.__navigation.machine
				
		are_controls_optimizers_compatible &= \
			first_machine is second_machine
			
			
		# Состав функций управления
		first_state_space, second_state_space = \
			first_controls_optimizer.__navigation.complex_controls_state_space,
				second_controls_optimizer.__navigation.complex_controls_state_space
				
		are_controls_optimizers_compatible &= \
			first_state_space == second_state_space
			
			
		# Состав аргументов функций управления
		first_arguments_space, second_arguments_space = \
			first_controls_optimizer.__navigation.complex_controls_arguments_space,
				second_controls_optimizer.__navigation.complex_controls_arguments_space
				
		are_controls_optimizers_compatible &= \
			first_arguments_space == second_arguments_space
			
			
		return are_controls_optimizers_compatible
		
		
		
	def __init__(self,
					navigation,
					controls_evolution_parameters,
					control_tests_number,
					generate_target):
		if control_tests_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self.__navigation                    = navigation
		self.__controls_evolution_parameters = controls_evolution_parameters
		self.__control_tests_number          = control_tests_number
		
		
		self.__buffer_controls_complex_population = None
		self.__controls_complex_population        = None
		
		self.__controls_complex_population_rating = None
		self.__targets_source                     = None
		
		self.__test_complex_control               = None
		self.__test                               = None
		
		
		controls_populations = dict()
		
		for state_space_coordinate in navigation.complex_controls_state_space:
			controls_population = \
				ControlsPopulation(
					navigation.complex_controls_arguments_space,
					[]
				)
				
			controls_populations[state_space_coordinate] = controls_population
			
		self.__buffer_controls_complex_population = \
			ControlsComplexPopulation(
				navigation.complex_controls_arguments_space,
				controls_populations
			)
			
		self.__controls_complex_population = \
			ControlsComplexPopulation(
				navigation.complex_controls_arguments_space,
				controls_populations
			)
			
			
			
	@abstractmethod
	def _create_test(self):
		pass
		
		
		
	@property
	def navigation(self):
		return self.__navigation
		
		
	@property
	def controls_evolution_parameters(self):
		return self.__controls_evolution_parameters
		
		
	@property
	def control_tests_number(self):
		return self.__control_tests_number
		
		
	@property
	def buffer_controls_complex_population(self):
		return self.__buffer_controls_complex_population
		
		
	@buffer_controls_complex_population.setter
	def buffer_controls_complex_population(self, controls_complex_population):
		is_controls_complex_population_compatible = True
		
		
		is_controls_complex_population_compatible &= \
			controls_complex_population.state_space \
				== self.__navigation.complex_controls_state_space
				
		is_controls_complex_population_compatible &= \
			controls_complex_population.controls_arguments_space \
				== self.__navigation.complex_controls_arguments_space
				
				
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
		else:
			if self.__check_controls_complex_population_completeness():
				is_controls_complex_population_completeness = True
			else:
				self.__replenish_controls_complex_population()
				
				is_controls_complex_population_completeness = \
					self.__check_controls_complex_population_completeness()
					
					
			if is_controls_complex_population_completeness:
				self.__controls_complex_population_rating = \
					ControlsComplexPopulationRating(
						self.__controls_complex_population,
						self.__control_tests_number
					)
					
				self.__targets_source = \
					RevolvingWrappedTargetsSource(
						generate_target
					)
			else:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
	def iterate(self, delta_time):
		if self.is_iteration_active:
			if self.__test_complex_control is None:
				self.__test_complex_control = \
					random.choice(
						self.__controls_complex_population_rating \
							.get_unrated_controls_complex_population()
					)
				self.__test = self._create_test()
				
				self.__targets_source.reset()
				self.__navigation.machine.reset_state()
				
				
				
			target     = self.__targets_source.current_target
			ship_state = \
				self.__navigation.machine.get_current_state(
					self.__navigation.complex_controls_state_space
				)
				
			while True:
				if self.__test.is_initialized:
					self.__test.measure(ship_state, target, delta_time)
				else:
					self.__test.initialize(ship_state, target)
					
					
				if target and not self.__test.is_finished:
					is_target_confirmed = \
						self.__navigation.check_target_confirmation(
							target
						)
						
					if is_target_confirmed:
						self.__targets_source.confirm_current_target()
						
						target     = self.__targets_source.current_target
						delta_time = 0
					else:
						break
				else:
					break
					
					
					
			if not self.__test.is_finished:
				targets_source_view = \
					TargetsSourceView(
						self.__targets_source,
						self.__navigation.targets_accounting_depth
					)
					
				try:
					self.__navigation.navigate(
						self.__test_complex_control,
						targets_source_view
					)
				except:
					self.__controls_complex_population_rating \
						.set_complex_control_test_result(
							self.__test_complex_control,
							None
						)
						
					is_test_finished = True
				else:
					is_test_finished = False
			else:
				self.__controls_complex_population_rating \
					.set_complex_control_test_result(
						self.__test_complex_control,
						self.__test.result
					)
					
				is_test_finished = True
				
				
				
			if is_test_finished:
				has_unrated_controls = \
					self.__controls_complex_population_rating \
						.has_unrated_controls()
						
				if not has_unrated_controls:
					self.__controls_complex_population = \
						evolve_complex_controls_population(
							self.__controls_complex_population_rating,
							self.__controls_evolution_parameters
						)
						
					self.__controls_complex_population_rating = None
					self.__targets_source                     = None
					
					
				self.__test                 = None
				self.__test_complex_control = None
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
	def __check_controls_complex_population_completeness(self):
		is_controls_complex_population_full = True
		
		
		needed_controls_population_size = \
			self.__controls_evolution_parameters.population_size
			
		state_space_coordinates = \
			self.__navigation.complex_controls_state_space \
				.state_space_coordinates
				
		for state_space_coordinate in state_space_coordinates:
			controls_population = \
				self.__controls_complex_population.get_controls_population(
					state_space_coordinate
				)
				
			if len(controls_population) != needed_controls_population_size:
				is_controls_complex_population_full = False
				break
				
				
		return is_controls_complex_population_full
		
		
	def __replenish_controls_complex_population(self):
		buffer_controls_populations = dict()
		controls_populations        = dict()
		
		
		needed_controls_population_size = \
			self.__controls_evolution_parameters.population_size
			
		arguments_space = \
			self.__navigation.complex_controls_arguments_space
			
		state_space_coordinates = \
			self.__navigation.complex_controls_state_space \
				.state_space_coordinates
				
				
		for state_space_coordinate in state_space_coordinates:
			buffer_controls_population = \
				self.__buffer_controls_complex_population.get_controls_population(
					state_space_coordinate
				)
			buffer_controls = list(buffer_controls_population)
			
			controls_population = \
				self.__controls_complex_population.get_controls_population(
					state_space_coordinate
				)
			controls = list(controls_population)
			
			
			while len(controls) < needed_controls_population_size:
				if len(buffer_controls) > 0:
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
				arguments_space,
				buffer_controls_populations
			)
			
		self.__controls_complex_population = \
			ControlsComplexPopulation(
				arguments_space,
				controls_populations
			)
			
			
			
class MovementControlsOptimizer(ControlsOptimizer):
	def __init__(self, 
					navigation,
					controls_evolution_parameters,
					control_tests_number,
					finishing_time):
		try:
			super(MovementControlsOptimizer, self).__init__(
				self,
				navigation,
				controls_evolution_parameters,
				control_tests_number,
			)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
			
		self.__finishing_time = finishing_time
		
		
	@property
	def finishing_time(self):
		return self.__finishing_time
		
		
	def _create_test(self):
		return MovementTest(self.__finishing_time)
		
		
		
class TimeControlsOptimizer(ControlsOptimizer):
	def __init__(self, 
					navigation,
					controls_evolution_parameters,
					control_tests_number,
					finishing_confirmed_targets_number,
					interrupting_time):
		try:
			super(TimeControlsOptimizer, self).__init__(
				self,
				navigation,
				controls_evolution_parameters,
				control_tests_number,
			)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
			
		self.__finishing_confirmed_targets_number = finishing_confirmed_targets_number
		self.__interrupting_time                  = interrupting_time
		
		
	@property
	def finishing_confirmed_targets_number(self):
		return self.__finishing_confirmed_targets_number
		
		
	@property
	def interrupting_time(self):
		return self.__interrupting_time
		
		
	def _create_test(self):
		test = \
			TimeTest(
				self.__finishing_confirmed_targets_number,
				self.__interrupting_time
			)
			
		return test
		
		
		
		
		
class ControlsOptimizersConveyor(object):
	def __init__(self, controls_optimizers, controls_optimizers_iterations_numbers):
		self.__controls_optimizers                    = list(controls_optimizers)
		self.__controls_optimizers_iterations_numbers = \
			dict(
				controls_optimizers_iterations_numbers
			)
			
		self.__controls_optimizer_iteration_number = None
		self.__iterable_controls_optimizer_number  = None
		
		
		if self.__controls_optimizers:
			last_controls_optimizer = None
			
			for controls_optimizer in self.__controls_optimizers:
				# Проверка совместимости оптимизаторов функций управления
				if last_controls_optimizer is None:
					last_controls_optimizer = controls_optimizer
				else:
					are_controls_optimizers_compatible = \
						check_controls_optimizers_compatibility(
							last_controls_optimizer,
							controls_optimizer
						)
						
					if not are_controls_optimizers_compatible:
						raise Exception() #!!!!! Создавать внятные исключения
						
						
				# Проверка числа итераций в серии для каждого оптимизатора
				controls_optimizer_iterations_number = \
					self.__controls_optimizers_iterations_number[
						controls_optimizer
					]
					
				if controls_optimizer_iterations_number <= 0:
					raise Exception() #!!!!! Создавать внятные исключения
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
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
				
				are_finished_controls_optimizer_iterations =
					self.__controls_optimizers_iterations_numbers[controls_optimizer] \
						== self.__controls_optimizer_iteration_number
						
						
			if are_finished_controls_optimizer_iterations:
				is_last_controls_optimizer = \
					self.__iterable_controls_optimizer_number \
						== len(self.__controls_optimizers) - 1
						
				if not is_last_controls_optimizer:
					next_controls_optimizer = \
						self.__controls_optimizers[
							self.__iterable_controls_optimizer_number + 1
						]
						
					next_controls_optimizer.buffer_controls_complex_population = \
						controls_optimizer.controls_complex_population
						
						
					self.__controls_optimizer_iteration_number  = 0
					self.__iterable_controls_optimizer_number  += 1
				else:
					self.__controls_optimizer_iteration_number = None
					self.__iterable_controls_optimizer_number  = None
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			