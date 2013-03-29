from bge import logic

import random
import math
import operator





#!!!!! 1. Весь модуль нужно исправить





# Базовый оператор функции управления
class Operator:
	def __init__(self, function, arguments_number, representation):
		self.function          = function
		self.arguments_number  = arguments_number
		self.representation    = representation
		self.input_operators   = [None] * arguments_number
		self.superior_operator = None
		
	# Поверхностное клонирование объекта оператора
	def copy(self):
		operator = \
			Operator(self.function, self.arguments_number, self.representation)
		operator.input_operators   = self.input_operators[:]
		operator.superior_operator = self.superior_operator
		
		return operator
		
		
	def __str__(self):
		return self.representation
		
	def __repr__(self):
		return self.__str__()
		
		
	def has_unbound_inputs(self):
		return None in self.input_operators
		
	def bind_input(self, input_operator):
		input_operators = self.input_operators
		
		if input_operator not in input_operators:
			try:
				input_operator_number = input_operators.index(None)
			except:
				raise Exception() #!!!!! Создавать внятные исключения
			else:
				input_operators[input_operator_number] = input_operator
				input_operator.superior_operator       = self
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
	def unbind_input(self, input_operator):
		try:
			input_operators       = self.input_operators
			input_operator_number = input_operators.index(input_operator)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			input_operators[input_operator_number] = None
			input_operator.superior_operator       = None
			
			
	def __call__(self, arguments):
		if not self.has_unbound_inputs():
			try:
				input_values = \
					[input_operator.__call__(arguments) for input_operator
						in self.input_operators]
						
				output_value = self.function(*input_values)
			except:
				raise Exception() #!!!!! Создавать внятные исключения
			else:
				return output_value
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
def get_operator_factory(function, arguments_number, representation):
	return (lambda: Operator(function, arguments_number, representation))
	
	
# Оператор базовая функция которого не может быть копирована,
# 	а должна быть создана заного (например, функция имеющая состояние)
class StatedOperator(Operator):
	def __init__(self, function_factory, arguments_number, representation):
		Operator.__init__(self, function_factory(), arguments_number, representation)
		
		self.function_factory = function_factory
		
	def copy():
		stated_operator                  = Operator.copy(self)
		stated_operator.function         = self.function_factory()
		stated_operator.function_factory = self.function_factory
		
		return stated_operator
		
def get_stated_operator_factory(function_factory, arguments_number, representation):
	return (lambda: StatedOperator(function_factory, arguments_number, representation))
	
	
# Константный оператор
class Constant(Operator):
	def __init__(self, lower_limit, upper_limit):
		constant = random.uniform(lower_limit, upper_limit)
		
		Operator.__init__(self, lambda: constant, 0, str(constant))
		
def get_constant_factory(lower_limit, upper_limit):
	return (lambda: Constant(lower_limit, upper_limit))
	
	
# Оператор-аргумент
class Argument(Operator):
	def __init__(self, argument_name):
		Operator.__init__(self, None, 0, argument_name)
		
		self.argument_name = argument_name
		
	def copy(self):
		argument               = Operator.copy()
		argument.argument_name = self.argument_name
		
		return argument
		
	def __call__(self, arguments):
		if self.argument_name in arguments:
			return arguments[self.argument_name]
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
def get_argument_factory(argument_name):
	return (lambda: Argument(argument_name))
	
	
	
# Фабрики базовых функций, которые не могут быть копированы
def differentiation_function_factory():
	last_argument_value = [None]
	
	def differentiation_function(argument):
		if last_argument_value[0] is None:
			last_argument_value[0] = argument
			
			
		derivative = \
			(argument - last_argument_value[0]) \
				* logic.getPhysicsTicRate()
				
		last_argument_value[0] = argument
		
		return derivative
		
		
	return differentiation_function
	
	
def integration_function_factory():
	accumulated_value = [0]
	
	def integration_function(argument):
		accumulated_value[0] += \
			argument / logic.getPhysicsTicRate()
			
		return accumulated_value
		
		
	return integration_function
	
	
	
