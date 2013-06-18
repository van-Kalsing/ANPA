from optimization._controls.computing \
	import NoneComputingContext, \
				NoneComputingResult
				
from optimization._controls.operators \
	import Operator, \
				OperatorComputingContext, \
				OperatorComputingResult \
				
from operator    import add, mul
from math        import pow, sin
from mongoengine import FloatField
from random      import uniform





#!!!!! Временно. Убрать в конфигурационный файл
lower_constant_limit = -10.0
upper_constant_limit =  10.0





class ConstantOperator(Operator):
	__constant = \
		FloatField(
			required = True,
			db_field = 'constant',
			default  = None
		)
		
		
		
	def __init__(self, *args, **kwargs):
		super(ConstantOperator, self).__init__(*args, **kwargs)
		
		if self.__constant is None:
			self.__constant = \
				uniform(
					lower_constant_limit,
					upper_constant_limit
				)
				
				
	@classmethod
	def create_operator(cls):
		return ConstantOperator()
		
		
		
	@property
	def arguments_number(self):
		return 0
		
		
		
	def _call(self, arguments, delta_time, computing_context):
		result = \
			OperatorComputingResult(
				self.__constant,
				NoneComputingContext()
			)
			
		return result
		
		
		
		
		
class AdditionOperator(Operator):
	@classmethod
	def create_operator(cls):
		return AdditionOperator()
		
		
		
	@property
	def arguments_number(self):
		return 2
		
		
		
	def _call(self, arguments, delta_time, computing_context):
		try:
			result = \
				OperatorComputingResult(
					add(*arguments),
					NoneComputingContext()
				)
		except:
			result = NoneComputingResult()
			
		return result
		
		
		
		
		
class MultiplicationOperator(Operator):
	@classmethod
	def create_operator(cls):
		return MultiplicationOperator()
		
		
		
	@property
	def arguments_number(self):
		return 2
		
		
		
	def _call(self, arguments, delta_time, computing_context):
		try:
			result = \
				OperatorComputingResult(
					mul(*arguments),
					NoneComputingContext()
				)
		except:
			result = NoneComputingResult()
			
		return result
		
		
		
		
		
class PowerOperator(Operator):
	@classmethod
	def create_operator(cls):
		return PowerOperator()
		
		
		
	@property
	def arguments_number(self):
		return 2
		
		
		
	def _call(self, arguments, delta_time, computing_context):
		try:
			result = \
				OperatorComputingResult(
					pow(*arguments),
					NoneComputingContext()
				)
		except:
			result = NoneComputingResult()
			
		return result
		
		
		
		
		
class SinusOperator(Operator):
	@classmethod
	def create_operator(cls):
		return SinusOperator()
		
		
		
	@property
	def arguments_number(self):
		return 1
		
		
		
	def _call(self, arguments, delta_time, computing_context):
		try:
			result = \
				OperatorComputingResult(
					sin(*arguments),
					NoneComputingContext()
				)
		except:
			result = NoneComputingResult()
			
		return result
		