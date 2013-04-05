"""
Модуль, содержащий набор классов, необходимых для описания
конкретного аппарата, синтезирование / оптимизация функций управления
которым должны быть проведены

Примечания:
	1. Предполагается, что аппарат в каждый момент времени может быть охарактеризован
		некоторым состоянием (класс State) - вектором параметров аппарата.
		Состояния, состав параметров которых один и тот же, объединяются
		во множества состояний - пространства состояний (класс StateSpace и
		его наследники). Для указания конкретных параметров состояния используются
		координаты пространств состояний (класс StateSpaceCoordinate)
	2. При определении конкретного аппарата, необходимо:
		а. Определить, наследованием от StateSpaceCoordinate, координаты
			пространства состояний аппарата. Наследники могут не иметь никаких
			дополнительных членов, так как основным предназначением экземпляров
			StateSpaceCoordinate является ссылка на параметры аппарата.
		б. Определить пространства состояний (наследованием от StateSpace и
			MetricStateSpace). Данный пункт может быть опущен, так как возможно
			формирование пространств состояний, созданием экземпляров
			CustomStateSpace
		в. Наследовать класс Machine, реализовав, при этом, запрашиваемые
			в нем методы.
"""

from abc         import ABCMeta, abstractmethod, abstractproperty
from collections import Mapping, Iterable





class StateSpaceCoordinate(object):
	"""
	Класс, экземпляры которого представляют координаты пространства
	состояний аппарата
	
	Примечания:
		1. Реализует паттерн Singleton (реализуется для наследников класса)
	"""
	
	def __new__(state_space_coordinate_class, *args, **kwargs):
		"""
		Реализует паттерн Singleton
		
		Примечания:
			1. Для каждого наследующего класса создается единственный объект,
				который возвращается при попытке создания нового объекта
			2. Создание экземпляров StateSpaceCoordinate невозможно
		"""
		
		if state_space_coordinate_class is StateSpaceCoordinate:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		try:
			instance = state_space_coordinate_class.__instance
		except AttributeError:
			instance = None
		else:
			if type(instance) is not state_space_coordinate_class:
				instance = None
				
		if instance is None:
			instance = \
				super(StateSpaceCoordinate, state_space_coordinate_class) \
					.__new__(state_space_coordinate_class, *args, **kwargs)
					
			state_space_coordinate_class.__instance = instance
			
		return instance
		
		
		
		
		
class State(Mapping, Iterable):
	"""
	Класс, экземпляры которого представляют состояния аппарата
	
	Аргументы конструктора:
		1. values
			Значения состояния
			
			Необрабатываемые требования к передаваемым значениям:
				1. Значение должно быть Mapping-коллекцией
				2. Ключи значения должны быть экземплярами StateSpaceCoordinate
				3. Элементы значения не должны меняться во времени (желательно
					использование неизменяемых объектов)
					
			Обрабатываемые требования к передаваемым значениям:
				1. Значение не должно быть пустым
	"""
	
	def __init__(self, values):
		try:
			state_space = \
				CustomStateSpace(
					values.keys()
				)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			self.__state_space = state_space
			self.__values      = dict(values)
			
			
			
	@property
	def state_space(self):
		"""
		Возвращает пространство состояний, которому принадлежит состояние
		"""
		
		return self.__state_space
		
		
		
	def __len__(self):
		"""
		Возвращает число поддерживаемых состоянием координат
		пространства состояний
		"""
		
		return len(self.__state_space.state_space_coordinates)
		
		
	def __iter__(self):
		"""
		Возвращает объект-итератор по поддерживаемым состоянием
		координатам пространства состояний
		"""
		
		return iter(self.__state_space.state_space_coordinates)
		
		
	def __contains__(self, state_space_coordinate):
		"""
		Проверяет поддерживает ли состояние переданную координату
		пространства состояний
		
		Аргументы:
			1. state_space_coordinate
				Координата пространства состояний, проверка поддержки
				которой производится
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть экземпляром StateSpaceCoordinate
		"""
		
		contains_state_space_coordinate = \
			state_space_coordinate \
				in self.__state_space.state_space_coordinates
				
		return contains_state_space_coordinate
		
		
	def __getitem__(self, state_space_coordinate):
		"""
		Возвращает значение, соответствующее переданной координате
		пространства состояний
		
		Аргументы:
			1. state_space_coordinate
				Координата пространства состояний, в соответствии с которой
				определяется результат
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть экземпляром StateSpaceCoordinate
					
				Обрабатываемые требования к передаваемым значениям:
					1. Значение должно поддерживаться состоянием (предварительно
						можно проверить методом __contains__)
		"""
		
		if state_space_coordinate in self:
			value = self.__values[state_space_coordinate]
		else:
			raise KeyError() #!!!!! Создавать внятные исключения
			
		return value
		
		
		