# Функция управления
class Control:
	def __init__(self):
		self.root_operator     = None
		self.max_control_depth = None
		self.arguments_space   = None #-----
		
	#-----
	@property
	def arguments_space(self):
		return self.arguments_space
		
	# Клонирование объекта функции управления
	def copy(self):
		def copy_operators(operator, superior_operator = None):
			operator                   = operator.copy()
			operator.superior_operator = superior_operator
			
			for input_operator in enumerate(operator.input_operators):
				input_operator_number, input_operator = input_operator
				
				operator.input_operators[input_operator_number] = \
					copy_operators(input_operator, operator)
					
			return operator
			
			
		control                   = Control()
		control.root_operator     = copy_operators(self.root_operator)
		control.max_control_depth = self.max_control_depth
		
		return control
		
		
	def __str__(self):
		def represent_control(operator, indent_size):
			representation = ("\t" * indent_size) + operator.representation
			
			for input_operator in operator.input_operators:
				representation += \
					"\n" + represent_control(input_operator, indent_size + 1)
					
			return representation
			
		return represent_control(self.root_operator, 0)
		
	def __repr__(self):
		return self.__str__()
		
		
	def __call__(self, arguments):
		output_value = self.root_operator.__call__(arguments)
		
		# Результат исполнения функции управления должен лежать в диапазоне от -1 до 1,
		# 	чтобы соответствовать диапазону возможных значений
		# 	относительной силы двигателей аппарата
		output_value = max(output_value, -1)
		output_value = min(output_value,  1)
		
		return output_value
		
		
		
class ComplexControl:
	def __init__(self, state_space, arguments_space):
		self.arguments_space = arguments_space #-----
		self.state_space     = state_space #-----
		self.controls        = dict()
		
		for state_space_coordinate in self.state_space.state_space_coordinates:
			self.controls[state_space_coordinate] = Control()
			
	#-----
	@property
	def arguments_space(self):
		return self.arguments_space
		
	#-----
	@property
	def state_space(self):
		return self.state_space
		
	def copy(self):
		complex_control = ComplexControl(self.state_space, self.arguments_space)
		
		for state_space_coordinate in self.state_space.state_space_coordinates:
			complex_control[state_space_coordinate] = self[state_space_coordinate]
			
		return complex_control
		
		
	def __getitem__(self, state_space_coordinate):
		if state_space_coordinate in self.state_space.state_space_coordinates:
			control = self.controls[state_space_coordinate]
		else:
			raise KeyError() #!!!!! Создавать внятные исключения
			
		return control
		
	def __setitem__(self, state_space_coordinate, control):
		if control.arguments_space != self.arguments_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if state_space_coordinate in self.state_space.state_space_coordinates:
			self.controls[state_space_coordinate] = control
		else:
			raise KeyError() #!!!!! Создавать внятные исключения
			
			
	def __str__(self):
		representation = ""
		
		for state_space_coordinate in self.state_space.state_space_coordinates:
			control_representation = "%s:\n%s" % (state_space_coordinate, str(self[state_space_coordinate]))
			control_representation = control_representation.replace("\n", "\n\t")
			
			if representation:
				representation += "\n"
				
			representation += control_representation
			
		return representation
		
	def __repr__(self):
		return self.__str__()
		
		
	def __call__(self, **arguments_values):
		if self.arguments_space != frozenset(arguments_values.iterkeys()): #!!!!! ArgumentsSpace(...)
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		output_value = dict()
		
		for state_space_coordinate in self.state_space.state_space_coordinates:
			control = self[state_space_coordinate]
			
			output_value[state_space_coordinate] = control.__call__(**arguments_values)
			
		return output_value
		
		
		
