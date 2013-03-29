from abc                   import ABCMeta, abstractmethod, abstractproperty
from optimization.controls import ComplexControl
from optimization.targets  import TargetsSourceView





class Navigation(object):
	__metaclass__ = ABCMeta
	
	
	
	@abstractproperty
	def machine(self):
		pass
		
	@abstractproperty
	def targets_accounting_depth(self):
		pass
		
	@abstractproperty
	def complex_controls_arguments_space(self):
		pass
		
	@abstractproperty
	def complex_controls_state_space(self):
		pass
		
	@abstractproperty
	def targets_state_space(self):
		pass
		
		
		
	@abstractproperty
	def confirming_distance(self):
		pass
		
		
	def check_target_confirmation(self, target):
		if target not in self.targets_state_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		current_state = \
			self.machine.get_current_state(
				self.targets_state_space
			)
			
		distance = \
			self.targets_state_space.compute_distance(
				current_state,
				target
			)
			
			
		return distance <= self.confirming_distance
		
		
		
	@abstractmethod
	def _compute_complex_control_value(self, complex_control, targets_source_view):
		pass
		
		
	def navigate(self, complex_control, targets_source_view):
		if not self.__check_complex_control_compatibility(complex_control):
			raise Exception() #!!!!! Создавать внятные исключения
			
		if not self.__check_targets_source_view_compatibility(targets_source_view):
			raise Exception() #!!!!! Создавать внятные исключения
			
		if targets_source_view.targets_number > 0:
			is_current_target_confirmed = \
				self.check_target_confirmation(
					targets_source_view.current_target
				)
				
			if is_current_target_confirmed:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
		try:
			control_value = \
				self._compute_complex_control_value(
					complex_control,
					targets_source_view
				)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			self.machine.set_state(control_value)
			
			
	def __check_complex_control_compatibility(self, complex_control):
		is_complex_control_compatible = True
		
		is_complex_control_compatible &= \
			complex_control.state_space \
				== self.complex_controls_state_space
				
		is_complex_control_compatible &= \
			complex_control.arguments_space \
				== self.complex_controls_arguments_space
				
		return is_complex_control_compatible
		
		
	def __check_targets_source_view_compatibility(self, targets_source_view):
		is_targets_source_view_compatible = True
		
		is_targets_source_view_compatible &= \
			targets_source_view.state_space \
				== self.targets_state_space
				
		is_targets_source_view_compatible &= \
			targets_source_view.targets_number \
				>= self.__targets_accounting_depth
				
		return is_targets_source_view_compatible
		