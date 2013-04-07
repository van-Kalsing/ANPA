from optimization.targets import TargetsSource, TargetsSourceView
from abc                  import ABCMeta, abstractmethod, abstractproperty





class WrappedTargetsSource(TargetsSource):
	def __init__(self, targets_state_space, generate_target):
		super(WrappedTargetsSource, self).__init__()
		
		self.__generate_target     = generate_target
		self.__targets_state_space = targets_state_space
		
		
	def _load_targets(self, targets_number):
		targets = []
		
		while len(targets) != targets_number:
			targets.append(
				self.__generate_target()
			)
			
		self._targets += targets
		
		
	@property
	def targets_state_space(self):
		return self.__targets_state_space
		
		
		
# class RevolvingWrappedTargetsSource(TargetsSource):
# 	def __init__(self, targets_state_space, generate_target):
# 		super(RevolvingWrappedTargetsSource, self).__init__()
		
# 		self.__base_target_offset  = 0
# 		self.__base_targets_source = \
# 			WrappedTargetsSource(
# 				targets_state_space,
# 				generate_target
# 			)
			
			
# 	def reset(self):
# 		self.__base_target_offset = 0
		
		
# 	def _load_targets(self, targets_number):
# 		targets = []
		
		
# 		targets_offsets = \
# 			range(
# 				self.__base_target_offset,
# 				self.__base_target_offset + targets_number
# 			)
			
# 		for target_offset in targets_offsets:
# 			targets.append(
# 				self.__base_targets_source.get_target(target_offset)
# 			)
			
			
# 		self.__base_target_offset += targets_number
# 		self._targets             += targets
		
		
# 	@property
# 	def targets_state_space(self):
# 		return self.__base_targets_source.targets_state_space
		
		
		
		
		
class ComplexControlTest(object):
	__metaclass__ = ABCMeta
	
	
	
	def __init__(self, navigation, complex_control, generate_target):
		is_complex_control_compatible = \
			complex_control.state_space \
				== navigation.complex_controls_state_space
				
		if not is_complex_control_compatible:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		self.__navigation      = navigation
		self.__complex_control = complex_control
		self.__targets_source  = \
			WrappedTargetsSource(
				navigation.targets_state_space,
				generate_target
			)
			
		self.__is_interrupted = False
		self._machine_state   = None
		self._target          = None
		
		
		
	@property
	def navigation(self):
		return self.__navigation
		
		
	@property
	def complex_control(self):
		return self.__complex_control
		
		
		
	@property
	def is_initialized(self):
		is_initialized = \
			self._machine_state is not None \
				and self._target is not None
				
		return is_initialized
		
		
	@abstractproperty
	def _is_finished(self):
		pass
		
		
	@property
	def is_finished(self):
		if self.__is_interrupted:
			is_finished = True
		else:
			is_finished = self._is_finished
			
		return is_finished
		
		
		
	@abstractproperty
	def _result(self):
		pass
		
		
	@property
	def result(self):
		if not self.is_finished:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		if self.__is_interrupted:
			result = None
		else:
			result = self._result
			
		return result
		
		
		
	@abstractmethod
	def _measure(self, machine_state, target, delta_time):
		pass
		
		
	def __measure(self, machine_state, target, delta_time):
		self._measure(machine_state, target, delta_time)
		
		self._target        = self.__targets_source.current_target
		self._machine_state = \
			self.__navigation.machine.get_current_state(
				self.__navigation.targets_state_space
			)
			
			
			
	def initialize(self):
		if self.is_initialized:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if self.is_finished:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self.__navigation.reset_machine_state()
		
		self._target        = self.__targets_source.current_target
		self._machine_state = \
			self.__navigation.machine.get_current_state(
				self.__navigation.targets_state_space
			)
			
			
		self.iterate(0.0)
		
		
	def iterate(self, delta_time):
		if not self.is_initialized:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if self.is_finished:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if delta_time < 0.0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		current_target = self.__targets_source.current_target
		machine_state  = \
			self.__navigation.machine.get_current_state(
				self.__navigation.targets_state_space
			)
			
			
		is_iteration_finished = False
		
		while not is_iteration_finished:
			self.__measure(machine_state, current_target, delta_time)
			
			
			if (current_target is not None) and (not self.is_finished):
				is_target_confirmed = \
					self.__navigation.check_target_confirmation(
						current_target
					)
					
				if is_target_confirmed:
					self.__targets_source.confirm_current_target()
					
					current_target = self.__targets_source.current_target
					delta_time     = 0.0
				else:
					is_iteration_finished = True
			else:
				is_iteration_finished = True
				
				
		if not self.is_finished:
			targets_source_view = \
				TargetsSourceView(
					self.__targets_source,
					self.__navigation.targets_accounting_depth
				)
				
			try:
				self.__navigation.navigate(
					self.__complex_control,
					targets_source_view
				)
			except:
				self.__is_interrupted = True
				
				
				