# Генерация случайной функции управления
def generate_control(max_control_depth, arguments_space):
	# Фабрики используемых операторов
	leaf_operator_factories = \
		[get_argument_factory(argument) for argument in arguments_space] \
			+ [get_constant_factory(-10, 10)]
			
	branch_operator_factories = [
		get_operator_factory(operator.add, 2, "+"),
		get_operator_factory(operator.mul, 2, "*"),
		get_operator_factory(math.pow, 2, "^"),
		get_operator_factory(math.sin, 1, "sin"),
		get_stated_operator_factory(
			differentiation_function_factory,
				1,
				"d/dt"
		),
		get_stated_operator_factory(
			integration_function_factory,
				1,
				"integration"
		)
	]
	
	operator_factories = leaf_operator_factories + branch_operator_factories
	
	
	
	# Генерация случайного оператора
	def generate_operator(operator_depth = 1):
		try:
			if operator_depth == max_control_depth:
				operator_factory = random.choice(leaf_operator_factories)
			else:
				operator_factory = random.choice(operator_factories)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			return operator_factory()
			
			
	# Создание корневого оператора функции управления
	root_operator     = generate_operator()
	unbound_operators = [(root_operator, 1)]
	
	# Добавление новых операторов в дерево происходит до тех пор,
	# 	пока в нем присутствуют несвязанные вершины
	while len(unbound_operators) > 0:
		unbound_operator, unbound_operator_depth = unbound_operators[0]
		
		if unbound_operator.has_unbound_inputs():
			generated_operator_depth = unbound_operator_depth + 1
			generated_operator       = generate_operator(generated_operator_depth)
			
			unbound_operator.bind_input(generated_operator)
			unbound_operators.append(
				(generated_operator, generated_operator_depth)
			)
		else:
			unbound_operators = \
				[(operator, operator_depth)
					for operator, operator_depth
					in  unbound_operators
					if	operator is not unbound_operator]
					
					
	# Создание функции управления
	сontrol                   = Control()
	сontrol.root_operator     = root_operator
	сontrol.max_control_depth = max_control_depth
	сontrol.arguments_space   = arguments_space
	
	return сontrol
	
	
	
# Скрещивание функций управления
def reproduce_controls(first_control, second_control, need_mutation):
	def collect_control_info(control):
		def collect_subcontrol_info(base_operator, base_operator_depth = 1):
			base_operator_subcontrol_info  = []
			base_operator_subcontrol_depth = 1
			
			
			for input_operator in base_operator.input_operators:
				input_operator_subcontrol_info, input_operator_subcontrol_depth = \
					collect_control_info(input_operator, base_operator_depth + 1)
					
				base_operator_subcontrol_info  += input_operator_subcontrol_info
				base_operator_subcontrol_depth  = \
					max(base_operator_subcontrol_depth, input_operator_subcontrol_depth + 1)
					
					
			base_operator_subcontrol_info += \
				[(base_operator, base_operator_depth, base_operator_subcontrol_depth)]
				
			return (
				base_operator_subcontrol_info,
					base_operator_subcontrol_depth
			)
			
		subcontrol_info, _ = collect_subcontrol_info(control.root_operator)
		
		
		return subcontrol_info
		
		
	first_control, second_control = first_control.copy(), second_control.copy()
	reproduced_control            = first_control
	
	
	
	# Скрещивание функций управления
	#
	
	# Выбор исключаемого и включаемого поддеревьев (их корневых операторов)
	first_control_info, second_control_info = \
		collect_control_info(first_control), None
		
	while not second_control_info:
		def filter_control_info(control_info, max_subcontrol_depth):
			def filter_predicate(operator_info):
				_, _, operator_subcontrol_depth = operator_info
				
				return operator_subcontrol_depth <= max_subcontrol_depth
				
			return (
				[operator_info for operator_info in control_info
					if filter_predicate(operator_info)]
			)
			
			
		excluded_operator, excluded_operator_depth, _ = \
			random.choice(first_control_info)
			
		second_control_info = \
			filter_control_info(
				collect_control_info(second_control),
					first_control.max_control_depth - excluded_operator_depth + 1
			)
			
			
	included_operator, _, _ = random.choice(second_control_info)
	
	
	# Замена поддерева
	superior_excluded_operator = excluded_operator.superior_operator
	
	if superior_excluded_operator:
		superior_excluded_operator.unbind_input(excluded_operator)
		superior_excluded_operator.bind_input(included_operator)
	else:
		reproduced_control.root_operator = included_operator
		
		
		
	# Мутация функции управления
	#
	
	if need_mutation:
		# Выбор исключаемого поддерева функции управления (его корневого оператора)
		excluded_operator, excluded_operator_depth, _ = \
			random.choice(
				collect_control_info(reproduced_control)
			)
			
			
		# Генерирование случайного поддерева
		max_included_subcontrol_depth = \
			reproduced_control.max_control_depth - excluded_operator_depth + 1
			
		included_operator = \
			generate_control(max_included_subcontrol_depth) \
				.root_operator
				
				
		# Замена поддерева функции управления
		superior_excluded_operator = excluded_operator.superior_operator
		
		if superior_excluded_operator:
			superior_excluded_operator.unbind_input(excluded_operator)
			superior_excluded_operator.bind_input(included_operator)
		else:
			reproduced_control.root_operator = included_operator
			