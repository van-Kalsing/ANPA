"""
Модуль, содержащий базовые классы для определения операторов, необходимых
для построения функций управления

Примечания:
	1. Оператор, представляет собой некоторую математическую функцию (например,
		сложение, умножение, sin, возведение в степень), оператор (
		например, дифференцирование, интегрирование), либо константу.
		Оператор выполняет некоторые вычисления, при этом результат может
		зависеть от переданных ему аргументов, времени, а также от внутреннего
		состояния оператора. Каждый оператор принимает фиксированное число
		аргументов
	2. При определении конкретного аппарата необходимо:
		а. Определить наследованием от Operator необходимые операторы для
			составления функций управления
		б. Если результат вычислений некоторого оператора зависит от его
			состояния, то необходимо определить наследованием от
			OperatorComputingContext контекст вычислений оператора,
			в экземплярах которого будет сохраняться информация о состоянии.
			При вычислениях, состояние передается через параметр
			computing_context (при первом вызове пердается
			NoneComputingContext), новое состояние необходимо возвращать
			в объекте результата
"""

from abc \
	import ABCMeta, \
				abstractproperty, \
				abstractmethod, \
				abstractclassmethod
				
from optimization._controls.computing \
	import ComputingContext, \
				ComputingResult
				
				
				
				
				
				
				
class OperatorComputingContext(ComputingContext):
	"""
	Класс, экземпляры которого хранят контекст вычислений оператора
	
	Примечания:
		1. Создание экземпляров OperatorComputingContext (не наследников)
			невозможно
	"""
	
	def __new__(cls, *args, **kwargs):
		if cls is OperatorComputingContext:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		operator_computing_context = \
			super(OperatorComputingContext, cls) \
				.__new__(cls, *args, **kwargs)
				
		return operator_computing_context
		
		
		
		
		
class OperatorComputingResult(ComputingResult):
	"""
	"""
	
	def __init__(self, result, computing_context):
		self.__result            = result
		self.__computing_context = computing_context
		
		
		
	@property
	def result(self):
		return self.__result
		
		
	@property
	def computing_context(self):
		return self.__computing_context
		
		
		
		
		
class Operator(metaclass = ABCMeta):
	"""
	Класс, экземпляры которого представляют операторы, используемые для
	построения функций управления
	
	Примечания:
		1. Экземпляры Operator являются неизменяемыми объектами (состояние
			сохраняется с помощью объектов класса OperatorComputingContext)
	"""
	
	@abstractclassmethod
	def create_operator(cls):
		pass
		
		
		
	@abstractproperty
	def arguments_number(self):
		"""
		Должен возвращать количество принимаемых аргументов
		
		Требования к реализации:
			1. Результат должен быть целым неотрицательным числом
			2. Все вызовы, для экземпляров одного класса-наследника, должны
				возвращать равные значения
		"""
		
		pass
		
		
		
	@abstractmethod
	def _call(self, arguments, delta_time, computing_context):
		"""
		Должен производить вычисления
		
		Требования к реализации:
			1. Результат должен быть экземпляром OperatorComputingResult, либо
				NoneComputingResult
			2. В случае отсутствия возможности произвести вычисления должен быть
				возвращен экземпляр NoneComputingResult
			3. При возвращении экземпляра OperatorComputingResult,
				computing_context, содержащийся в нем, должен корректно
				обрабатываться оператором при вычислениях
		"""
		
		pass
		
		
	def __call__(self, arguments, delta_time, computing_context):
		"""
		Производит вычисления
		
		Аргументы:
			1. arguments
				Аргументы оператора
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть Sequence-коллекцией чисел
					
				Обрабатываемые требования к передаваемым значениям:
					1. Значение должно содержать число элементов, равное числу
						принимаемых аргументов (возвращается arguments_number)
			2. delta_time
				Время прошедшее с момента последнего вызова
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть числом
					
				Обрабатываемые требования к передаваемым значениям:
					1. Значение должно быть неотрицательным
			3. computing_context
				Контекст вычислений
				
				Необрабатываемые требования к передаваемым значениям:
					1. Значение должно быть либо экземпляром
						OperatorComputingContext, либо NoneComputingContext.
						NoneComputingContext может передаваться в случае
						отсутствия у оператора состояний, либо при первом вызове
						оператора
		"""
		
		if len(arguments) != self.arguments_number:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if delta_time < 0.0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		return self._call(arguments, delta_time, computing_context)
		