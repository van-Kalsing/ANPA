#!!!!! 1. В рейтинге комплексной популяции убрать доступ к рейтингам
#!!!!! 		отдельных популяций напрямую, т.к. они изменяемые.
#!!!!! 		Реализовать клонирование рейтингов и возвращать копии
#!!!!! 2. В рейтинге комплексной популяции убрать подсчет количества возможных
#!!!!! 		комплексных функций управления (если останется, то поправить
#!!!!! 		подсчет, в случае пустой популяции может выдавать неверные данные),
#!!!!! 		а также убрать доступ по индексу к комплексным ФУ (__getitem__
#!!!!! 		использовать для доступа к функции управления по координате
#!!!!! 		пространства состояний)

from optimization.machine \
	import StateSpaceCoordinate, \
				CustomStateSpace
				
from collections                         import Sequence
from optimization._controls.arguments    import ArgumentsSpace
from optimization._controls.controls     import Control, ComplexControl
from optimization.evolution.criterions   import Maximization, Minimization
from optimization.evolution.reproduction import reproduce_controls
from random                              import random







class ControlsPopulation:
	def __init__(self, controls_arguments_space, controls):
		super(ControlsPopulation, self).__init__()
		
		
		self.__controls_arguments_space = controls_arguments_space
		self.__controls                 = list(controls)
		
		for control in self.__controls:
			if self.__controls_arguments_space != control.arguments_space:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
				
	@property
	def controls_arguments_space(self):
		return self.__controls_arguments_space
		
		
	#!!!!! Убрать, когда вернется __len__ и наследуется collections.Sequence
	#!!!!! Используется в controlsOptimization
	@property
	def controls(self):
		return list(self.__controls)
		
		
		
	# def __len__(self):
	# 	return len(self.__controls)
	
	
	#!!!!! Заменить обратно на __len__
	#!!!!! Используется в текущем файле и в controlsOptimization
	@property
	def count(self):
		return len(self.__controls)
		
		
	# def __getitem__(self, index):
	# 	if index >= len(self.__controls):
	# 		raise IndexError() #!!!!! Создавать внятные исключения
			
	# 	return self.__controls[index]
		
		
	# #!!!!! Наследовать collections.Sequence и убрать, когда вернется __len__
	# def __contains__(self, control):
	# 	return control in self.__controls
		
		
	# #!!!!! Наследовать collections.Sequence и убрать, когда вернется __len__
	# def __iter__(self):
	# 	return iter(self.__controls)
		
		
		
		
		
