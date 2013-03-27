from abc      import ABCMeta, abstractmethod
from controls import ComplexControl
from targets  import TargetsSourceView



#!!!!! 1. Принимаемые функции управления должны быть одного типа
#!!!!! 		Добавить проверку



class Navigation(object):
	__metaclass__ = ABCMeta
	
	
	
	def __init__(self, targets_accounting_depth):
		self.__targets_accounting_depth = targets_accounting_depth
		
		
		
	@abstractproperty
	def machine(self):
		pass
		
	@abstractproperty
	def controls_arguments(self):
		pass
		
	@property
	def targets_accounting_depth(self):
		return self.__targets_accounting_depth
		
		
		
	@abstarctmethod
	def check_target_confirmation(self, target):
		pass
		
	def navigate(self, complex_control, targets_source_view):
		if not self.__check_complex_control_compatibility(complex_control):
			raise Exception() #!!!!! Создавать внятные исключения
			
		if not self.__check_targets_source_view_compatibility(targets_source_view):
			raise Exception() #!!!!! Создавать внятные исключения
			
		if targets_source_view.tagets_number > 0:
			is_target_confirmed = \
				self.check_target_confirmation(
					targets_source_view.current_target
				)
				
			if is_target_confirmed:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
		self.__navigate(complex_control, targets_source_view)
		
		
		
	@abstractmethod
	def __navigate(self, complex_control, targets_source_view):
		pass
		
	#!!!!!
	def __check_complex_control_compatibility(self, complex_control):
		return True #!!!!!
		
	#!!!!!
	def __check_targets_source_view_compatibility(self, targets_source_view):
		return (
			targets_source_view.tagets_number \
				>= self.__targets_accounting_depth
		)
s











