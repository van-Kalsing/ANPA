"""
Модуль, содержащий класс, необходимый для предоставления базовых средств
управления аппаратом

Примечания:
	1. Управление аппаратом производится путем перевода его в некоторое
		состояние, при этом изменению подлежит только часть параметров состояния
		аппарата, образующих пространство управления.
		Новые значения изменяемых параметров вычисляются с помощью функции
		управления (ФУ). ФУ принимает цели (некоторое заданное количество) и
		текущее положение аппарата, возвращает состояние из пространства
		управления (т.о. пространство состояний ФУ должно совпадать с
		пространством управления)
	2. При определении конкретного аппарата, необходимо:
		а. Наследовать класс Navigation, реализовав, при этом, запрашиваемые
			в нем методы
"""

#!!!!! 1. Как-то избавиться от метода генерации целей.
#!!!!! 		Это не задача класса Navigation







from abc \
	import ABCMeta, \
				abstractmethod, \
				abstractproperty
				
from mongoengine                      import EmbeddedDocument
from optimization.external.noconflict import classmaker
from optimization.targets             import TargetsSourceView







class Navigation(EmbeddedDocument, metaclass = classmaker((ABCMeta,))):
	"""
	Класс, экземпляры которого предоставляют средства для управления аппаратом
	"""
	
	# Настройка отображения на БД
	meta = \
		{
			'allow_inheritance': True	# Разрешено наследование
		}
		
		
		
	@abstractproperty
	def machine(self):
		"""
		Должен возвращать аппарат, средства для управления которым
		предоставляются
		
		Требования к реализации:
			1. Результат должен быть экземпляром Machine
			2. Все вызовы, для каждого экземпляра, должны возвращать один и
				тот же объект
		"""
		
		pass
		
		
	@abstractproperty
	def targets_accounting_depth(self):
		"""
		Должен возвращать число целей учитываемых при управлении
		
		Требования к реализации:
			1. Результат должен быть целым положительным числом
			2. Все вызовы, для каждого экземпляра, должны возвращать равные
				значения
		"""
		
		pass
		
		
	@abstractproperty
	def complex_controls_arguments_space(self):
		"""
		Должен возвращать пространство аргументов функций управления
		
		Требования к реализации:
			1. Результат должен быть экземпляром ArgumentsSpace
			2. Все вызовы, для каждого экземпляра, должны возвращать равные
				значения
		"""
		
		pass
		
		
	@abstractproperty
	def complex_controls_state_space(self):
		"""
		Должен возвращать пространство состояний функций управления
		
		Требования к реализации:
			1. Результат должен быть экземпляром StateSpace
			2. Результат должен быть проекцией полного пространства состояний
				аппаратв
			3. Все вызовы, для каждого экземпляра, должны возвращать равные
				значения
		"""
		
		pass
		
		
	@abstractproperty
	def targets_state_space(self):
		"""
		Должен возвращать пространство состояний целей
		
		Требования к реализации:
			1. Результат должен быть экземпляром MetricStateSpace
			2. Результат должен быть проекцией полного пространства состояний
				аппарата
			3. Все вызовы, для каждого экземпляра, должны возвращать равные
				значения
		"""
		
		pass
		
		
		
	@abstractproperty
	def confirming_distance(self):
		"""
		Должен возвращать наибольшее расстояние от аппарата до цели, при котором
		регистрируется достижение этой цели
		
		Требования к реализации:
			1. Результат должен быть неотрицательным числом
			2. Все вызовы, для каждого экземпляра, должны возвращать равные
				значения
		"""
		
		pass
		
		
	def check_target_confirmation(self, target):
		"""
		Возвращает признак достижения аппаратом цели (True - цель достигнута,
		False - иначе)
		
		Аргументы:
			1. target
				Цель, достижение которой проверяется
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть экземпляром StateSpace
					
				Обрабатываемые требования к передаваемым значениям:
					1. Значение должно содержаться в пространстве состояний
						целей
		"""
		
		if target not in self.targets_state_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		current_state = \
			self.machine.get_current_state(
				self.targets_state_space
			)
			
		distance = \
			self.targets_state_space.compute_distance(
				current_state,
				target
			)
			
			
		return distance <= self.confirming_distance
		
		
		
	#!!!!! Костыль. Надо куда-то убрать
	@abstractmethod
	def generate_target(self):
		"""
		Должен возвращать случайную цель
		"""
		
		pass
		
		
	@abstractmethod
	def reset_machine_state(self):
		"""
		Должен переводить аппарат в исходное состояние
		"""
		
		pass
		
		
	@abstractmethod
	def _compute_complex_control_value(self,
										complex_control,
										targets_source_view):
		"""
		Должен вычислять значение переданной функции управления от текущего
		положения аппарата и переданных целей
		"""
		
		pass
		
		
	def navigate(self, complex_control, targets_source_view):
		"""
		Вычисляет значение переданной функции управления от текущего положения
		аппарата и переданных целей
		
		Аргументы:
			1. complex_control
				Функция управления, значение которой вычисляется
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть экземпляром ComplexControl
					
				Обрабатываемые требования к передаваемым значениям:
					1. Пространство состояний значения должно быть равным
						пространству состояний функций управления (возвращаемому
						complex_controls_state_space)
					2. Пространство аргументов значения должно быть равным
						пространству аргументов функций управления
						(возвращаемому complex_controls_arguments_space)
			2. targets_source_view
				Цели управления
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть экземпляром TargetsSourceView
					
				Обрабатываемые требования к передаваемым значениям:
					1. Цели должны входить в пространство состояний целей
						(возвращаемое targets_state_space)
					2. Число целей должно быть не меньше числа целей,
						учитываемых при управлении (возвращаемого
						targets_accounting_depth)
					3. Ближайшая цель не должна быть достигнутой
		"""
		
		if not self.__check_complex_control_compatibility(complex_control):
			raise Exception() #!!!!! Создавать внятные исключения
			
		if not self.__check_targets_source_view_compatibility(targets_source_view):
			raise Exception() #!!!!! Создавать внятные исключения
			
		if targets_source_view.targets_number > 0:
			is_current_target_confirmed = \
				self.check_target_confirmation(
					targets_source_view.current_target
				)
				
			if is_current_target_confirmed:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
		try:
			control_value = \
				self._compute_complex_control_value(
					complex_control,
					targets_source_view
				)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			self.machine.set_state(control_value)
			
			
			
	def __check_complex_control_compatibility(self, complex_control):
		is_complex_control_compatible = True
		
		is_complex_control_compatible &= \
			complex_control.state_space \
				== self.complex_controls_state_space
				
		is_complex_control_compatible &= \
			complex_control.arguments_space \
				== self.complex_controls_arguments_space
				
		return is_complex_control_compatible
		
		
	def __check_targets_source_view_compatibility(self, targets_source_view):
		is_targets_source_view_compatible = True
		
		is_targets_source_view_compatible &= \
			targets_source_view.targets_state_space \
				== self.targets_state_space
				
		is_targets_source_view_compatible &= \
			targets_source_view.targets_number \
				>= self.targets_accounting_depth
				
		return is_targets_source_view_compatible
		