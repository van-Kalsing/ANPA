from collections           import Iterable
from optimization.machine  import CustomStateSpace
from optimization.controls import ComplexControl

import optimization
import random





#!!!!! 1. В рейтинге комплексной популяции убрать доступ к рейтингам
#!!!!! 		отдельных популяций напрямую, т.к. они изменяемые.
#!!!!! 		Реализовать клонирование рейтингов и возвращать копии





class ControlsPopulation(Iterable):
	def __init__(self, controls_arguments_space, controls):
		for control in controls:
			if controls_arguments_space != control.arguments_space:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
		self.__controls_arguments_space = controls_arguments_space
		self.__controls                 = frozenset(controls)
		
		
		
	@property
	def controls_arguments_space(self):
		return self.__controls_arguments_space
		
		
		
	def __contains__(self, control):
		return control in self.__controls
		
		
	def __iter__(self):
		return iter(self.__controls)
		
		
	def __len__(self):
		return len(self.__controls)
		
		
		
	def __getitem__(self, index):
		if index < len(self.__controls):
			current_index  = 0
			result_control = None
			
			for control in self.__controls:
				if current_index == index:
					result_control = control
					break
				else:
					current_index += 1
		else:
			raise IndexError() #!!!!! Создавать внятные исключения
			
		return result_control
		
		
		
class ControlsComplexPopulation(object):
	def __init__(self, controls_arguments_space, controls_populations):
		try:
			state_space = \
				CustomStateSpace(
					controls_populations.keys()
				)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			for controls_population in controls_populations.values():
				is_controls_population_compatible = \
					controls_population.controls_arguments_space \
						== controls_arguments_space
						
				if not is_controls_population_compatible:
					raise Exception() #!!!!! Создавать внятные исключения
					
					
			self.__state_space              = state_space
			self.__controls_arguments_space = controls_arguments_space
			self.__controls_populations     = dict(controls_populations)
			
			
			
	@property
	def state_space(self):
		return self.__state_space
		
		
	@property
	def controls_arguments_space(self):
		return self.__controls_arguments_space
		
		
		
	def __contains__(self, complex_control):
		contains_complex_control = True
		
		
		contains_complex_control &= \
			self.__state_space \
				== complex_control.state_space
				
		contains_complex_control &= \
			self.__controls_arguments_space \
				== complex_control.arguments_space
				
				
		if contains_complex_control:
			state_space_coordinates = self.__state_space.state_space_coordinates
			
			for state_space_coordinate in state_space_coordinates:
				control             = complex_control[state_space_coordinate]
				controls_population = \
					self.__controls_populations[
						state_space_coordinate
					]
					
				if control not in controls_population:
					contains_complex_control = False
					break
					
					
		return contains_complex_control
		
		
	def __len__(self):
		complex_controls_number = 0
		controls_populations    = self.__controls_populations.values()
		
		for controls_population in controls_populations:
			if complex_controls_number == 0:
				complex_controls_number = len(controls_population)
			else:
				complex_controls_number *= len(controls_population)
				
				
		return complex_controls_number
		
		
	def __getitem__(self, index):
		if index >= len(self):
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		complex_control = \
			ComplexControl(
				self.__state_space,
				self.__controls_arguments_space
			)
			
			
		residual_complex_controls_number = len(self)
		residual_index                   = index
		
		for state_space_coordinate in self.__state_space.state_space_coordinates:
			controls_population = \
				self.__controls_populations[
					state_space_coordinate
				]
				
				
			residual_complex_controls_number /= \
				len(controls_population)
			
			controls_population_index = \
				residual_index \
					// residual_complex_controls_number
					
			residual_index -= \
				residual_complex_controls_number \
					* controls_population_index
					
					
			complex_control[state_space_coordinate] = \
				controls_population[controls_population_index]
				
				
		return complex_control
		
		
		
	def get_controls_population(self, state_space_coordinate):
		if state_space_coordinate not in self.__state_space.state_space_coordinates:
			raise KeyError() #!!!!! Создавать внятные исключения
			
		return self.__controls_populations[state_space_coordinate]
		
		
		
		
		