class StateSpace(object):
	"""
	Класс, экземпляры которого представляют пространства состояний аппарата
	
	Примечания:
		1. Экземпляры могут содержать не полный набор координат пространства
			состояний аппарата, а описывать его некоторую проекцию
		2. Экземпляры считаются равными, если содержат равные
			множества координат пространства состояний
	"""
	
	__metaclass__ = ABCMeta
	
	
	
	@abstractproperty
	def _state_space_coordinates(self):
		"""
		Должен возвращать множество координат пространства состояний
		
		Требования к реализации:
			1. Результат должен быть Iterable-коллекцией
			2. Результат должен содержать экземпляры StateSpaceCoordinate
			3. Результат не должен меняться во времени
			4. Результат не должен быть пустым
			5. Все вызовы метода должны возвращать равные результаты
				(с точностью до порядка элементов)
		"""
		
		pass
		
		
	@property
	def state_space_coordinates(self):
		"""
		Возвращает множество координат пространства состояний
		
		Примечания:
			1. Результат имеет тип frozenset
		"""
		
		return frozenset(self._state_space_coordinates)
		
		
		
	# Сравнение пространств состояний
	def __lt__(self, state_space):
		result = \
			self.state_space_coordinates.__lt__(
				state_space.state_space_coordinates
			)
			
		return result
		
		
	def __le__(self, state_space):
		result = \
			self.state_space_coordinates.__le__(
				state_space.state_space_coordinates
			)
			
		return result
		
		
	def __eq__(self, state_space):
		result = \
			self.state_space_coordinates.__eq__(
				state_space.state_space_coordinates
			)
			
		return result
		
		
	def __ne__(self, state_space):
		result = \
			self.state_space_coordinates.__ne__(
				state_space.state_space_coordinates
			)
			
		return result
		
		
	def __gt__(self, state_space):
		result = \
			self.state_space_coordinates.__gt__(
				state_space.state_space_coordinates
			)
			
		return result
		
		
	def __ge__(self, state_space):
		result = \
			self.state_space_coordinates.__ge__(
				state_space.state_space_coordinates
			)
			
		return result
		
		
		
	# Принадлежность состояния аппарата пространству
	def __contains__(self, state):
		"""
		Проверяет принадлежность переданного состояния пространству состояний
		
		Аргументы:
			1. state
				Состояние принадлежность пространству состояний
				которого проверяется
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть экземпляром State
		"""
		
		return self == state.state_space
		
		
		
class CustomStateSpace(StateSpace):
	"""
	Класс, экземпляры которого представляют пространства состояний аппарата,
	список координат которого задается при создании
	
	Аргументы конструктора:
		1. state_space_coordinates
			Координаты пространства состояний
			
			Необрабатываемые требования к передаваемым значениям:
				1. Значение должно быть Iterable-коллекцией
				2. Элементы значения должны быть экземплярами StateSpaceCoordinate
				
			Обрабатываемые требования к передаваемым значениям:
				1. Значение не должно быть пустым
	"""
	
	def __init__(self, state_space_coordinates):
		self.__state_space_coordinates = frozenset(state_space_coordinates)
		
		if len(self.__state_space_coordinates) == 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
	@property
	def _state_space_coordinates(self):
		"""
		Возвращает множество координат пространства состояний
		"""
		
		return self.__state_space_coordinates
		
		
		
class MetricStateSpace(StateSpace):
	"""
	Класс, экземпляры которого представляют пространства состояний аппарата,
	на которых задана метрика
	"""
	
	__metaclass__ = ABCMeta
	
	
	
	@abstractmethod
	def _compute_distance(self, first_state, second_state):
		"""
		Должен возвращать расстояние между двумя состояниями пространства состояний
		
		Требования к реализации:
			1. Для любых принимаемых состояний должен быть получен результат
			2. Результат должен быть неотрицательным числом
			3. Для равных состояний, результат должен равняться 0
			4. Смена порядка состояний не должна приводить к изменению результата
			5. Для равных пар, результат не должен меняться (в том числе во времени)
		"""
		
		pass
		
		
	def compute_distance(self, first_state, second_state):
		"""
		Возвращает расстояние между двумя состояниями пространства состояний
		
		Аргументы:
			1. first_state
			2. second_state
				Состояния между которыми вычисляется расстояние.
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значения должны быть экземплярами State
					
				Обрабатываемые требования к передаваемым значениям:
					1. Значения должны принадлежать пространству состояний
		"""
		
		if first_state not in self or second_state not in self:
			raise Exception() #!!!!! Создавать внятные исключения
			
		return self._compute_distance(first_state, second_state)
		
		
		
		
		
class Machine(object):
	"""
	Класс, экземпляры которого (наследников класса) представляют аппарат,
	управление которого должно быть синтезировано / оптимизировано
	"""
	
	__metaclass__ = ABCMeta
	
	
	
	@abstractproperty
	def _full_state_space(self):
		"""
		Должен возвращать полное пространство состояний аппарата -
		такое пространство состояний, которое описывает все рассматриваемые
		параметры аппарата (представленные координатами)
		
		Требования к реализации:
			1. Результат должен быть экземпляром StateSpace
			2. Возвращаемые результаты для каждого экземпляра должны быть равными
		"""
		
		pass
		
		
		
	@abstractmethod
	def _get_current_state(self, state_space):
		"""
		Должен возвращать проекцию текущего состояния аппарата на
		переданное пространство состояний
		
		Требования к реализации:
			1. Результат должен быть экземпляром State
			2. Пространство состояний результата должно быть равно state_space
		"""
		
		pass
		
		
	def get_current_state(self, state_space):
		"""
		Возвращает проекцию текущего состояния аппарата на переданное
		пространство состояний
		
		Аргументы:
			1. state_space
				Пространство состояний, на которое осуществляется проекция
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть экземпляром StateSpace
		"""
		
		if not state_space <= self._full_state_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
		return self._get_current_state(state_space)
		
		
		
	@abstractmethod
	def _set_state(self, state):
		"""
		Должен переводить аппарат в переданное состояние
		"""
		
		pass
		
		
	def set_state(self, state):
		"""
		Переводит аппарат в переданное состояние
		
		Аргументы:
			1. state
				Состояние в которое требуется перевести аппарат
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть экземпляром State
					
				Обрабатываемые требования к передаваемым значениям:
					1. Пространство состояний значения должно быть проекцией
						полного пространства состояний аппарата
		"""
		
		if not state.state_space <= self._full_state_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
		self._set_state(state)
		