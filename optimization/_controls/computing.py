"""
"""

from optimization.utilities.singleton \
	import Singleton
	
from abc import ABCMeta, abstractproperty







class ComputingContext:
	"""
	Класс, являющийся базовым для контекстов вычислений операторов, функций и
	комплексных функций. Экземпляры данного класса предназначены для хранения
	состояния вычислений
	
	Примечания:
		1. Создание экземпляров ComputingContext (не наследников) невозможно
	"""
	
	def __new__(cls, *args, **kwargs):
		if cls is ComputingContext:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		computing_context = \
			super(ComputingContext, cls) \
				.__new__(cls, *args, **kwargs)
				
		return computing_context
		
		
		
		
		
class NoneComputingContext(Singleton, ComputingContext):
	"""
	"""
	
	pass
	
	
	
	
	
	
	
class ComputingResult(metaclass = ABCMeta):
	"""
	"""
	
	@abstractproperty
	def computing_context(self):
		pass
		
		
		
		
		
class NoneComputingResult(Singleton, ComputingResult):
	"""
	"""
	
	@property
	def computing_context(self):
		return NoneComputingContext()
		