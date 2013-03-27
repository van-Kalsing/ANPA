from collections import Set, Iterator

import random



class ControlsPopulation(Set):
	def __init__(self, controls, controls_ages = None):
		#!!!!! Проверка функций управления
		controls      = frozenset(controls)
		# controls_ages = \
			# dict(
				# [(control, 0) for control in controls]
			# )
			
			
		# Реализация интерфейса множества
		self.__contains__ = \
			lambda self, control: control in controls
			
		self.__len__ = \
			lambda self: len(controls)
			
			
		# Костыль, введенный потому, что Python
		# 	не хочет принимать присвоенный на лету метод __iter__
		self.get_iterator = \
			lambda : iter(controls)
			
		# def get_control_age(self, control):
			# if control in controls:
				# control_age = controls_ages[control]
			# else:
				# raise Exception() #!!!!! Создавать внятные исключения
				
			# return control_age
			
		# self.get_control_age = get_control_age
	def __contains__(self, control):
		pass
		
	def __iter__(self):
		return self.get_iterator()
		
	def __len__(self):
		pass
class EvolvedControlPopulation:
	pass
class ControlOptimizer:
	def __init__(self,
					control_factory,
					selected_controls_number,
					reproduced_controls_number,
					control_mutation_probability,
					control_tests_number):
		self.control_factory              = control_factory
		self.selected_controls_number     = selected_controls_number
		self.reproduced_controls_number   = reproduced_controls_number
		self.control_mutation_probability = control_mutation_probability
		self.control_tests_number         = control_tests_number
		
		self.untested_controls = \
			[(generated_control, []) for generated_control
				in self.generate_controls(selected_controls_number + reproduced_controls_number)]
		self.tested_controls = []
		self.test_control    = self.untested_controls.pop(0)
		
		
	def has_untested_controls(self):
		return bool(self.untested_controls)
	def get_test_control(self):
		test_control, test_control_results = self.test_control
		
		return test_control
		
	def set_test_control_result(self, test_control_result):
		# Сохранение результатов тестируемой функции управления
		test_control, test_control_results = \
			self.test_control
			
		test_control_results.append(test_control_result)
		
		if len(test_control_results) == self.control_tests_number:
			# Вычисление среднего результата тестируемой функции управления
			test_control_results = \
				[test_control_result for test_control_result in test_control_results
					if test_control_result is not None]
					
			if test_control_results:
				test_control_result = sum(test_control_results)
			else:
				test_control_result = None
				
			self.tested_controls.append((test_control, test_control_result))
		else:
			self.untested_controls.append((test_control, test_control_results))
			
			
		# Создание нового поколения функций управления
		if not self.untested_controls:
			untested_controls = []
			
			try:
				# Скрещивание функций управления
				untested_controls += \
					self.reproduce_controls(
						self.tested_controls,
						self.reproduced_controls_number,
						self.control_mutation_probability
					)
			except:
				# Генерация случайных функций управления,
				# 	т.к. отсутствуют функции пригодные для скрещивания
				untested_controls += \
					self.generate_controls(self.reproduced_controls_number)
					
			# Селекция функций управления
			untested_controls += \
				self.select_controls(
					self.tested_controls,
					self.selected_controls_number
				)
				
				
			self.tested_controls   = []
			self.untested_controls = \
				[(untested_control, []) for untested_control in untested_controls]
				
				
		# Выбор новой тестируемой функции управления
		untested_control_number = \
			random.randint(0, len(self.untested_controls) - 1)
			
		self.test_control = self.untested_controls.pop(untested_control_number)
		
		
		
	# Генерация случайных функций управления
	def generate_controls(self, controls_number):
		controls = []
		
		while len(controls) < controls_number:
			controls.append(
				self.control_factory()
			)
			
		return controls
		
	# Отбор функций управления
	def select_controls(self, tested_controls, controls_number):
		def measure_control(tested_control):
			_, tested_control_result = tested_control
			
			if tested_control_result is None:
				tested_control_result = 0.0
				#!!!!! Добавить позже
				#else:
				#	tested_control_result = abs(tested_control_result)
				
			return tested_control_result
			
			
		controls = sorted(tested_controls, key = measure_control, reverse = True)
		controls = \
			[control for control, control_result in controls
				if control_result is not None]
				
		if len(controls) < controls_number:
			controls += \
				self.generate_controls(
					controls_number - len(controls)
				)
		else:
			controls = controls[0:controls_number]
			
		return controls
		
	# Скрещивание функций управления
	def reproduce_controls(self,
								tested_controls,
								reproduced_controls_number,
								control_mutation_probability):
		# Фильтрация работоспособных функций управления
		tested_controls = \
			[(control, control_result) for control, control_result in tested_controls
				if control_result is not None]
				
				
		# Число родительских функций управления
		controls_number = len(tested_controls)
		
		if controls_number == 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
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
			
			
		# Определение наихудшего и наилучшего результатов
		_, min_control_result = tested_controls[0]
		_, max_control_result = tested_controls[0]
		total_controls_result  = 0.0
		
		for _, controls_result in tested_controls[1:]:
			if controls_result < min_control_result:
				min_control_result = controls_result
				
			if controls_result > max_control_result:
				max_control_result = controls_result
				
			total_controls_result += controls_result
			
		total_controls_result -= controls_number * min_control_result
		
		
		
		# Вычисление вероятностей функций управления стать родителем
		controls_probability_distribution = []
		
		if min_control_result == max_control_result:
			# Равномерное распределение вероятностей
			control_probability = 1.0 / controls_number
			
			for control, _ in tested_controls:
				controls_probability_distribution.append(
					(control, control_probability)
				)
		else:
			# Вероятность пропорциональна вкладу функции в общую сумму
			for control, control_result in tested_controls:
				control_probability = \
					(control_result - min_control_result) \
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
		