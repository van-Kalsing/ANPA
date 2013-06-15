#!!!!! 1. В рейтинге комплексной популяции убрать доступ к рейтингам
#!!!!! 		отдельных популяций напрямую, т.к. они изменяемые.
#!!!!! 		Реализовать клонирование рейтингов и возвращать копии
#!!!!! 2. В рейтинге комплексной популяции убрать подсчет количества возможных
#!!!!! 		комплексных функций управления (если останется, то поправить
#!!!!! 		подсчет, в случае пустой популяции может выдавать неверные данные),
#!!!!! 		а также убрать доступ по индексу к комплексным ФУ (__getitem__
#!!!!! 		использовать для доступа к функции управления по координате
#!!!!! 		пространства состояний)

from mongoengine \
	import Document, \
				EmbeddedDocument, \
				FloatField, \
				IntField
				
from collections                       import Sequence
from optimization._controls.controls   import ComplexControl
from optimization.evolution.criterions import Maximization, Minimization
from optimization.machine              import CustomStateSpace
from random                            import random

import optimization







class ControlsPopulation(Sequence, Document):
	# Настройка отображения на БД
	meta = \
		{
			'collection': 'controls_populations'
		}
		
		
	__controls = \
		FloatField(
			required = True,
			db_field = 'controls',
			default  = None
		)
		
		
	__controls_arguments_space = \
		IntField(
			ArgumentsSpace,
			required = True,
			db_field = 'controls_arguments_space',
			default  = None
		)
		
		
		
	def __init__(self,
					controls_arguments_space = None,
					controls                 = None,
					*args,
					**kwargs):
		super(ControlsPopulation, self).__init__(*args, **kwargs)
		
		if self.__controls is None:
			if controls_arguments_space is None:
				raise Exception() #!!!!! Создавать внятные исключения
				
			if controls is None:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
			self.__controls_arguments_space = controls_arguments_space
			self.__controls                 = list(controls)
			
			for control in self.__controls:
				if self.__controls_arguments_space != control.arguments_space:
					raise Exception() #!!!!! Создавать внятные исключения
					
					
					
	@property
	def controls_arguments_space(self):
		return self.__controls_arguments_space
		
		
		
	def __len__(self):
		return len(self.__controls)
		
		
	def __getitem__(self, index):
		if index >= len(self.__controls):
			raise IndexError() #!!!!! Создавать внятные исключения
			
		return self.__controls[index]
		
		
		
		
		
class ControlsComplexPopulation(Document):
	# Настройка отображения на БД
	meta = \
		{
			'collection': 'controls_populations'
		}
		
		
	__controls_populations_db_view = \
		DynamicField(
			required = True,
			db_field = 'controls_populations',
			default  = None
		)
		
		
		
	def __init__(self, controls_populations = None, *args, **kwargs):
		super(ControlsComplexPopulation, self).__init__(*args, **kwargs)
		
		
		if self.__controls_populations_db_view is not None:
			# Восстановление словаря из спискового представления
			self.__controls_populations = dict()
			
			for controls_population in self.__controls_db_view:
				state_space_coordinate, controls_population = \
					controls_population
					
				self.__controls_populations[state_space_coordinate] = \
					controls_population
		else:
			if controls_populations is None:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
				
			self.__controls_populations = dict(controls_populations)
			
			
			# Проверка популяций функций управления:
			# 	Все функции управления должны иметь одно пространство аргументов
			controls_arguments_space = None
			
			for state_space_coordinate in self.__controls_populations:
				controls_population = \
					self.__controls_populations[
						state_space_coordinate
					]
					
				if controls_arguments_space is None:
					controls_arguments_space = \
						controls_population.controls_arguments_space
				else:
					are_controls_populations_compatible = \
						controls_arguments_space \
							!= controls_population.controls_arguments_space
							
					if not are_controls_populations_compatible:
						raise Exception() #!!!!! Создавать внятные исключения
						
						
			# Проверка популяций функций управления:
			# 	Должна присутствовать хотя бы одна популяция функций управления
			if len(self.__controls_populations) == 0:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
			# Приведение словаря к списковому представлению
			self.__controls_populations_db_view = []
			
			for state_space_coordinate in self.__controls_populations:
				controls_population = \
					self.__controls_populations[
						state_space_coordinate
					]
					
				self.__controls_populations_db_view.append(
					[state_space_coordinate, controls_population]
				)
				
				
		self.__state_space = \
			CustomStateSpace(
				self.__controls_populations.keys()
			)
			
		self.__controls_arguments_space = \
			list(self.__controls_populations.values())[0] \
				.controls_arguments_space
				
				
				
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
			
			
			
		controls = dict()
		
		
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
					
					
			controls[state_space_coordinate] = \
				controls_population[controls_population_index]
				
				
		return ComplexControl(controls)
		
		
		
	def get_controls_population(self, state_space_coordinate):
		if state_space_coordinate not in self.__state_space.state_space_coordinates:
			raise KeyError() #!!!!! Создавать внятные исключения
			
		return self.__controls_populations[state_space_coordinate]
		
		
		
		
		
		
		
