from collections import Set, Iterator
from machine     import StateSpace

import random



class ControlsPopulation(Set, Iterator):
	def __init__(self, controls_arguments_space, controls):
		for control in controls:
			if controls_arguments_space != control.arguments_space:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
		self.__controls_arguments_space = controls_arguments_space
		self.__controls                 = frozenset(controls)
		
		
	# Реализация интерфейса множества
	def __contains__(self, control):
		return control in self.__controls
		
	def __iter__(self):
		return self
		
	def __len__(self):
		return len(self.__controls)
		
		
	# Доступ к функциям управления по индексу
	def __getitem__(self, index):
		if index < len(self.__controls):
			current_index  = 0
			result_control = None
			
			for control in self.__controls:
				if current_index == index:
					result_control = control
				else:
					current_index += 1
		else:
			raise IndexError() #!!!!! Создавать внятные исключения
			
		return result_control
		
		
	# Реализация итерирования
	def next(self):
		for control in self.__controls:
			yield control
			
		raise StopIteration
		
		
		
#!!!!!
class ControlsComplexPopulation(object):
	def __init__(self, **controls_populations):
		self.controls_populations = dict()
		self.state_space = \
			StateSpace(
				controls_populations.iterkeys()
			)
			
		for controls_population_name in self.controls_populations_names:
			self.controls_populations[controls_population_name] = \
				controls_populations[controls_population_name]
				
				
	def __contains__(self, complex_control):
		is_complex_control_compatible = \
			self.controls_populations_names == complex_control.controls_names
			
		if not is_complex_control_compatible:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		contains_complex_control = True
		
		for control_name in complex_control.controls_names:
			control             = complex_control[control_name]
			controls_population = self[control_name]
			
			if control not in controls_population:
				contains_complex_control = False
				break
				
				
		return contains_complex_control
		
	def __len__(self):
		complex_controls_number = 0
		
		for controls_population in self.controls_populations:
			complex_controls_number *= len(controls_population)
			
		return complex_controls_number
		
	def __getitem__(self, index):
		complex_control = ComplexControl(self.controls_populations_names)
		
		
		residual_complex_controls_number = len(self)
		residual_index                   = index
		
		for controls_population_name in self.controls_populations_names:
			controls_population = self.controls_populations[controls_population_name]
			
			
			residual_complex_controls_number /= \
				len(controls_population)
			
			controls_population_index = \
				residual_index \
					// residual_complex_controls_number
					
			residual_index -= \
				residual_complex_controls_number \
					* controls_population_index
					
					
			complex_control[controls_population_name] = \
				controls_population[controls_population_index]
				
				
		return complex_control
		
		
	def get_controls_population(self, controls_population_name):
		if controls_population_name in self.controls_populations_names:
			controls_population = \
				self.controls_populations[controls_population_name]
		else:
			raise KeyError() #!!!!! Создавать внятные исключения
			
		return controls_population
		
		
		
class ControlsPopulationRating(object):
	def __init__(self, controls_population, control_tests_number):
		if control_tests_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self.controls_population  = controls_population
		self.control_tests_number = control_tests_number
		
		self.unrated_controls       = set(controls_population)
		self.controls_tests_results = \
			dict(
				[(control, []) for control in controls_population]
			)
			
			
	def compute_control_rating(self, control_tests_results):
		control_tests_successful_results = \
			[control_test_result for control_test_result
				in control_tests_results
				if control_test_result is not None]
				
		if control_tests_successful_results:
			control_rating = sum(control_tests_successful_results)
		else:
			control_rating = None
			
		return control_rating
		
		
	def is_control_rated(self, control):
		if control in controls_population:
			is_control_rated = control not in self.unrated_controls
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
		return is_control_rated
		
	def has_unrated_controls(self):
		return bool(self.unrated_controls)
		
	def get_unrated_controls_population(self):
		return ControlsPopulation(self.unrated_controls)
		
		
	def get_control_rating(self, control):
		try:
			is_correct_control = self.is_control_rated(control)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			control_tests_results = self.controls_tests_results[control]
			control_rating        = self.compute_control_rating(control_tests_results)
			
			return control_rating
			
	def set_control_test_result(self, control, control_test_result):
		try:
			is_correct_control = not self.is_control_rated(control)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			if is_correct_control:
				control_tests_results = self.controls_tests_results[control]
				control_tests_results.append(control_test_result)
				
				if len(control_tests_results) == control_tests_number:
					self.unrated_controls.discard(control)
			else:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
				