class ControlsComplexPopulation:
	def __init__(self, controls_populations_map):
		super(ControlsComplexPopulation, self).__init__()
		
		
		
		self.__controls_populations_map = dict(controls_populations_map)
		
		
		
		# Проверка популяций функций управления:
		# 	Все функции управления должны иметь одно пространство аргументов
		controls_arguments_space = None
		
		for state_space_coordinate in self.__controls_populations_map:
			controls_population = \
				self.__controls_populations_map[
					state_space_coordinate
				]
				
			if controls_arguments_space is None:
				controls_arguments_space = \
					controls_population.controls_arguments_space
			else:
				are_controls_populations_compatible = \
					controls_arguments_space \
						== controls_population.controls_arguments_space
						
				if not are_controls_populations_compatible:
					raise Exception() #!!!!! Создавать внятные исключения
					
					
					
		# Проверка популяций функций управления:
		# 	Должна присутствовать хотя бы одна популяция функций управления
		if len(self.__controls_populations_map) == 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		# Приведение словаря к списковому представлению
		state_space_coordinates = []
		controls_populations    = []
		
		
		for state_space_coordinate in self.__controls_populations_map:
			state_space_coordinates.append(state_space_coordinate)
			
			controls_populations.append(
				self.__controls_populations_map[state_space_coordinate]
			)
			
			
		self.__state_space_coordinates = frozenset(state_space_coordinates)
		self.__state_space             = \
			CustomStateSpace(
				state_space_coordinates
			)
			
		self.__controls_populations     = frozenset(controls_populations)
		self.__controls_arguments_space = \
			controls_populations[0].controls_arguments_space
			
			
			
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
			for state_space_coordinate in self.__state_space_coordinates:
				control             = complex_control[state_space_coordinate]
				controls_population = \
					self.__controls_populations_map[
						state_space_coordinate
					]
					
				if control not in controls_population.controls:
					contains_complex_control = False
					break
					
					
		return contains_complex_control
		
		
	#!!!!! Убрать или заменить на __len__
	@property
	def count(self):
		complex_controls_number = 0
		
		for controls_population in self.__controls_populations:
			if complex_controls_number == 0:
				complex_controls_number = controls_population.count
			else:
				complex_controls_number *= controls_population.count
				
				
		return complex_controls_number
		
		
	def __getitem__(self, index):
		if index >= self.count:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		controls = dict()
		
		
		residual_complex_controls_number = self.count
		residual_index                   = index
		
		for state_space_coordinate in self.__state_space_coordinates:
			controls_population = \
				self.__controls_populations_map[
					state_space_coordinate
				]
				
				
			residual_complex_controls_number /= \
				controls_population.count
			
			controls_population_index = \
				residual_index \
					// residual_complex_controls_number
					
			residual_index -= \
				residual_complex_controls_number \
					* controls_population_index
					
					
			controls[state_space_coordinate] = \
				controls_population.controls[
					controls_population_index
				]
				
				
		return ComplexControl(controls)
		
		
		
	def get_controls_population(self, state_space_coordinate):
		if state_space_coordinate not in self.__state_space_coordinates:
			raise KeyError() #!!!!! Создавать внятные исключения
			
		return self.__controls_populations_map[state_space_coordinate]
		
		
		
		
		
		
		
class ControlsPopulationRating:
	def __init__(self, controls_population):
		super(ControlsPopulationRating, self).__init__()
		
		
		self.__controls_population = controls_population
		
		self.__controls_accumulated_ratings = \
			dict(
				[(control, None) for control in controls_population.controls]
			)
			
		self.__controls_ratings_numbers = \
			dict(
				[(control, 0) for control in controls_population.controls]
			)
			
			
			
	@property
	def controls_population(self):
		return self.__controls_population
		
		
		
	@property
	def has_unrated_controls(self):
		has_unrated_controls     = False
		controls_ratings_numbers = self.__controls_ratings_numbers.values()
		
		for control_ratings_number in controls_ratings_numbers:
			if control_ratings_number == 0:
				has_unrated_controls = True
				break
				
				
		return has_unrated_controls
		
		
	def is_control_rated(self, control):
		if control not in self.__controls_population.controls:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		return self.__controls_ratings_numbers[control] != 0
		
		
	def get_control_average_rating(self, control):
		if control not in self.__controls_population.controls:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if self.__controls_ratings_numbers[control] == 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		control_accumulated_rating = \
			self.__controls_accumulated_ratings[
				control
			]
			
		if control_accumulated_rating is not None:
			control_average_rating = \
				float(control_accumulated_rating) \
					/ float(self.__controls_ratings_numbers[control])
		else:
			control_average_rating = None
			
			
		return control_average_rating
		
		
	def rate_control(self, control, control_rating):
		if control not in self.__controls_population.controls:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		if self.__controls_accumulated_ratings[control] is not None:
			if control_rating is None:
				control_rating = 0.0
				
			self.__controls_accumulated_ratings[control] += control_rating
		else:
			self.__controls_accumulated_ratings[control] = control_rating
			
		self.__controls_ratings_numbers[control] += 1
		
		
		
		
		
