"""
Модуль, содержащий набор классов необходимых для определения деревьев операторов
функций управления аппаратом

Примечания:
	1. Функция управления аппаратом строится в виде дерева операторов. Каждый
		узел этого дерева представляет либо некоторый оператор, либо аргумент
		функции. Узел оператора может иметь поддеревья, каждое из которых
		соответствует аргументу оператора 
"""

from abc \
	import ABCMeta, \
				abstractproperty, \
				abstractmethod
				
from mongoengine \
	import EmbeddedDocument, \
				EmbeddedDocumentField, \
				DynamicField
				
from optimization.external.noconflict import classmaker
from optimization._controls.operators import Operator
from optimization._controls.arguments import ArgumentsSpaceCoordinate







class Compound(EmbeddedDocument, metaclass = classmaker((ABCMeta,))):
	"""
	Класс, экземпляры которого представляют узлы дерева функции управления
	
	Аргументы конструктора:
		1. bindings (передается как keyword аргумент)
			Коллекция поддеревьев узла
			
			Необрабатываемые требования к передаваемым значениям:
				1. Значение должно быть Sequence-коллекцией экземпляров Compound
				
			Обрабатываемые требования к передаваемым значениям:
				1. Значение должно быть передано
				2. Совокупность всех элементов значения и их потомков не должна
					содержать дубликатов
					
	Примечания:
		1. Создание экземпляров Compound (не наследников) невозможно
		2. Экземпляры Compound являются неизменяемыми объектами
		3. Отображается на БД как встроенный документ
	"""
	
	# Настройка отображения на БД
	meta = \
		{
			'allow_inheritance': True	# Разрешено наследование
		}
		
	__bindings = \
		DynamicField(
			required = True,
			db_field = 'bindings',
			default  = None
		)
		
		
		
	def __new__(cls, *args, **kwargs):
		if cls is Compound:
			raise Exception() #!!!!! Создавать внятные исключения
			
		return super(Compound, cls).__new__(cls, *args, **kwargs)
		
		
	def __init__(self, bindings = None, *args, **kwargs):
		super(Compound, self).__init__(*args, **kwargs)
		
		
		if self.__bindings is None:
			if bindings is None:
				raise Exception() #!!!!! Создавать внятные исключения
				
			self.__bindings = bindings
			
			
		# Проверка дочерних узлов:
		# 	В структуре не должно быть дубликатов узлов
		#	(мощность множества потомков д.б. равна числу потомков.
		#	Такая проверка возможна, т.к. из множества (типа языка)
		#	удаляются дубликаты)
		child_compounds_max_height = 0
		child_compounds_number     = len(self.__bindings)
		child_compounds            = set(self.__bindings)
		
		for child_compound in self.__bindings:
			child_compounds_max_height = \
				max(
					child_compounds_max_height,
					child_compound.height
				)
				
			child_compounds_number += \
				len(child_compound.__child_compounds)
				
			child_compounds.update(
				child_compound.__child_compounds
			)
			
		if len(child_compounds) != child_compounds_number:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self.__child_compounds = frozenset(child_compounds)
		self.__height          = child_compounds_max_height + 1
		
		
		
	def __hash__(self):
		return id(self)
		
		
	def __eq__(self, obj):
		return id(self) == id(obj)
		
		
	def __ne__(self, obj):
		return id(self) != id(obj)
		
		
		
	@property
	def child_compounds(self):
		"""
		Возвращает множество дочерних узлов
		"""
		
		return self.__child_compounds
		
		
	@property
	def height(self):
		"""
		Возвращает высоту дерева
		"""
		
		return self.__height
		
		
	@property
	def bindings(self):
		"""
		Возвращает список поддеревьев
		"""
		
		return list(self.__bindings)
		
		
	@property
	def bindings_number(self):
		"""
		Возвращает число поддеревьев
		"""
		
		return len(self.__bindings)
		
		
	def __getitem__(self, binding_number):
		"""
		Возвращает поддерево, соответствующее указанному номеру связи
		
		Аргументы:
			1. binding_number
				Номер связи
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть целым числом
					
				Обрабатываемые требования к передаваемым значениям:
					1. Значение должно быть неотрицательным числом, меньшим
						числа аргументов оператора
		"""
		
		if (binding_number < 0) or (binding_number >= len(self.__bindings)):
			raise IndexError() #!!!!! Создавать внятные исключения
			
			
		return self.__bindings[binding_number]
		
		
		
		
		
		
		
class ArgumentCompound(Compound):
	"""
	Класс, экземпляры которого представляют узлы-аргументы дерева функции
	управления
	
	Аргументы конструктора:
		1. arguments_space_coordinate (передается как keyword аргумент)
			Координата пространства аргументов функций управления,
			идентифицирующая аргумент
			
			Необрабатываемые требования к передаваемым значениям:
				1. Значение должно быть экземпляром ArgumentsSpaceCoordinate
				
			Обрабатываемые требования к передаваемым значениям:
				1. Значение должно быть передано
	"""
	
	# Настройка отображения на БД
	__arguments_space_coordinate = \
		EmbeddedDocumentField(
			ArgumentsSpaceCoordinate,
			required = True,
			db_field = 'arguments_space_coordinate',
			default  = None
		)
		
		
		
	def __init__(self, arguments_space_coordinate = None, *args, **kwargs):
		super(ArgumentCompound, self).__init__([], *args, **kwargs)
		
		
		if self.__arguments_space_coordinate is None:
			if arguments_space_coordinate is None:
				raise Exception() #!!!!! Создавать внятные исключения
				
			self.__arguments_space_coordinate = arguments_space_coordinate
			
			
			
	@property
	def arguments_space_coordinate(self):
		return self.__arguments_space_coordinate
		
		
		
		
		
		
		
class OperatorCompound(Compound):
	"""
	Класс, экземпляры которого представляют узлы-операторы дерева функции
	управления
	
	Аргументы конструктора:
		1. operator (передается как keyword аргумент)
			Оператор узла
			
			Необрабатываемые требования к передаваемым значениям:
				1. Значение должно быть экземпляром Operator
				
			Обрабатываемые требования к передаваемым значениям:
				1. Значение должно быть передано
		2. bindings (передается как keyword аргумент)
			Коллекция поддеревьев узла
			
			Необрабатываемые требования к передаваемым значениям:
				1. Значение должно быть Sequence-коллекцией экземпляров Compound
				
			Обрабатываемые требования к передаваемым значениям:
				1. Значение должно быть передано
				2. Число элементов значения должно быть равно числу аргументов
					оператора
	"""
	
	# Настройка отображения на БД
	__operator = \
		EmbeddedDocumentField(
			Operator,
			required = True,
			db_field = 'operator',
			default  = None
		)
		
		
		
	def __init__(self, operator = None, bindings = None, *args, **kwargs):
		try:
			super(OperatorCompound, self).__init__(bindings, *args, **kwargs)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		if self.__operator is None:
			if (operator is None) or (bindings is None):
				raise Exception() #!!!!! Создавать внятные исключения
				
				
			self.__operator = operator
			
			# Проверка дочерних узлов:
			# 	Число узлов должно соответствовать числу аргументов оператора
			if len(bindings) != self.__operator.arguments_number:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
				
	@property
	def operator(self):
		"""
		Возвращает оператор узла
		"""
		
		return self.__operator
		