class ControlsPopulationRating(object):
	def __init__(self, controls_population, control_tests_number):
		if control_tests_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self.__controls_population  = controls_population
		self.__control_tests_number = control_tests_number
		
		self.__unrated_controls       = set(controls_population)
		self.__controls_tests_results = \
			dict(
				[(control, []) for control in controls_population]
			)
			
			
			
	def __compute_control_rating(self, control_tests_results):
		control_tests_successful_results = \
			[control_test_result for control_test_result
				in control_tests_results
				if control_test_result is not None]
				
		if control_tests_successful_results:
			control_rating = sum(control_tests_successful_results)
		else:
			control_rating = None
			
			
		return control_rating
		
		
		
	@property
	def controls_population(self):
		return self.__controls_population
		
		
	@property
	def control_tests_number(self):
		return self.__control_tests_number
		
		
		
	def is_control_rated(self, control):
		if control in self.__controls_population:
			is_control_rated = control not in self.__unrated_controls
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		return is_control_rated
		
		
	@property
	def has_unrated_controls(self):
		return bool(self.__unrated_controls)
		
		
	def get_unrated_controls_population(self):
		if not self.has_unrated_controls:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		controls_population = \
			ControlsPopulation(
				self.__controls_population.controls_arguments_space,
				self.__unrated_controls
			)
			
		return controls_population
		
		
		
	def get_control_rating(self, control):
		try:
			is_control_rated = self.is_control_rated(control)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			if is_control_rated:
				control_tests_results = self.__controls_tests_results[control]
				control_rating        = \
					self.__compute_control_rating(
						control_tests_results
					)
			else:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
			return control_rating
			
			
	def set_control_test_result(self, control, control_test_result):
		try:
			is_control_rated = self.is_control_rated(control)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			if not is_control_rated:
				control_tests_results = self.__controls_tests_results[control]
				control_tests_results.append(control_test_result)
				
				if len(control_tests_results) == self.__control_tests_number:
					self.__unrated_controls.discard(control)
			else:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
				
class ControlsComplexPopulationRating(object):
	def __init__(self, controls_complex_population, control_tests_number):
		if control_tests_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		state_space_coordinates = \
			controls_complex_population.state_space \
				.state_space_coordinates
				
				
		first_controls_population_length = None
		
		for state_space_coordinate in state_space_coordinates:
			controls_population = \
				controls_complex_population.get_controls_population(
					state_space_coordinate
				)
				
			if first_controls_population_length is None:
				first_controls_population_length = len(controls_population)
			else:
				if len(controls_population) != first_controls_population_length:
					raise Exception() #!!!!! Создавать внятные исключения
					
					
		self.__controls_populations_ratings = dict()
		self.__controls_complex_population  = controls_complex_population
		self.__control_tests_number         = control_tests_number
		
		for state_space_coordinate in state_space_coordinates:
			controls_population = \
				controls_complex_population.get_controls_population(
					state_space_coordinate
				)
				
			self.__controls_populations_ratings[state_space_coordinate] = \
				ControlsPopulationRating(
					controls_population,
					control_tests_number
				)
				
				
				
	@property
	def controls_complex_population(self):
		return self.__controls_complex_population
		
		
	@property
	def control_tests_number(self):
		return self.__control_tests_number
		
		
		
	@property
	def has_unrated_controls(self):
		controls_populations_ratings = \
			list(
				self.__controls_populations_ratings \
					.values()
			)
			
		has_unrated_controls = \
			controls_populations_ratings[0] \
				.has_unrated_controls
				
				
		return has_unrated_controls
		
		
	def get_unrated_controls_complex_population(self):
		if not self.has_unrated_controls:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		unrated_controls_populations = dict()
		
		
		state_space_coordinates = \
			self.__controls_complex_population.state_space \
				.state_space_coordinates
				
		for state_space_coordinate in state_space_coordinates:
			controls_population_rating = \
				self.__controls_populations_ratings[
					state_space_coordinate
				]
				
			unrated_controls_populations[state_space_coordinate] = \
				controls_population_rating.get_unrated_controls_population()
				
				
		complex_population = \
			ControlsComplexPopulation(
				self.__controls_complex_population.controls_arguments_space,
				unrated_controls_populations
			)
			
		return complex_population
		
		
		
	def get_controls_population_rating(self, state_space_coordinate):
		state_space_coordinates = \
			self.__controls_complex_population.state_space.state_space_coordinates
			
			
		if state_space_coordinate not in state_space_coordinates:
			raise KeyError() #!!!!! Создавать внятные исключения
			
			
		controls_population_rating = \
			self.__controls_populations_ratings[
				state_space_coordinate
			]
			
		return controls_population_rating
		
		
	def set_complex_control_test_result(self,
											complex_control,
											complex_control_test_result):
		if complex_control not in self.__controls_complex_population:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			if self.has_unrated_controls:
				unrated_controls_complex_population = \
					self.get_unrated_controls_complex_population()
					
				if complex_control not in unrated_controls_complex_population:
					raise Exception() #!!!!! Создавать внятные исключения
			else:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
		state_space_coordinates = \
			self.__controls_complex_population.state_space \
				.state_space_coordinates
				
		for state_space_coordinate in state_space_coordinates:
			controls_population_rating = \
				self.__controls_populations_ratings[
					state_space_coordinate
				]
				
			controls_population_rating.set_control_test_result(
				complex_control[state_space_coordinate],
				complex_control_test_result
			)
			
			
			
			
			