class ControlsComplexPopulationRating:
	def __init__(self, controls_complex_population):
		super(ControlsComplexPopulationRating, self).__init__()
		
		
		self.__controls_complex_population  = controls_complex_population
		self.__controls_populations_ratings = dict()
		self.__state_space_coordinates      = \
			controls_complex_population.state_space \
				.state_space_coordinates
				
				
		for state_space_coordinate in self.__state_space_coordinates:
			controls_population = \
				controls_complex_population.get_controls_population(
					state_space_coordinate
				)
				
			self.__controls_populations_ratings[state_space_coordinate] = \
				ControlsPopulationRating(
					controls_population
				)
				
				
				
	@property
	def controls_complex_population(self):
		return self.__controls_complex_population
		
		
		
	#!!!!! Копировать рейтинг
	def get_controls_population_rating(self, state_space_coordinate):
		if state_space_coordinate not in self.__state_space_coordinates:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		controls_population_rating = \
			self.__controls_populations_ratings[
				state_space_coordinate
			]
			
		return controls_population_rating
		
		
	def rate_complex_control(self,
								complex_control,
								complex_control_rating):
		if complex_control not in self.__controls_complex_population:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		for state_space_coordinate in self.__state_space_coordinates:
			controls_population_rating = \
				self.__controls_populations_ratings[
					state_space_coordinate
				]
				
			control = complex_control[state_space_coordinate]
			
			
			controls_population_rating.rate_control(
				control,
				complex_control_rating
			)
			
			
			
			
			
			
			
class ControlsEvolutionParameters:
	def __init__(self,
					selected_controls_number,
					reproduced_controls_number,
					control_mutation_probability):
		super(ControlsEvolutionParameters, self).__init__()
		
		
		if selected_controls_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if reproduced_controls_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if control_mutation_probability < 0.0:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if control_mutation_probability > 1.0:
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
		
		
		
		
		
		
		
def reproduce_controls_population(controls_population_rating,
									improvement_direction,
									evolution_parameters,
									constructing_parameters):
	# Выбор функции управления в соответствии с заданным законом распределния
	# вероятностей
	def choose_control(controls_probability_distribution):
		chosen_control                   = None
		accumulated_controls_probability = 0.0
		sample                           = random()
		
		
		for control, control_probability in controls_probability_distribution:
			accumulated_controls_probability += control_probability
			
			if accumulated_controls_probability > sample:
				chosen_control = control
				break
				
		# Добавлено на случай влияния ошибки округления, когда суммарная
		# вероятность меньше 1; в этом случае за результат принимается последняя
		# функция управления, вероятность выбора которой отлична от нуля
		if chosen_control is None:
			for control_probability in controls_probability_distribution[::-1]:
				control, control_probability = control_probability
				
				if control_probability != 0.0:
					chosen_control = control
					break
					
					
		return chosen_control
		
		
		
		
	if controls_population_rating.has_unrated_controls:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	controls_population = controls_population_rating.controls_population
	
	are_controls_arguments_spaces_equal = \
		controls_population.controls_arguments_space \
			== constructing_parameters.controls_arguments_space
			
	if not are_controls_arguments_spaces_equal:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	for control in controls_population_rating.controls_population.controls:
		if control.height > constructing_parameters.controls_max_height:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
	# Фильтрация работоспособных функций управления и сбор статистики
	controls_ratings = []
	
	total_controls_rating = 0
	min_controls_rating   = None
	max_controls_rating   = None
	
	
	for control in controls_population_rating.controls_population.controls:
		# Вычисление рейтинга функции управления, с учетом направления
		# улучшения рейтинга
		control_rating = \
			controls_population_rating.get_control_average_rating(
				control
			)
			
		if isinstance(improvement_direction, Minimization):
			if control_rating is not None:
				control_rating *= -1.0
				
				
				
		if control_rating is not None:
			controls_ratings.append(
				(control, control_rating)
			)
			
			
			total_controls_rating += control_rating
			
			if min_controls_rating is None:
				min_controls_rating = control_rating
				max_controls_rating = control_rating
				
			elif control_rating < min_controls_rating:
				min_controls_rating = control_rating
				
			elif control_rating > max_controls_rating:
				max_controls_rating = control_rating
				
				
				
	if controls_ratings:
		# Вычисление вероятностей функций управления стать родителем
		controls_probability_distribution = []
		controls_number                   = len(controls_ratings)
		
		
		if min_controls_rating == max_controls_rating:
			# Равномерное распределение вероятностей
			control_probability = 1.0 / controls_number
			
			for control, control_rating in controls_ratings:
				controls_probability_distribution.append(
					(control, control_probability)
				)
		else:
			# Вероятность пропорциональна вкладу функции в общую сумму
			normalized_total_controls_rating = \
				total_controls_rating \
					- (controls_number * min_controls_rating)
					
			for control, control_rating in controls_ratings:
				control_probability = \
					(control_rating - min_controls_rating) \
						/ normalized_total_controls_rating
						
				controls_probability_distribution.append(
					(control, control_probability)
				)
				
				
				
		# Генерация новых функций управления
		generated_controls = []
		
		for _ in range(evolution_parameters.reproduced_controls_number):
			# Выбор родительской пары функций управления
			first_control, second_control = \
				choose_control(controls_probability_distribution), \
					choose_control(controls_probability_distribution)
					
					
			generated_control = \
				reproduce_controls(
					first_control,
					second_control,
					evolution_parameters.control_mutation_probability,
					constructing_parameters
				)
				
			generated_controls.append(generated_control)
	else:
		generated_controls = []
		
		
		
	return generated_controls
	
	
	
	
	
