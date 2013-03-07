from bge import logic
import random



# Базовый оператор функции управления
class Operator:
	def __init__(self, function, arguments_number):
		self.function          = function
		self.arguments_number  = arguments_number
		self.input_operators   = [None] * arguments_number
		self.superior_operator = None
		
	# Поверхностное копирование объекта оператора
	def copy(self):
		operator                   = Operator(self.function, self.arguments_number)
		operator.input_operators   = self.input_operators[:]
		operator.superior_operator = self.superior_operator
		
		return operator
		
		
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
			
			
	def invoke(self, arguments):
		if not self.has_unbound_inputs():
			try:
				input_values = \
					[input_operator.invoke(arguments) for input_operator
						in self.input_operators]
						
				output_value = self.function(*input_values)
			except:
				raise Exception() #!!!!! Создавать внятные исключения
			else:
				return output_value
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
def get_operator_factory(function, arguments_number):
	return (lambda: Operator(function, arguments_number))
	
	
# Оператор базовая функция которого не может быть копирована,
# 	а должна быть создана заного (например, функция имеющая состояние)
class StatedOperator(Operator):
	def __init__(self, function_factory, arguments_number):
		Operator.__init__(self, function_factory(), arguments_number)
		
		self.function_factory = function_factory
		
	def copy():
		stated_operator                  = Operator.copy(self)
		stated_operator.function         = self.function_factory()
		stated_operator.function_factory = self.function_factory
		
		return stated_operator
		
def get_stated_operator_factory(function_factory, arguments_number):
	return (lambda: StatedOperator(function_factory, arguments_number))
	
	
# Константный оператор
class Constant(Operator):
	def __init__(self, lower_limit, upper_limit):
		constant = random.uniform(lower_limit, upper_limit)
		
		Operator.__init__(self, lambda: constant, 0)
		
def get_constant_factory(lower_limit, upper_limit):
	return (lambda: Constant(lower_limit, upper_limit))
	
	
# Оператор-аргумент
class Argument(Operator):
	def __init__(self, argument_name):
		Operator.__init__(self, None, 0)
		
		self.argument_name = argument_name
		
	def copy(self):
		argument               = Operator.copy()
		argument.argument_name = self.argument_name
		
		return argument
		
	def invoke(self, arguments):
		if self.argument_name in arguments:
			return arguments[self.argument_name]
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
def get_argument_factory(argument_name):
	return (lambda: Argument(argument_name))
	
	
	
# Функция управления
class Control:
	def __init__(self):
		self.root_operator     = None
		self.max_control_depth = None
		
	# Поверхностное копирование объекта функции управления
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
		
		
	def invoke(self, arguments):
		output_value = self.root_operator.invoke(arguments)
		
		# Результат исполнения функции управления должен лежать в диапазоне от -1 до 1,
		# 	чтобы соответствовать диапазону возможных значений
		# 	относительной силы двигателей аппарата
		output_value = max(output_value, -1)
		output_value = min(output_value,  1)
		
		return output_value
		
		
		
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
	
	
	
# Генерация случайной функции управления
def generate_control(max_control_depth, argument_names):
	# Фабрики используемых операторов
	leaf_operator_factories = \
		[get_argument_factory(argument_name) for argument_name in argument_names] \
			+ [get_constant_factory(-10, 10)]
			
	branch_operator_factories = [
		get_operator_factory(
			(lambda first_argument, second_argument: first_argument + second_argument),
				2
		),
		get_operator_factory(
			(lambda first_argument, second_argument: first_argument * second_argument),
				2
		),
		get_operator_factory(
			(lambda argument: 1 / argument),
				1
		),
		get_stated_operator_factory(
			differentiation_function_factory,
				1
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
			