class ControlsComplexPopulationRating(object):
	def __init__(self, controls_complex_population, control_tests_number):
		controls_populations_names = \
			controls_complex_population.controls_populations_names
			
			
		controls_populations_lengths = \
			[len(controls_complex_population[controls_population_name])
				for controls_population_name
				in  controls_populations_names]
				
		filtered_controls_populations_lengths = \
			filter(
				lambda controls_population_length:
					controls_population_length != controls_populations_lengths[0],
				controls_populations_lengths
			)
			
		if filtered_controls_populations_lengths:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self.controls_populations_ratings = dict()
		self.controls_complex_population  = controls_complex_population
		self.control_tests_number         = control_tests_number
		
		for controls_population_name in controls_populations_names:
			self.controls_populations_ratings[controls_population_name] = \
				ControlsPopulationRating(
					controls_complex_population[controls_population_name],
					control_tests_number
				)
				
				
	def get_controls_population_rating(self, controls_population_name):
		controls_populations_names = \
			self.controls_complex_population.controls_populations_names
			
		if controls_population_name in controls_populations_names:
			controls_population_rating = \
				self.controls_populations_ratings[controls_population_name]
		else:
			raise KeyError() #!!!!! Создавать внятные исключения
			
		return controls_population_rating
		
		
	def has_unrated_controls(self):
		controls_populations_ratings = self.controls_populations_ratings.values()
		
		if controls_populations_ratings:
			controls_population_rating = controls_populations_ratings[0]
			
			has_unrated_controls = \
				controls_population_rating.has_unrated_controls()
		else:
			has_unrated_controls = False
			
		return has_unrated_controls
		
		
	def get_unrated_controls_complex_population(self):
		unrated_controls_populations = dict()
		
		
		controls_populations_names = controls_complex_population.controls_names
		
		for controls_population_name in controls_populations_names:
			controls_population_rating = \
				self.controls_populations_ratings[controls_population_name]
				
			unrated_controls_populations[controls_population_name] = \
				controls_population_rating.get_unrated_controls_population()
				
				
		return ControlsComplexPopulation(**unrated_controls_populations)
		
		
	def set_complex_control_test_result(self,
											complex_control,
											complex_control_test_result):
		is_complex_control_compatible = \
			self.controls_complex_population.controls_populations_names
				== complex_control.controls_names
				
		if is_complex_control_compatible:
			if complex_control not in self.controls_complex_population:
				raise Exception() #!!!!! Создавать внятные исключения
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		for control_name in complex_control.controls_names:
			controls_population_rating = self[control_name]
			
			controls_population_rating.set_control_test_result(
				complex_control[control_name],
				complex_control_test_result
			)
			
			
			
class ControlsEvolutionParameters(object):
	def __init__(self,
					selected_controls_number,
					reproduced_controls_number,
					control_mutation_probability):
		if selected_controls_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if reproduced_controls_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if control_mutation_probability < 0 or control_mutation_probability > 1:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self.selected_controls_number     = selected_controls_number
		self.reproduced_controls_number   = reproduced_controls_number
		self.control_mutation_probability = control_mutation_probability
		
		
	@property
	def population_size(self):
		population_size = \
			self.selected_controls_number \
				+ self.reproduced_controls_number
				
		return population_size
		
		
		
# Отбор функций управления
def select_controls(controls_population_rating, selected_controls_number):
	if controls_population_rating.has_unrated_controls():
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
			reverse = True
		)
		
	selected_controls = controls[0:selected_controls_number]
	
	
	return selected_controls
	
	
# Скрещивание функций управления
def reproduce_controls(controls_population_rating,
							reproduced_controls_number,
							control_mutation_probability):
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
		
		
		
	#
	if controls_population_rating.has_unrated_controls():
		raise Exception() #!!!!! Создавать внятные исключения
		
	if reproduced_controls_number <= 0:
		raise Exception() #!!!!! Создавать внятные исключения
		
	if control_mutation_probability < 0 or control_mutation_probability > 1:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
		
	# Фильтрация работоспособных функций управления
	controls = \
		[control for control
			in controls_population_rating.controls_population
			if controls_population_rating.get_control_rating(control) is not None]
			
	if not(controls):
		raise Exception() #!!!!! Создавать внятные исключения
		
		
		
	# Определение наихудшего и наилучшего результатов
	total_controls_rating = 0
	min_control_rating    = None
	max_control_rating    = None
	controls_number       = len(controls)
	
	for control in controls:
		control_rating = controls_population_rating.get_control_rating(control)
		
		if control_rating < min_control_rating or min_control_rating is None:
			min_control_rating = control_rating
			
		if control_rating > max_control_rating or max_control_rating is None:
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
			control_rating = controls_population_rating.get_control_rating(control)
			
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
		
		control = \
			reproduce_controls(
				first_control,
				second_control,
				sample < control_mutation_probability
			)
			
			
		reproduced_controls.append(control)
		
		
		
	return reproduced_controls
	
	
def evolve_controls_population(controls_population_rating,
									controls_evolution_parameters):
	if controls_population_rating.has_unrated_controls():
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	# Создание нового поколения функций управления
	evolved_controls = []
	
	# Скрещивание функций управления
	try:
		evolved_controls += \
			reproduce_controls(
				controls_population_rating,
				controls_evolution_parameters.reproduced_controls_number,
				controls_evolution_parameters.control_mutation_probability
			)
	except:
		pass
		
	# Селекция функций управления
	evolved_controls += \
		select_controls(
			controls_population_rating,
			controls_evolution_parameters.selected_controls_number
		)
		
		
	return ControlsPopulation(evolved_controls)
	
	
	
def evolve_complex_controls_population(controls_complex_population_rating,
											controls_evolution_parameters):
	if controls_complex_population_rating.has_unrated_controls():
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	#
	evolved_controls_populations = dict()
	
	
	controls_complex_population = \
		controls_complex_population_rating.controls_complex_population
		
	controls_populations_names = \
		controls_complex_population.controls_populations_names
		
	for controls_population_name in controls_populations_names
		controls_population_rating = \
			controls_complex_population_rating.get_controls_population_rating(
				controls_population_name
			)
			
		evolved_controls_populations[controls_population_name] = \
			evolve_controls_population(
				controls_population_rating,
				controls_evolution_parameters
			)
			
			
	return ControlsComplexPopulation(**evolved_controls_populations)
	