def filter_controls_population(controls_population_rating,
									improvement_direction,
									evolution_parameters):
	if controls_population_rating.has_unrated_controls:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	# Фильтрация работоспособных функций
	useful_controls = []
	
	for control in controls_population_rating.controls_population.controls:
		control_rating = \
			controls_population_rating.get_control_average_rating(
				control
			)
			
		if control_rating is not None:
			useful_controls.append(control)
			
			
	# Сортировка работоспособных функций
	sorted_controls = \
		sorted(
			useful_controls,
			key     = controls_population_rating.get_control_average_rating,
			reverse = isinstance(improvement_direction, Maximization)
		)
		
		
	# Выбор заданного числа лучших работоспособных функций
	selected_controls = \
		sorted_controls[
			0:evolution_parameters.selected_controls_number
		]
		
		
	return selected_controls
	
	
	
	
	
def evolve_controls_population(controls_population_rating,
									improvement_direction,
									evolution_parameters,
									constructing_parameters):
	if controls_population_rating.has_unrated_controls:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
		
	# Создание нового поколения функций управления
	evolved_controls = []
	
	# try:
	# Скрещивание функций управления
	evolved_controls += \
		reproduce_controls_population(
			controls_population_rating,
			improvement_direction,
			evolution_parameters,
			constructing_parameters
		)
		
	# Селекция функций управления
	evolved_controls += \
		filter_controls_population(
			controls_population_rating,
			improvement_direction,
			evolution_parameters
		)
	# except:
	# 	raise Exception() #!!!!! Создавать внятные исключения
		
		
	controls_arguments_space = \
		controls_population_rating.controls_population \
			.controls_arguments_space
			
			
	evolved_controls_population = \
		ControlsPopulation(
			controls_arguments_space,
			evolved_controls
		)
		
	return evolved_controls_population
	
	
	
	
	
def evolve_complex_controls_population(controls_complex_population_rating,
											improvement_direction,
											evolution_parameters,
											constructing_parameters):
	state_space = \
		controls_complex_population_rating.controls_complex_population \
			.state_space
			
			
	evolved_controls_populations = dict()
	
	for state_space_coordinate in state_space.state_space_coordinates:
		controls_population_rating = \
			controls_complex_population_rating \
				.get_controls_population_rating(
					state_space_coordinate
				)
				
		evolved_controls_populations[state_space_coordinate] = \
			evolve_controls_population(
				controls_population_rating,
				improvement_direction,
				evolution_parameters,
				constructing_parameters
			)
			
			
	evolved_controls_complex_population = \
		ControlsComplexPopulation(
			evolved_controls_populations
		)
		
	return evolved_controls_complex_population
	