class ControlsPopulationRating:
	def __init__(self, controls_population):
		super(ControlsPopulationRating, self).__init__()
		
		
		self.__controls_population = controls_population
		
		self.__controls_accumulated_ratings = \
			dict(
				[(control, None) for control in controls_population]
			)
			
		self.__controls_ratings_numbers = \
			dict(
				[(control, 0) for control in controls_population]
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
		if control not in self.__controls_population:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		return self.__controls_ratings_numbers[control] != 0
		
		
	def get_control_average_rating(self, control):
		if control not in self.__controls_population:
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
		if control not in self.__controls_population:
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
			
			
			
			
			
			
			
class ControlsEvolutionParameters(EmbeddedDocument):
	# Настройка отображения на БД
	__selected_controls_number = \
		IntField(
			required = True,
			db_field = 'selected_controls_number',
			default  = None
		)
		
		
	__reproduced_controls_number = \
		IntField(
			required = True,
			db_field = 'reproduced_controls_number',
			default  = None
		)
		
		
	__control_mutation_probability = \
		FloatField(
			required = True,
			db_field = 'control_mutation_probability',
			default  = None
		)
		
		
		
	def __init__(self,
					selected_controls_number     = None,
					reproduced_controls_number   = None,
					control_mutation_probability = None,
					*args,
					**kwargs):
		super(ControlsEvolutionParameters, self).__init__(*args, **kwargs)
		
		
		if self.__selected_controls_number is None:
			if selected_controls_number is None:
				raise Exception() #!!!!! Создавать внятные исключения
				
			if reproduced_controls_number is None:
				raise Exception() #!!!!! Создавать внятные исключения
				
			if control_mutation_probability is None:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
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
		
		
		
		
		
		
		
def select_controls(controls_population_rating,
						improvement_direction,
						evolution_parameters):
	if controls_population_rating.has_unrated_controls:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	# Фильтрация работоспособных функций
	useful_controls = []
	
	for control in controls_population_rating.controls_population:
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
	
	
	
	
	
def reproduce_population(controls_population_rating,
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
		
		
	are_controls_arguments_spaces_equal = \
		controls_population_rating.controls_arguments_space \
			== constructing_parameters.controls_arguments_space
			
	if not are_controls_arguments_spaces_equal:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	for control in controls_population_rating.controls_population:
		if control.height > constructing_parameters.controls_max_height:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
	# Фильтрация работоспособных функций управления и сбор статистики
	controls_ratings = []
	
	total_controls_rating = 0
	min_controls_rating   = None
	max_controls_rating   = None
	
	
	for control in controls_population_rating.controls_population:
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
			
			if min_control_rating is None:
				min_control_rating = control_rating
				max_control_rating = control_rating
				
			elif control_rating < min_control_rating:
				min_control_rating = control_rating
				
			elif control_rating > max_control_rating:
				max_control_rating = control_rating
				
				
				
	if controls_ratings:
		# Вычисление вероятностей функций управления стать родителем
		controls_probability_distribution = []
		controls_number                   = len(controls_ratings)
		
		
		if min_control_rating == max_control_rating:
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
					- (controls_number * min_control_rating)
					
			for control, control_rating in controls_ratings:
				control_probability = \
					(control_rating - min_control_rating) \
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
	
	
	
	
	
def evolve_controls_population(controls_population_rating,
									controls_evolution_parameters,
									improvement_direction):
	if controls_population_rating.has_unrated_controls:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	# Создание нового поколения функций управления
	evolved_controls = []
	
	# Скрещивание функций управления
	try:
		evolved_controls += \
			reproduce_population(
				controls_population_rating,
				controls_evolution_parameters.reproduced_controls_number,
				controls_evolution_parameters.control_mutation_probability,
				improvement_direction
			)
	except:
		pass
		
	# Селекция функций управления
	evolved_controls += \
		select_controls(
			controls_population_rating,
			controls_evolution_parameters.selected_controls_number,
			improvement_direction
		)
		
		
	controls_arguments_space = \
		controls_population_rating.controls_population \
			.controls_arguments_space
			
	return ControlsPopulation(controls_arguments_space, evolved_controls)
	
	
	
def evolve_complex_controls_population(controls_complex_population_rating,
											controls_evolution_parameters,
											improvement_direction):
	controls_complex_population = \
		controls_complex_population_rating \
			.controls_complex_population
			
	state_space_coordinates = \
		controls_complex_population.state_space \
			.state_space_coordinates
			
			
			
	for state_space_coordinate in state_space_coordinates:
		controls_population_rating = \
			controls_complex_population_rating \
				.get_controls_population_rating(
					state_space_coordinate
				)
				
		if controls_population_rating.has_unrated_controls:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
	evolved_controls_populations = dict()
	
	for state_space_coordinate in state_space_coordinates:
		controls_population_rating = \
			controls_complex_population_rating \
				.get_controls_population_rating(
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
	