class ImprovementDirection(object):
	def __new__(improvement_direction_class, *args, **kwargs):
		if improvement_direction_class is ImprovementDirection:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		try:
			instance = improvement_direction_class.__instance
		except AttributeError:
			instance = None
		else:
			if type(instance) is not improvement_direction_class:
				instance = None
				
		if instance is None:
			instance = \
				super(ImprovementDirection, improvement_direction_class) \
					.__new__(improvement_direction_class, *args, **kwargs)
					
			improvement_direction_class.__instance = instance
			
		return instance
		
		
		
class Maximization(ImprovementDirection):
	pass
	
	
	
class Minimization(ImprovementDirection):
	pass
	
	
	
	
	
class ControlsEvolutionParameters(object):
	def __init__(self,
					selected_controls_number,
					reproduced_controls_number,
					control_mutation_probability):
		if selected_controls_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if reproduced_controls_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if control_mutation_probability < 0.0 or control_mutation_probability > 1.0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self.__selected_controls_number     = selected_controls_number
		self.__reproduced_controls_number   = reproduced_controls_number
		self.__control_mutation_probability = control_mutation_probability
		
		
		
	@property
	def selected_controls_number(self):
		return self.__selected_controls_number
		
		
	@property
	def reproduced_controls_number(self):
		return self.__reproduced_controls_number
		
		
	@property
	def control_mutation_probability(self):
		return self.__control_mutation_probability
		
		
		
	@property
	def population_size(self):
		population_size = \
			self.__selected_controls_number \
				+ self.__reproduced_controls_number
				
		return population_size
		
		
		
# Отбор функций управления
def select_controls(controls_population_rating,
						selected_controls_number,
						improvement_direction):
	if controls_population_rating.has_unrated_controls:
		raise Exception() #!!!!! Создавать внятные исключения
		
	if selected_controls_number <= 0:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	controls = \
		[control for control
			in controls_population_rating.controls_population
			if controls_population_rating.get_control_rating(control) is not None]
			
	controls = \
		sorted(
			controls,
			key     = lambda control: controls_population_rating.get_control_rating,
			reverse = isinstance(improvement_direction, Maximization)
		)
		
	selected_controls = controls[0:selected_controls_number]
	
	
	return selected_controls
	
	
