from optimization._controls.constructing \
	import generate_compounds, \
				copy_compounds, \
				replace_compound
				
from random import choice





def cross_controls(first_control, second_control, max_height):
	if first_control.height > max_height:
		raise Exception() #!!!!! Создавать внятные исключения
		
	if second_control.height > max_height:
		raise Exception() #!!!!! Создавать внятные исключения
		
	if first_control.arguments_space != second_control.arguments_space:
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
			
	included_compound_max_height = max_height - excluded_compound_depth + 1
	
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
	
	
	
	
	
def mutate_control(control, operators_classes, max_height):
	if control.height > max_height:
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
	included_compound_max_height = max_height - excluded_compound_depth + 1
	
	included_compound = \
		generate_compounds(
			control.arguments_space,
			operators_classes,
			included_compound_max_height
		)
		
		
	# Замена поддерева
	mutated_control = \
		replace_compound(
			control,
			excluded_compound,
			included_compound
		)
		
		
	return mutated_control
	