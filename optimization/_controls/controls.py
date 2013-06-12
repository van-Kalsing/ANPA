"""
"""

from mongoengine \
	import Document, \
				EmbeddedDocumentField
				
from optimization._controls.arguments \
	import ArgumentsSpace, \
				CustomArgumentsSpace
			
from optimization._controls.compound \
	import Compound, \
				ArgumentCompound, \
				OperatorCompound
				
from optimization._controls.computing \
	import ComputingContext, \
				ComputingResult, \
				NoneComputingContext, \
				NoneComputingResult
				
				
				
				
				
				
				
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
			
			
		if len(self.__compounds) == 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
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
		
		
		
		
		
class Control(Document):
	"""
	Класс, экземпляры которого представляют функции управления аппаратом
	"""
	
	# Настройка отображения на БД
	meta = \
		{
			'collection': 'controls'	# Коллекция controls
		}
		
		
	__root_compound = \
		EmbeddedDocumentField(
			Compound,
			required = True,
			db_field = 'root_compound',
			default  = None
		)
		
		
	__arguments_space = \
		EmbeddedDocumentField(
			ArgumentsSpace,
			required = True,
			db_field = 'arguments_space',
			default  = None
		)
		
		
		
	def __init__(self, *args, **kwargs):
		super(Control, self).__init__(*args, **kwargs)
		
		
		if self.__root_compound is None:
			if 'root_compound' not in kwargs:
				raise Exception() #!!!!! Создавать внятные исключения
				
			if 'arguments_space' not in kwargs:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
			self.__root_compound   = kwargs['root_compound']
			self.__arguments_space = kwargs['arguments_space']
			
			
		# Составление списка узлов
		compounds = \
			{self.__root_compound} \
				.update(self.__root_compound.child_compounds)
				
				
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
					if computing_context is NoneComputingContext():
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
						
					if computing_result is not NoneComputingResult():
						result = computing_result.result
						
						computing_contexts[compound] = \
							computing_result.computing_context
					else:
						result = None
						
						
			else:	# Закрытая ветвь
				raise Exception() #!!!!! Создавать внятные исключения
				
				
			return result
			
			
			
		if len(computing_context.compounds) != self.__operator_compounds_number:
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
		
		
		
		
		
class ComplexControl(Document):
	# Настройка отображения на БД
	meta = \
		{
			'collection': 'complex_controls'	# Коллекция complex_controls
		}
		
		
	__controls_db_view = \
		DynamicField(
			required = True,
			db_field = 'controls',
			default  = None
		)
		
		
		
	def __init__(self, *args, **kwargs):
		super(ComplexControl, self).__init__(*args, **kwargs)
		
		
		if self.__controls_db_view is not None:
			# Восстановление словаря из спискового представления
			self.__controls = dict()
			
			for (state_space_coordinate, control) in self.__controls_db_view:
				self.__controls[state_space_coordinate] = control
		else:
			if 'controls' not in kwargs:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
			self.__controls = dict(kwargs['controls'])
			
			# Проверка функций управления:
			# 	Все функции управления должны иметь одно пространство аргументов
			arguments_space = None
			
			for state_space_coordinate in self.__controls:
				control = self.__controls[state_space_coordinate]
				
				if arguments_space is None:
					arguments_space = control.arguments_space
				else:
					if arguments_space != control.arguments_space:
						raise Exception() #!!!!! Создавать внятные исключения
						
			# Проверка функций управления:
			# 	Должна присутствовать хотя бы одна функция управления
			if len(self.__controls) == 0:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
			# Приведение словаря к списковому представлению
			self.__controls_db_view = []
			
			for state_space_coordinate in self.__controls:
				control = self.__controls[state_space_coordinate]
				
				self.__controls_db_view.append(
					[state_space_coordinate, control]
				)
				
				
		self.__state_space = \
			CustomStateSpace(
				self.__controls.keys()
			)
			
		self.__arguments_space = \
			list(self.__controls.values())[0] \
				.arguments_space
				
				
				
	@property
	def state_space(self):
		return self.__state_space
		
		
	@property
	def arguments_space(self):
		return self.__arguments_space
		
		
		
	def __getitem__(self, state_space_coordinate):
		state_space_coordinates = \
			self.__state_space.state_space_coordinates
			
		if state_space_coordinate not in state_space_coordinates:
			raise KeyError() #!!!!! Создавать внятные исключения
			
			
		return self.__controls[state_space_coordinate]
		
		
		
	def __call__(self, arguments, delta_time, computing_context):
		"""
		Примечания:
			1. Проверка аргументов arguments и delta_time происходит косвенно,
				при передаче их в функции управления
		"""
		
		# Проверка контекста:
		# 	Множества функций управления контекста вычислений и комплексной
		#	функции управления должны совпадать
		controls = \
			frozenset(
				self.__controls.values()
			)
			
		if controls != computing_context.controls:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		computing_results  = dict()
		computing_contexts = dict()
		
		try:
			for state_space_coordinate in self.__state_space:
				control = self.__controls[state_space_coordinate]
				
				computing_result = \
					control(
						arguments,
						delta_time,
						computing_context[control]
					)
					
				if computing_result is NoneComputingResult():
					computing_results[state_space_coordinate] = \
						NoneComputingResult()
						
					computing_contexts[control] = NoneComputingContext()
				else:
					computing_results[state_space_coordinate] = \
						computing_result.result
						
					computing_contexts[control] = \
						computing_results.computing_context
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
			
			
			
			
			
			
			
def cast_control(control, arguments_space):
	root_compound = control.root_compound
	
	try:
		casted_control = \
			Control(
				'root_compound':   root_compound,
				'arguments_space': arguments_space
			)
	except:
		raise Exception() #!!!!! Создавать внятные исключения
	else:
		return casted_control
		
		
		
		
		
def cast_complex_control(complex_control, arguments_space):
	controls = dict()
	
	try:
		state_space_coordinates = \
			complex_control.state_space \
				.state_space_coordinates
				
		for state_space_coordinate in state_space_coordinates:
			controls[state_space_coordinate] = \
				cast_control(
					complex_control[state_space_coordinate],
					arguments_space
				)
	except:
		raise Exception() #!!!!! Создавать внятные исключения
	else:
		return ComplexControl('controls' = controls)
		