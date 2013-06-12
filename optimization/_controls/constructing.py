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







def generate_control(arguments_space, operators_classes):
	operators = \
		[operator_class.create_operator() for operator_class
			in operators_classes]
			
			
	compounds_content = \
		operators \
			+ list(arguments_space.arguments_space_coordinates)
			
	def generate_compound():
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
					generate_compound()
				)
				
			generated_compound = \
				OperatorCompound(
					operator = operator,
					bindings = bindings
				)
				
				
		return generated_compound
		
		
	try:
		root_compound = generate_compound()
	except:
		raise Exception() #!!!!! Создавать внятные исключения
	else:
		generated_control = \
			Control(
				root_compound   = root_compound,
				arguments_space = arguments_space
			)
			
		return generated_control
		
		
		
		
		
def generate_complex_control(state_space, arguments_space, operators_classes):
	try:
		controls = dict()
		
		for state_space_coordinate in state_space.state_space_coordinates:
			controls[state_space_coordinate] = \
				generate_control(
					arguments_space,
					operators_classes
				)
	except:
		raise Exception() #!!!!! Создавать внятные исключения
	else:
		generated_complex_control = \
			ComplexControl(
				controls = controls
			)
			
		return generated_complex_control
		
		
		
		
		
		
		
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
		