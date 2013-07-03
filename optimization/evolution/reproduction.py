from optimization.controls.constructing \
	import ControlsConstructingParameters, \
				generate_compounds, \
				copy_compounds, \
				replace_compound
				
from random import random, choice







def cross_controls(first_control, second_control, constructing_parameters):
	if first_control.height > constructing_parameters.controls_max_height:
		raise Exception() #!!!!! Создавать внятные исключения
		
	if second_control.height > constructing_parameters.controls_max_height:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
	controls_arguments_space = constructing_parameters.controls_arguments_space
	
	if first_control.arguments_space != controls_arguments_space:
		raise Exception() #!!!!! Создавать внятные исключения
		
	if second_control.arguments_space != controls_arguments_space:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
		
		
	# Сбор информации об узлах функций управления
	described_compounds = []
	
	for control in [first_control, second_control]:
		def describe_compounds(compound, depth = 1):
			described_compounds.append([
				compound,
				control,
				depth
			])
			
			for child_compound in compound.bindings:
				describe_compounds(child_compound, depth + 1)
				
				
		describe_compounds(control.root_compound)
		
		
		
	# Выбор исключаемого поддерева
	excluded_compound, excluded_compound_control, excluded_compound_depth = \
		choice(described_compounds)
		
		
		
	# Выбор включаемого поддерева
	included_compound_control = \
		second_control if excluded_compound_control is first_control \
			else first_control
			
	included_compound_max_height = \
		constructing_parameters.controls_max_height \
			- excluded_compound_depth \
			+ 1
			
	included_compound = \
		choice(
			[compound for compound
				in included_compound_control.compounds
				if compound.height <= included_compound_max_height]
		)
		
		
		
	# Замена поддерева
	included_compound = copy_compounds(included_compound)
	
	generated_control = \
		replace_compound(
			excluded_compound_control,
			excluded_compound,
			included_compound
		)
		
		
		
	return generated_control
	
	
	
	
	
def mutate_control(control, constructing_parameters):
	controls_arguments_space = constructing_parameters.controls_arguments_space
	
	if control.arguments_space != controls_arguments_space:
		raise Exception() #!!!!! Создавать внятные исключения
		
	if control.height > constructing_parameters.controls_max_height:
		raise Exception() #!!!!! Создавать внятные исключения
		
		
		
		
	# Сбор информации об узлах функции управления
	described_compounds = []
	
	def describe_compounds(compound, depth = 1):
		described_compounds.append([
			compound,
			depth
		])
		
		for child_compound in compound.bindings:
			describe_compounds(child_compound, depth + 1)
			
			
	describe_compounds(control.root_compound)
	
	
	
	# Выбор исключаемого поддерева
	excluded_compound, excluded_compound_depth = \
		choice(described_compounds)
		
		
		
	# Генерация включаемого поддерева
	included_compound_max_height = \
		constructing_parameters.controls_max_height \
			- excluded_compound_depth \
			+ 1
			
	included_compound_constructing_parameters = \
		ControlsConstructingParameters(
			constructing_parameters.controls_arguments_space,
			constructing_parameters.controls_operators_classes,
			included_compound_max_height
		)
		
	included_compound = \
		generate_compounds(included_compound_constructing_parameters)
		
		
		
	# Замена поддерева
	mutated_control = \
		replace_compound(
			control,
			excluded_compound,
			included_compound
		)
		
		
		
	return mutated_control
	
	
	
	
	
def reproduce_controls(first_control,
							second_control,
							mutation_probability,
							constructing_parameters):
	try:
		generated_control = \
			cross_controls(
				first_control,
				second_control,
				constructing_parameters
			)
			
		if random() < mutation_probability:
			generated_control = \
				mutate_control(
					generated_control,
					constructing_parameters
				)
	except:
		raise Exception() #!!!!! Создавать внятные исключения
	else:
		return generated_control
		