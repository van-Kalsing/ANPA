"""
"""

from optimization.controls.arguments \
	import ArgumentsSpace, \
				CustomArgumentsSpace
				
from optimization.controls.compounds \
	import Compound, \
				ArgumentCompound, \
				OperatorCompound
				
from optimization.controls.computing \
	import ComputingContext, \
				ComputingResult, \
				NoneComputingContext, \
				NoneComputingResult
				
from optimization.machine import StateSpaceCoordinate, CustomStateSpace, State







class ControlComputingContext(ComputingContext):
	"""
	Примечания:
		1. Не проверяется соответсвие контекста некоторой функции управления,
			поэтому возможно создание контекста ссылающегося на узлы
			принадлежащие нескольким функциям управления, либо не на все узлы
			одной функции управления.
			Соответсвие контекста функции управления проверяется при вычислении
			самой функцией управления
	"""
	
	def __init__(self, computing_contexts):
		super(ControlComputingContext, self).__init__()
		
		self.__computing_contexts = dict(computing_contexts)
		self.__compounds          = \
			frozenset(
				self.__computing_contexts.keys()
			)
			
			
			
	@property
	def compounds(self):
		return self.__compounds
		
		
		
	def __getitem__(self, compound):
		if compound not in self.__compounds:
			raise KeyError() #!!!!! Создавать внятные исключения
			
		return self.__computing_contexts[compound]
		
		
		
		
		
class ControlComputingResult(ComputingResult):
	def __init__(self, result, computing_context):
		super(ControlComputingResult, self).__init__()
		
		self.__result            = result
		self.__computing_context = computing_context
		
		
		
	@property
	def result(self):
		return self.__result
		
		
	@property
	def computing_context(self):
		return self.__computing_context
		
		
		
		
		
class Control:
	"""
	Класс, экземпляры которого представляют функции управления аппаратом
	"""
	
	def __init__(self,
					root_compound,
					arguments_space):
		super(Control, self).__init__()
		
		
		self.__root_compound   = root_compound
		self.__arguments_space = arguments_space
		
		
		# Составление списка узлов
		compounds = \
			{self.__root_compound} \
				.union(self.__root_compound.child_compounds)
				
				
		# Составление списка обрабатываемых аргументов
		# и подсчет количества узлов-операторов
		arguments_space_coordinates = set()
		operator_compounds_number   = 0
		
		for compound in compounds:
			if isinstance(compound, ArgumentCompound):
				arguments_space_coordinates.add(
					compound.arguments_space_coordinate
				)
				
			elif isinstance(compound, OperatorCompound):
				operator_compounds_number += 1
				
			else:	# Закрытая ветвь
				raise Exception() #!!!!! Создавать внятные исключения
				
				
		self.__compounds                 = frozenset(compounds)
		self.__operator_compounds_number = operator_compounds_number
		
		
		# Проверка дерева функции управления:
		# 	Не должно быть аргументов, координата которых не входит в
		# 	пространство аргументов функции управления
		arguments_space = CustomArgumentsSpace(arguments_space_coordinates)
		
		if not arguments_space <= self.__arguments_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
	@property
	def root_compound(self):
		return self.__root_compound
		
		
	@property
	def compounds(self):
		return self.__compounds
		
		
	@property
	def arguments_space(self):
		return self.__arguments_space
		
		
	@property
	def height(self):
		return self.__root_compound.height
		
		
		
	def __call__(self, arguments, delta_time, computing_context):
		computing_contexts = dict()
		
		
		def compute(compound):
			if isinstance(compound, ArgumentCompound):
				result = \
					arguments[
						compound.arguments_space_coordinate
					]
					
					
			elif isinstance(compound, OperatorCompound):
				operator_arguments = \
					[compute(child_compound) for child_compound
						in compound.bindings]
						
				if None in operator_arguments:
					result = None
				else:
					if computing_context == NoneComputingContext():
						operator_computing_context = NoneComputingContext()
					elif compound in computing_context:
						operator_computing_context = \
							computing_context[
								compound
							]
					else:
						raise Exception() #!!!!! Создавать внятные исключения
						
						
					computing_result = \
						compound.operator(
							operator_arguments,
							delta_time,
							operator_computing_context
						)
						
					if computing_result != NoneComputingResult():
						result = computing_result.result
						
						computing_contexts[compound] = \
							computing_result.computing_context
					else:
						result = None
						
						
			else:	# Закрытая ветвь
				raise Exception() #!!!!! Создавать внятные исключения
				
				
			return result
			
			
			
		if computing_context != NoneComputingContext():
			operator_compounds_number = self.__operator_compounds_number
			
			if len(computing_context.compounds) != operator_compounds_number:
				raise Exception() #!!!!! Создавать внятные исключения
				
		if arguments not in self.__arguments_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if delta_time < 0.0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		try:
			result = compute(self.__root_compound)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			if result is None:
				computing_result = NoneComputingResult()
			else:
				computing_result = \
					ControlComputingResult(
						result,
						ControlComputingContext(computing_contexts)
					)
					
			return computing_result
			
			
			
			
			
			
			
