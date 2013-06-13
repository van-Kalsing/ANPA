from abc \
	import ABCMeta, \
				abstractclassmethod
				
from optimization._controls.compounds \
	import ArgumentCompound, \
				OperatorCompound
				
from optimization._controls.controls \
	import Control, \
				ComplexControl
				
from optimization._controls.arguments import ArgumentsSpaceCoordinate
from random                           import choice







def generate_control(arguments_space, operators_classes, max_depth):
	leaf_compounds_content = list(arguments_space.arguments_space_coordinates)
	compounds_content      = list(arguments_space.arguments_space_coordinates)
	
	for operator_class in operators_classes:
		operator = operator_class.create_operator()
		
		
		if operator.arguments_number == 0:
			leaf_compounds_content.append(operator)
			
		compounds_content.append(operator)
		
		
	def generate_compound(depth = 1):
		if depth == max_depth:
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
					generate_compound(depth + 1)
				)
				
			generated_compound = \
				OperatorCompound(
					operator = operator,
					bindings = bindings
				)
				
				
		return generated_compound
		
		
	if max_depth <= 0:
		raise Exception() #!!!!! Создавать внятные исключения
		
	if len(leaf_compounds_content) == 0:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	root_compound = generate_compound()
	
	return Control(root_compound, arguments_space)
	
	
	
	
	
def generate_complex_control(state_space,
								arguments_space,
								operators_classes,
								max_depth):
	try:
		controls = dict()
		
		for state_space_coordinate in state_space.state_space_coordinates:
			controls[state_space_coordinate] = \
				generate_control(
					arguments_space,
					operators_classes,
					max_depth
				)
	except:
		raise Exception() #!!!!! Создавать внятные исключения
	else:
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
		