# Скрещивание функций управления
def reproduce_controls(controls_population_rating,
							reproduced_controls_number,
							control_mutation_probability,
							improvement_direction):
	# Выбор функции управления в соответствии с заданным законом распределния вероятностей
	def choose_control(controls_probability_distribution):
		chosen_control                   = None
		accumulated_controls_probability = 0.0
		sample                           = random.random()
		
		
		for control, control_probability in controls_probability_distribution:
			if control_probability != 0.0:
				accumulated_controls_probability += control_probability
				
				if accumulated_controls_probability >= sample:
					chosen_control = control
					break
					
		# Добавлено на случай влияния ошибки округления, когда суммарная вероятность меньше 1;
		# 	в этом случае за результат принимается последняя функция управления,
		# 	вероятность выбора которой отлична от нуля
		if chosen_control is None:
			for control, control_probability in controls_probability_distribution[::-1]:
				if control_probability != 0.0:
					chosen_control = control
					break
					
					
		return chosen_control
		
		
	def get_control_rating(control):
		control_rating = \
			controls_population_rating.get_control_rating(
				control
			)
			
		if control_rating is not None:
			if isinstance(improvement_direction, Minimization):
				control_rating *= -1.0
				
				
		return control_rating
		
		
		
	#
	if controls_population_rating.has_unrated_controls:
		raise Exception() #!!!!! Создавать внятные исключения
		
	if reproduced_controls_number <= 0:
		raise Exception() #!!!!! Создавать внятные исключения
		
	if control_mutation_probability < 0.0 or control_mutation_probability > 1.0:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
		
	# Фильтрация работоспособных функций управления
	controls = \
		[control for control
			in controls_population_rating.controls_population
			if get_control_rating(control) is not None]
			
	if not(controls):
		raise Exception() #!!!!! Создавать внятные исключения
		
		
		
	# Определение наихудшего и наилучшего результатов
	total_controls_rating = 0
	min_control_rating    = None
	max_control_rating    = None
	controls_number       = len(controls)
	
	for control in controls:
		control_rating = get_control_rating(control)
		
		if min_control_rating is None or control_rating < min_control_rating:
			min_control_rating = control_rating
			
		if max_control_rating is None or control_rating > max_control_rating:
			max_control_rating = control_rating
			
		total_controls_rating += control_rating
		
	total_controls_rating -= controls_number * min_control_rating
	
	
	
	# Вычисление вероятностей функций управления стать родителем
	controls_probability_distribution = []
	
	if min_control_rating == max_control_rating:
		# Равномерное распределение вероятностей
		control_probability = 1.0 / controls_number
		
		for control in controls:
			controls_probability_distribution.append(
				(control, control_probability)
			)
	else:
		# Вероятность пропорциональна вкладу функции в общую сумму
		for control in controls:
			control_rating = get_control_rating(control)
			
			control_probability = \
				(control_rating - min_control_rating) \
					/ total_controls_result
					
			controls_probability_distribution.append(
				(control, control_probability)
			)
			
			
			
	# Генерация новых функций управления
	reproduced_controls = []
	
	while len(reproduced_controls) < reproduced_controls_number:
		# Выбор родительской пары функций управления
		first_control, second_control = \
			choose_control(controls_probability_distribution), \
				choose_control(controls_probability_distribution)
				
		# Скрещивание функций управления
		sample = random.random()
		
		reproduced_control = \
			optimization.controls.reproduce_controls(
				first_control,
				second_control,
				sample < control_mutation_probability
			)
			
			
		reproduced_controls.append(reproduced_control)
		
		
		
	return reproduced_controls
	
	
def evolve_controls_population(controls_population_rating,
									controls_evolution_parameters,
									improvement_direction):
	if controls_population_rating.has_unrated_controls:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	# Создание нового поколения функций управления
	evolved_controls = []
	
	# Скрещивание функций управления
	evolved_controls += \
		reproduce_controls(
			controls_population_rating,
			controls_evolution_parameters.reproduced_controls_number,
			controls_evolution_parameters.control_mutation_probability,
			improvement_direction
		)
	# try:
		# evolved_controls += \
			# reproduce_controls(
				# controls_population_rating,
				# controls_evolution_parameters.reproduced_controls_number,
				# controls_evolution_parameters.control_mutation_probability,
				# improvement_direction
			# )
	# except:
		# pass
		
	# Селекция функций управления
	evolved_controls += \
		select_controls(
			controls_population_rating,
			controls_evolution_parameters.selected_controls_number,
			improvement_direction
		)
		
		
	return ControlsPopulation(evolved_controls)
	
	
	
def evolve_complex_controls_population(controls_complex_population_rating,
											controls_evolution_parameters,
											improvement_direction):
	if controls_complex_population_rating.has_unrated_controls:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
		
	controls_complex_population = \
		controls_complex_population_rating.controls_complex_population
		
		
	evolved_controls_populations = dict()
	
	state_space_coordinates = \
		controls_complex_population.state_space.state_space_coordinates
		
	for state_space_coordinate in state_space_coordinates:
		controls_population_rating = \
			controls_complex_population_rating.get_controls_population_rating(
				state_space_coordinate
			)
			
		evolved_controls_populations[state_space_coordinate] = \
			evolve_controls_population(
				controls_population_rating,
				controls_evolution_parameters,
				improvement_direction
			)
			
			
	evolved_controls_complex_population = \
		ControlsComplexPopulation(
			controls_complex_population.controls_arguments_space,
			evolved_controls_populations
		)
		
	return evolved_controls_complex_population
	