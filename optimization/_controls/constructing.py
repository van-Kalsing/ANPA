from mongoengine \
	import EmbeddedDocument, \
				EmbeddedDocumentField, \
				ListField, \
				IntField, \
				BooleanField
				
from optimization._controls.arguments \
	import ArgumentsSpaceCoordinate, \
				ArgumentsSpace
				
from optimization._controls.compounds \
	import ArgumentCompound, \
				OperatorCompound
				
from optimization._controls.controls \
	import Control, \
				ComplexControl
				
from abc                              import ABCMeta, abstractclassmethod
from optimization._controls.operators import Operator
from random                           import choice







class ControlsConstructingParameters(EmbeddedDocument):
	__is_retrieved = \
		BooleanField(
			required = True,
			db_field = 'is_retrieved',
			default  = False
		)
		
		
	__controls_arguments_space = \
		EmbeddedDocumentField(
			ArgumentsSpace,
			required = True,
			db_field = 'controls_arguments_space',
			default  = None
		)
		
		
	__controls_max_height = \
		IntField(
			required = True,
			db_field = 'controls_max_height',
			default  = None
		)
		
		
	__controls_operators = \
		ListField(
			EmbeddedDocumentField(Operator),
			db_field = 'controls_operators_db_view',
			default  = []
		)
		
		
		
	def __init__(self,
					controls_arguments_space   = None,
					controls_operators_classes = None,
					controls_max_height        = None,
					*args,
					**kwargs):
		super(ControlsConstructingParameters, self).__init__(*args, **kwargs)
		
		
		if not self.__is_retrieved:
			self.__is_retrieved = True
			
			
			if controls_arguments_space is None:
				raise Exception() #!!!!! Создавать внятные исключения
				
			if controls_operators_classes is None:
				raise Exception() #!!!!! Создавать внятные исключения
				
			if controls_max_height is None:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
			if controls_max_height <= 0:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
				
			self.__controls_arguments_space = controls_arguments_space
			self.__controls_max_height      = controls_max_height
			
			
			# Составление списка операторов
			self.__controls_operators = []
			
			for operator_class in controls_operators_classes:
				self.__controls_operators.append(
					operator_class.create_operator()
				)
				
				
				
		self.__controls_branch_operators = []
		self.__controls_leaf_operators   = []
		
		for operator in self.__controls_operators:
			if operator.arguments_number == 0:
				self.__controls_leaf_operators.append(operator)
			else:
				self.__controls_branch_operators.append(operator)
				
				
		self.__controls_operators_classes = \
			frozenset(
				[operator.__class__ for operator
					in self.__controls_operators]
			)
			
			
			
		# Проверка листовых элементов:
		# 	должен присутствовать хотя бы один листовой элемент
		arguments_space_coordinates_number = \
			len(
				self.__controls_arguments_space \
					.arguments_space_coordinates
			)
			
		leaf_operators_number = len(self.__controls_leaf_operators)
		
		if arguments_space_coordinates_number == 0:
			if leaf_operators_number == 0:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
				
	@property
	def controls_arguments_space(self):
		return self.__controls_arguments_space
		
		
	@property
	def controls_max_height(self):
		return self.__controls_max_height
		
		
	@property
	def controls_operators_classes(self):
		return self.__controls_operators_classes
		
		
	@property
	def controls_branch_operators(self):
		return frozenset(self.__controls_branch_operators)
		
		
	@property
	def controls_leaf_operators(self):
		return frozenset(self.__controls_leaf_operators)
		
		
	@property
	def controls_operators(self):
		return frozenset(self.__controls_operators)
		
		
		
		
		
		
		
def generate_compounds(constructing_parameters):
	arguments_space_coordinates = \
		list(
			constructing_parameters.controls_arguments_space \
				.arguments_space_coordinates
		)
		
	leaf_compounds_content = \
		list(constructing_parameters.controls_leaf_operators) \
			+ arguments_space_coordinates
			
	compounds_content = \
		list(constructing_parameters.controls_operators) \
			+ arguments_space_coordinates
			
			
	def generate_compounds(depth = 1):
		if depth == constructing_parameters.controls_max_height:
			compound_content = choice(leaf_compounds_content)
		else:
			compound_content = choice(compounds_content)
			
			
		if isinstance(compound_content, ArgumentsSpaceCoordinate):
			generated_compound = \
				ArgumentCompound(
					arguments_space_coordinate = compound_content
				)
		else:
			operator = compound_content
			bindings = []
			
			for _ in range(operator.arguments_number):
				bindings.append(
					generate_compounds(depth + 1)
				)
				
			generated_compound = \
				OperatorCompound(
					operator = operator,
					bindings = bindings
				)
				
				
		return generated_compound
		
		
	return generate_compounds()
	
	
	
	
	
def copy_compounds(root_compound):
	if isinstance(root_compound, ArgumentCompound):
		copied_compounds = \
			ArgumentCompound(
				root_compound.arguments_space_coordinate
			)
			
	elif isinstance(root_compound, OperatorCompound):
		bindings = []
		
		for child_compound in root_compound.bindings:
			bindings.append(
				copy_compounds(child_compound)
			)
			
		copied_compounds = \
			OperatorCompound(
				root_compound.operator,
				bindings
			)
			
	else:	# Закрытая ветвь
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	return copied_compounds
	
	
	
	
	
	
	
def generate_control(constructing_parameters):
	root_compound = generate_compounds(constructing_parameters)
	
	generated_control = \
		Control(
			root_compound,
			constructing_parameters.controls_arguments_space
		)
		
		
	return generated_control
	
	
	
	
	
def generate_complex_control(state_space, constructing_parameters):
	controls = dict()
	
	for state_space_coordinate in state_space.state_space_coordinates:
		controls[state_space_coordinate] = \
			generate_control(constructing_parameters)
			
			
	return ComplexControl(controls)
	
	
	
	
	
	
	
def replace_compound(control, existing_compound, substitutional_compound):
	def replace_compound(compound):
		if compound == existing_compound:
			processed_compound = substitutional_compound
		elif compound in compound.child_compounds:
			bindings = []
			
			for child_compound in compound.bindings:
				bindings.append(
					replace_compound(child_compound)
				)
				
			# Возможен только узел-оператор
			processed_compound = \
				OperatorCompound(
					compound.operator,
					bindings
				)
		else:
			processed_compound = compound
			
			
		return processed_compound
		
		
		
	if existing_compound not in control.compounds:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	try:
		root_compound = replace_compound(control.root_compound)
		
		control = \
			Control(
				root_compound,
				control.arguments_space
			)
	except:
		raise Exception() #!!!!! Создавать внятные исключения
	else:
		return control
		
		
		
		
		
		
		
def cast_control(control, arguments_space):
	root_compound = control.root_compound
	
	try:
		casted_control = \
			Control(
				root_compound   = root_compound,
				arguments_space = arguments_space
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
		generated_complex_control = \
			ComplexControl(
				controls = controls
			)
			
		return generated_complex_control
		