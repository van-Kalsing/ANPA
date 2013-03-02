from bge import logic
import random



# Получение объектов модели
scene = logic.getCurrentScene()
ship  = scene.objects["Ship"]



# Базовый класс фабрик операторов функции управления
class OperatorFactory:
	def __init__(self):
		self.arguments_number = None
		
	def create_operator(this):
		raise Exception() #!!!!! Создавать внятные исключения
		
		
		
# Фабрики базовых операторов функции управления
class ConstantFactory(OperatorFactory):
	def __init__(self, limits):
		self.arguments_number = 0
		self.limits           = limits
		
	def create_operator(self):
		constant = random.uniform(*self.limits)
		
		return (lambda: constant)
		
		
class InversionFactory(OperatorFactory):
	def __init__(self):
		self.arguments_number = 1
		
	def create_operator(this):
		return (
			lambda argument: 1.0 / argument
		)
		
		
class DifferentiationFactory(OperatorFactory):
	def __init__(self):
		self.arguments_number = 1
		
	def create_operator(this):
		last_argument_value = [None]
		
		def differentiation(argument):
			if last_argument_value[0] is None:
				last_argument_value[0] = argument
				
			derivative = \
				(argument - last_argument_value[0]) \
					* logic.getPhysicsTicRate()
			last_argument_value[0] = argument
			
			return derivative
			
		return differentiation
		
		
class AdditionFactory(OperatorFactory):
	def __init__(self):
		self.arguments_number = 2
		
	def create_operator(this):
		return (
			lambda first_argument, second_argument: first_argument + second_argument
		)
		
		
class MultiplicationFactory(OperatorFactory):
	def __init__(self):
		self.arguments_number = 2
		
	def create_operator(this):
		return (
			lambda first_argument, second_argument: first_argument * second_argument
		)
		
		
		
# Узел функции управления
class Node:
	def __init__(self, operator, inputs_number):
		self.operator = operator
		self.inputs   = list(enumerate([None] * inputs_number))
		
		
	def has_unbound_inputs(self):
		for _, child_node in self.inputs:
			if not child_node:
				return True
				
				
	def get_unbound_input_numbers(self):
		return (
			[input_number for input_number, child_node in self.inputs
				if not child_node]
		)
		
		
	def bound_input(self, input_number, node):
		if input_number < len(self.inputs):
			self.inputs[input_number] = (input_number, node)
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
	def invoke(self):
		if not self.has_unbound_inputs():
			try:
				input_values = [child_node.invoke() for _, child_node in self.inputs]
				output_value = self.operator(*input_values)
			except:
				raise Exception() #!!!!! Создавать внятные исключения
			else:
				return output_value
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
# Функция управления
leaf_nodes_max_number = 10

operator_factories = \
	[
		ConstantFactory((-10, 10)),
		InversionFactory(),
		#DifferentiationFactory(),
		AdditionFactory(),
		MultiplicationFactory()
	]
	
class ControlFunction:
	def __init__(self):
		leaf_factories = \
			[leaf_factory for leaf_factory in operator_factories
				if leaf_factory.arguments_number == 0]
				
		branch_factories = \
			[leaf_factory for leaf_factory in operator_factories
				if leaf_factory.arguments_number != 0]
				
				
		def create_leaf_nodes():
			leaf_nodes_number = random.randint(1, leaf_nodes_max_number)
			leaf_nodes        = []
			
			while len(leaf_nodes) < leaf_nodes_number:
				leaf_factory  = random.choice(leaf_factories)
				leaf_operator = leaf_factory.create_operator()
				
				leaf_nodes.append(
					Node(leaf_operator, 0)
				)
				
			return leaf_nodes
			
			
		def build_tree(leaf_nodes):
			unbound_nodes = leaf_nodes
			
			while len(unbound_nodes) > 1:
				filtered_branch_factories = \
					[branch_factory for branch_factory in branch_factories
						if branch_factory.arguments_number <= len(unbound_nodes)]
						
				if filtered_branch_factories:
					branch_factory = random.choice(filtered_branch_factories)
					branch_node    = \
						Node(
							branch_factory.create_operator(),
							branch_factory.arguments_number
						)
						
					branch_node_input_numbers = branch_node.get_unbound_input_numbers()
					
					
					for branch_node_input_number in branch_node_input_numbers:
						unbound_node_number = random.randint(0, len(unbound_nodes) - 1)
						unbound_node        = unbound_nodes.pop(unbound_node_number)
						
						branch_node.bound_input(branch_node_input_number, unbound_node)
						
					leaf_nodes.append(branch_node)
				else:
					raise Exception() #!!!!! Создавать внятные исключения
					
			return unbound_nodes[0]
			
			
		self.root_node = \
			build_tree(
				create_leaf_nodes()
			)
			
			
	def invoke(self):
		return self.root_node.invoke()
		