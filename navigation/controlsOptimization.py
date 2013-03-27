import random





#!!!!! 1. Типы функций управления предыдущих оптимизаторов должны приводиться
#!!!!! 		к типам функций управления последующих. Для этого:
#!!!!! 			- ввести проверки принимаемых функций (для буфферов функций)
#!!!!! 			- ввести проверки совместимости оптимизаторов по типам функций
#!!!!! 		Совместимость проявляется по составу комплексной функции управления и
#!!!!! 		аргументам принимаемым функцией управления (возможно приведение, если
#!!!!! 		целевой тип имеет более широкий набор аргументов)
#!!!!! 2. Генерацию случайных целей перенести в навигацию,
#!!!!! 		либо передавать оттуда функцию генерации целей





#!!!!! Временно
targets_x_limits = 25, 30
targets_y_limits = 25, 30
targets_z_limits = -6, -5





# Источники целей
class RandomTargetsSource(TargetsSource):
	def _load_targets(self, targets_number):
		targets = []
		
		while len(targets) < targets_number:
			targets.append(
				Vector([
					random.uniform(*targets_x_limits),
					random.uniform(*targets_y_limits),
					random.uniform(*targets_z_limits)
				])
			)
			
		return targets
		
		
		
class RevolvingRandomTargetsSource(TargetsSource):
	def __init__(self):
		self.__base_targets_source = RandomTargetsSource()
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
			
			
		#!!!!! Проверка совместимости состава функций управления
		#!!!!! Проверка совместимости функций управления
		
		
		return are_controls_optimizers_compatible
		
		
		
	def __init__(self,
					navigation,
					controls_evolution_parameters,
					control_tests_number):
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
		
		
		controls_populations = \
			dict(
				[(control_name, Control()) for control_name
					in self._controls_names]
			)
			
		self.__buffer_controls_complex_population = \
			ControlsComplexPopulation(**controls_populations)
			
		self.__controls_complex_population = \
			ControlsComplexPopulation(**controls_populations)
			
			
			
	@abstractmethod
	def _create_test(self):
		pass
		
		
		
	@property
	def buffer_controls_complex_population(self):
		return self.__buffer_controls_complex_population
		
		
	@buffer_controls_complex_population.setter
	def buffer_controls_complex_population(self, controls_complex_population):
		#!!!!! Проверка совместимости controls_complex_population
		
		
		self.__buffer_controls_complex_population = controls_complex_population
		
		
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
					
				self.__targets_source = RevolvingRandomTargetsSource()
			else:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
	def iterate(self, delta_time):
		if self.is_iteration_active:
			if self.__test_complex_control is None:
				self.__test_complex_control = \
					random.choice(
						self.__controls_complex_population_rating
							.get_unrated_controls_complex_population()
					)
				self.__test = self._create_test()
				
				self.__targets_source.reset()
				self.__navigation.machine.reset_state()
				
				
				
			target     = self.__targets_source.current_target
			ship_state = self.__navigation.machine.current_state
			
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
					self.__controls_complex_population_rating
						.set_complex_control_test_result(
							self.__test_complex_control,
							None
						)
						
					is_test_finished = True
				else:
					is_test_finished = False
			else:
				self.__controls_complex_population_rating
					.set_complex_control_test_result(
						self.__test_complex_control,
						self.__test.result
					)
					
				is_test_finished = True
				
				
				
			if is_test_finished:
				has_unrated_controls = \
					self.__controls_complex_population_rating
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
			self.__controls_evolution_parameters.get_population_size()
			
		for control_name in self._controls_names:
			controls_population = \
				self.__controls_complex_population.get_controls_population(
					control_name
				)
				
			if len(controls_population) != needed_controls_population_size:
				is_controls_complex_population_full = False
				break
				
				
		return is_controls_complex_population_full
		
		
	def __replenish_controls_complex_population(self):
		buffer_controls_populations = dict()
		controls_populations        = dict()
		
		
		needed_controls_population_size = \
			self.__controls_evolution_parameters.get_population_size()
			
		for control_name in self._controls_names:
			buffer_controls_population = \
				self.__buffer_controls_complex_population.get_controls_population(
					control_name
				)
			buffer_controls = list(buffer_controls_population)
			
			controls_population = \
				self.__controls_complex_population.get_controls_population(
					control_name
				)
			controls = list(controls_population)
			
			
			while len(controls) < needed_controls_population_size:
				if len(buffer_controls) > 0:
					controls.append(
						buffer_controls.pop()
					)
				else:
					break
					
					
			buffer_controls_populations[control_name] = \
				ControlsPopulation(buffer_controls)
				
			controls_populations[control_name] = \
				ControlsPopulation(controls)
				
				
		self.__buffer_controls_complex_population = \
			ControlsComplexPopulation(**buffer_controls_populations)
			
		self.__controls_complex_population = \
			ControlsComplexPopulation(**controls_populations)
			
			
			
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
			