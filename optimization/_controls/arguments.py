"""
Модуль, содержащий набор классов необходимых для описания аргументов
передаваемых функциям управления

Примечания:
	1. Каждая функция управления принимает фиксированный набор аргументов
		(экземпляр класса Arguments). Все множество принимаемых наборов образует
		пространство аргументов функции управления (экземпляр класса
		ArgumentsSpace). Каждый аргумент в наборе идентифицируется с помощью
		координаты пространства аргументов функции управления (экземпляр
		ArgumentsSpaceCoordinate)
	2. При определении конкретного аппарата необходимо:
		а. Определить наследованием от ArgumentsSpaceCoordinate координаты
			пространства аргументов функции управления
		б. Определить наследованием от ArgumentsSpace или созданием экземпляров
			CustomArgumentsSpace пространств аргументов функций управления
			аппаратом
"""

from mongoengine \
	import EmbeddedDocument, \
				EmbeddedDocumentField, \
				ListField
				
from optimization.utilities.singleton \
	import Singleton
	
from abc         import ABCMeta, abstractmethod, abstractproperty
from collections import Mapping, Iterable







class ArgumentsSpaceCoordinate(Singleton, EmbeddedDocument):
	"""
	Класс, экземпляры которого представляют координаты пространства аргументов
	функций управления
	
	Примечания:
		1. Реализует паттерн Singleton
		2. Создание экземпляров ArgumentsSpaceCoordinate (не наследников)
			невозможно
		3. Отображается на БД как встроенный документ
	"""
	
	# Настройка отображения на БД
	meta = \
		{
			'allow_inheritance': True	# Разрешено наследование
		}
		
		
		
	def __new__(cls, *args, **kwargs):
		if cls is ArgumentsSpaceCoordinate:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		arguments_space_coordinate = \
			super(ArgumentsSpaceCoordinate, cls) \
				.__new__(cls, *args, **kwargs)
				
		return arguments_space_coordinate
		
		
		
	def __hash__(self):
		"""
		Возвращает хэш
		
		Примечания:
			1. Метод добавлен для того, чтобы было возможно использование
				экземпляров ArgumentsSpaceCoordinate в качестве ключей, а также
				добавления их во множества
		"""
		
		return id(self)
		
		
	def __eq__(self, obj):
		return id(self) == id(obj)
		
		
	def __ne__(self, obj):
		return id(self) != id(obj)
		
		
		
		
		
		
		
class Arguments(Mapping):
	"""
	Класс, экземпляры которого представляют аргументы функций управления
	
	Аргументы конструктора:
		1. values
			Значения аргументов
			
			Необрабатываемые требования к передаваемым значениям:
				1. Значение должно быть Mapping-коллекцией
				2. Ключи значения должны быть экземплярами
					ArgumentsSpaceCoordinate
				3. Элементы значения не должны меняться во времени (желательно
					использование неизменяемых объектов)
					
			Обрабатываемые требования к передаваемым значениям:
				1. Значение не должно быть пустым
	"""
	
	def __init__(self, values):
		try:
			arguments_space = \
				CustomArgumentsSpace(
					values.keys()
				)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			self.__arguments_space = arguments_space
			self.__values          = dict(values)
			
			
			
	@property
	def arguments_space(self):
		"""
		Возвращает пространство аргументов функций управления, которому
		принадлежат аргументы
		"""
		
		return self.__arguments_space
		
		
		
	def __len__(self):
		"""
		Возвращает число поддерживаемых аргументами координат
		пространства аргументов функций управления
		"""
		
		return len(self.__arguments_space.arguments_space_coordinates)
		
		
	def __iter__(self):
		"""
		Возвращает объект-итератор по поддерживаемым аргументами
		координатам пространства аргументов функций управления
		"""
		
		return iter(self.__arguments_space.arguments_space_coordinates)
		
		
	def __contains__(self, arguments_space_coordinate):
		"""
		Проверяет поддерживают ли аргументы переданную координату
		пространства аргументов функций управления
		
		Аргументы:
			1. arguments_space_coordinate
				Координата пространства аргументов функций управления, проверка
				поддержки которой производится
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть экземпляром ArgumentsSpaceCoordinate
		"""
		
		contains_arguments_space_coordinate = \
			arguments_space_coordinate \
				in self.__arguments_space.arguments_space_coordinates
				
		return contains_arguments_space_coordinate
		
		
	def __getitem__(self, arguments_space_coordinate):
		"""
		Возвращает значение, соответствующее переданной координате
		пространства аргументов функций управления
		
		Аргументы:
			1. arguments_space_coordinate
				Координата пространства аргументов функций управления,
				в соответствии с которой определяется результат
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть экземпляром ArgumentsSpaceCoordinate
					
				Обрабатываемые требования к передаваемым значениям:
					1. Значение должно поддерживаться аргументами
						(предварительно можно проверить с помощью __contains__)
		"""
		
		if arguments_space_coordinate in self:
			value = self.__values[arguments_space_coordinate]
		else:
			raise KeyError() #!!!!! Создавать внятные исключения
			
		return value
		
		
		
		
		
		
		