class FixedTimeMovementComplexControlTest(ComplexControlTest):
	def __init__(self,
					navigation,
					complex_control,
					generate_target,
					finishing_time):
		super(FixedTimeMovementComplexControlTest, self) \
			.__init__(navigation, complex_control, generate_target)
			
		self.__finishing_time       = finishing_time
		self.__accumulated_time     = 0.0
		self.__accumulated_movement = 0.0
		
		
	@property
	def _is_finished(self):
		return self.__accumulated_time >= self.__finishing_time
		
		
	@property
	def _result(self):
		return self.__accumulated_movement
		
		
	def _measure(self, machine_state, target, delta_time):
		if self._target is not None:
			state_space = self.navigation.targets_state_space
			
			self.__accumulated_time     += delta_time
			self.__accumulated_movement += \
				state_space.compute_distance(self._target, self._machine_state) \
					- state_space.compute_distance(self._target, machine_state)
					
					
					
class FreeTimeMovementComplexControlTest(ComplexControlTest):
	def __init__(self,
					navigation,
					complex_control,
					generate_target,
					finishing_absolute_movement,
					interrupting_time):
		super(FreeTimeMovementComplexControlTest, self) \
			.__init__(navigation, complex_control, generate_target)
			
		self.__finishing_absolute_movement   = finishing_absolute_movement
		self.__interrupting_time             = interrupting_time
		self.__accumulated_time              = 0.0
		self.__accumulated_movement          = 0.0
		self.__accumulated_absolute_movement = 0.0
		
		
	@property
	def _is_finished(self):
		is_finished = False
		
		is_finished |= \
			self.__accumulated_absolute_movement \
				>= self.__finishing_absolute_movement
				
		is_finished |= \
			self.__accumulated_time \
				>= self.__interrupting_time
				
		return is_finished
		
		
	@property
	def _result(self):
		is_correct_finish = \
			self.__accumulated_absolute_movement \
				>= self.__finishing_absolute_movement
				
		if is_correct_finish:
			result = self.__accumulated_movement
		else:
			result = None
			
			
		return result
		
		
	def _measure(self, machine_state, target, delta_time):
		if self._target is not None:
			state_space = self.navigation.targets_state_space
			
			
			self.__accumulated_movement += \
				state_space.compute_distance(self._target, self._machine_state) \
					- state_space.compute_distance(self._target, machine_state)
					
			self.__accumulated_absolute_movement += \
				state_space.compute_distance(
					self._machine_state,
					machine_state
				)
				
			self.__accumulated_time += delta_time
			
			
			
class TimeComplexControlTest(ComplexControlTest):
	def __init__(self,
					navigation,
					complex_control,
					generate_target,
					finishing_confirmed_targets_number,
					interrupting_time):
		super(TimeComplexControlTest, self) \
			.__init__(navigation, complex_control, generate_target)
			
		self.__finishing_confirmed_targets_number   = finishing_confirmed_targets_number
		self.__interrupting_time                    = interrupting_time
		self.__accumulated_confirmed_targets_number = 0
		self.__accumulated_time                     = 0.0
		
		
	@property
	def _is_finished(self):
		is_finished = False
		
		is_finished |= \
			self.__accumulated_time \
				>= self.__interrupting_time
				
		is_finished |= \
			self.__accumulated_confirmed_targets_number \
				>= self.__finishing_confirmed_targets_number
				
		return is_finished
		
		
	@property
	def _result(self):
		is_correct_finish = \
			self.__accumulated_confirmed_targets_number \
				>= self.__finishing_confirmed_targets_number
				
		if is_correct_finish:
			result = self.__accumulated_time
		else:
			result = None
			
			
		return result
		
		
	def _measure(self, machine_state, target, delta_time):
		if self._target is not None:
			self.__accumulated_time += delta_time
			
			if self._target != target:
				self.__accumulated_confirmed_targets_number += 1
				