class ComplexControlComputingContext(ComputingContext):
	def __init__(self, computing_contexts):
		super(ComplexControlComputingContext, self).__init__()
		
		self.__computing_contexts = dict(computing_contexts)
		self.__controls           = \
			frozenset(
				self.__computing_contexts.keys()
			)
			
			
		if len(self.__controls) == 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
	@property
	def controls(self):
		return self.__controls
		
		
		
	def __getitem__(self, control):
		if control not in self.__controls:
			raise KeyError() #!!!!! Создавать внятные исключения
			
		return self.__computing_contexts[control]
		
		
		
		
		
class ComplexControlComputingResult(ComputingResult):
	def __init__(self, result, computing_context):
		super(ComplexControlComputingResult, self).__init__()
		
		self.__result            = result
		self.__computing_context = computing_context
		
		
		
	@property
	def result(self):
		return self.__result
		
		
	@property
	def computing_context(self):
		return self.__computing_context
		
		
		
		
		
class ComplexControl:
	def __init__(self, controls_map):
		super(ComplexControl, self).__init__()
		
		
		
		self.__controls_map = dict(controls_map)
		
		
		
		# Проверка функций управления:
		# 	Все функции управления должны иметь одно пространство аргументов
		arguments_space = None
		
		for state_space_coordinate in self.__controls_map:
			control = self.__controls_map[state_space_coordinate]
			
			if arguments_space is None:
				arguments_space = control.arguments_space
			else:
				if arguments_space != control.arguments_space:
					raise Exception() #!!!!! Создавать внятные исключения
					
					
					
		# Проверка функций управления:
		# 	Должна присутствовать хотя бы одна функция управления
		if not self.__controls_map:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		# Приведение словаря к списковому представлению
		state_space_coordinates = []
		controls                = []
		
		
		for state_space_coordinate in self.__controls_map:
			state_space_coordinates.append(state_space_coordinate)
			
			controls.append(
				self.__controls_map[state_space_coordinate]
			)
			
			
		self.__state_space_coordinates = frozenset(state_space_coordinates)
		self.__state_space = \
			CustomStateSpace(
				state_space_coordinates
			)
			
		self.__controls        = frozenset(controls)
		self.__arguments_space = \
			controls[0].arguments_space
			
			
			
	@property
	def state_space(self):
		return self.__state_space
		
		
	@property
	def arguments_space(self):
		return self.__arguments_space
		
		
		
	def __getitem__(self, state_space_coordinate):
		if state_space_coordinate not in self.__state_space_coordinates:
			raise KeyError() #!!!!! Создавать внятные исключения
			
			
		return self.__controls_map[state_space_coordinate]
		
		
		
	def __call__(self, arguments, delta_time, computing_context):
		"""
		Примечания:
			1. Проверка аргументов arguments и delta_time происходит косвенно,
				при передаче их в функции управления
		"""
		
		if computing_context != NoneComputingContext():
			# Проверка контекста:
			# 	Множества функций управления контекста вычислений и комплексной
			#	функции управления должны совпадать
			if self.__controls != computing_context.controls:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
		computing_results  = dict()
		computing_contexts = dict()
		
		try:
			for state_space_coordinate in self.__state_space_coordinates:
				control = self.__controls_map[state_space_coordinate]
				
				control_computing_context = \
					computing_context[control] \
						if   computing_context != NoneComputingContext() \
						else NoneComputingContext()
						
						
				computing_result = \
					control(
						arguments,
						delta_time,
						control_computing_context
					)
					
				if computing_result == NoneComputingResult():
					computing_results[state_space_coordinate] = \
						NoneComputingResult()
						
					computing_contexts[control] = NoneComputingContext()
				else:
					computing_results[state_space_coordinate] = \
						computing_result.result
						
					computing_contexts[control] = \
						computing_result.computing_context
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			if NoneComputingResult() in computing_results.values():
				computing_result = NoneComputingResult()
			else:
				computing_result = \
					ComplexControlComputingResult(
						State(computing_results),
						ComplexControlComputingContext(computing_contexts)
					)
					
			return computing_result
			