from optimization.external.noconflict import classmaker
asd = classmaker(right_metas = (ABCMeta,))
class ArgumentsSpace(EmbeddedDocument,
						metaclass = asd):
	"""
	Класс, экземпляры которого представляют пространства аргументов функций
	управления
	
	Примечания:
		1. Экземпляры считаются равными, если содержат равные множества
			координат пространства аргументов функций управления
		2. Отображается на БД как встроенный документ
	"""
	
	
	
	# Настройка отображения на БД
	meta = \
		{
			'allow_inheritance': True	# Разрешено наследование
		}
		
		
		
	@abstractproperty
	def _arguments_space_coordinates(self):
		"""
		Должен возвращать множество координат пространства аргументов функций
		управления
		
		Требования к реализации:
			1. Результат должен быть Iterable-коллекцией
			2. Результат должен содержать экземпляры ArgumentsSpaceCoordinate
			3. Все вызовы метода должны возвращать равные результаты
				(с точностью до порядка элементов)
		"""
		
		pass
		
		
	@property
	def arguments_space_coordinates(self):
		"""
		Возвращает множество координат пространства аргументов функций
		управления
		
		Примечания:
			1. Результат получается преобразованием к типу frozenset,
				значения возвращаемого _arguments_space_coordinates
		"""
		
		return frozenset(self._arguments_space_coordinates)
		
		
		
	# Сравнение пространств аргументов функций управления
	def __lt__(self, arguments_space):
		result = \
			self.arguments_space_coordinates.__lt__(
				arguments_space.arguments_space_coordinates
			)
			
		return result
		
		
	def __le__(self, arguments_space):
		result = \
			self.arguments_space_coordinates.__le__(
				arguments_space.arguments_space_coordinates
			)
			
		return result
		
		
	def __eq__(self, arguments_space):
		result = \
			self.arguments_space_coordinates.__eq__(
				arguments_space.arguments_space_coordinates
			)
			
		return result
		
		
	def __ne__(self, arguments_space):
		result = \
			self.arguments_space_coordinates.__ne__(
				arguments_space.arguments_space_coordinates
			)
			
		return result
		
		
	def __gt__(self, arguments_space):
		result = \
			self.arguments_space_coordinates.__gt__(
				arguments_space.arguments_space_coordinates
			)
			
		return result
		
		
	def __ge__(self, arguments_space):
		result = \
			self.arguments_space_coordinates.__ge__(
				arguments_space.arguments_space_coordinates
			)
			
		return result
		
		
		
	# Принадлежность аргументов функций управления пространству
	def __contains__(self, arguments):
		"""
		Проверяет принадлежность переданных аргументов пространству аргументов
		функций управления
		
		Аргументы:
			1. arguments
				Аргументы принадлежность пространству аргументов функций
				управления которых проверяется
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть экземпляром Arguments
		"""
		
		return self == arguments.arguments_space
		
		
		
		
		
class CustomArgumentsSpace(ArgumentsSpace):
	"""
	Класс, экземпляры которого представляют пространства аргументов функций
	управления, список координат которого задается при создании
	
	Аргументы конструктора:
		1. arguments_space_coordinates (передается как keyword аргумент)
			Координаты пространства аргументов функций управления
			
			Необрабатываемые требования к передаваемым значениям:
				1. Значение должно быть Iterable-коллекцией экземпляров
					ArgumentsSpaceCoordinate
					
			Обрабатываемые требования к передаваемым значениям:
				1. Значение должно быть передано
	"""
	
	# Настройка отображения на БД
	__arguments_space_coordinates = \
		ListField(
			EmbeddedDocumentField(ArgumentsSpaceCoordinate),
			required = True,
			db_field = 'arguments_space_coordinates',
			default  = None
		)
		
		
		
	def __init__(self, *args, **kwargs):
		super(CustomArgumentsSpace, self).__init__(*args, **kwargs)
		
		if self.__arguments_space_coordinates is None:
			if 'arguments_space_coordinates' not in kwargs:
				raise Exception() #!!!!! Создавать внятные исключения
				
			self.__arguments_space_coordinates = \
				list(
					kwargs[arguments_space_coordinates]
				)
				
				
				
	@property
	def _arguments_space_coordinates(self):
		"""
		Возвращает множество координат пространства аргументов функций
		управления
		
		Примечания:
			1. Список содержащий координаты пространства не копируется, т.к.
				в дальнейшем он будет преобразован к frozenset базовым классом
		"""
		
		return self.__arguments_space_coordinates
		