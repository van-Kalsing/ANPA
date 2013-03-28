from abc import ABCMeta, abstractmethod, abstractproperty



class Test(object):
	__metaclass__ = ABCMeta
	
	
	
	def __init__(self, state_space):
		self.__state_space  = state_space
		self._machine_state = None
		self._target        = None
		
		
		
	@property
	def state_space(self):
		return self.__state_space
		
		
	@property
	def is_initialized(self):
		is_initialized = \
			self._machine_state is not None
				and self._target is not None
				
		return is_initialized
		
		
	@abstractproperty
	def is_finished(self):
		pass
		
		
		
	def initialize(self, machine_state, target):
		if self.is_initialized:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if self.is_finished:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		if machine_state not in self.__state_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if target not in self.__state_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self._machine_state = machine_state
		self._target        = target
		
		
	def measure(self, machine_state, target, delta_time):
		if not self.is_initialized:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if self.is_finished:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		if machine_state not in self.__state_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if target not in self.__state_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self._measure(machine_state, target, delta_time)
		
		self._machine_state = machine_state
		self._target        = target
		
		
	@property
	def result(self):
		if not self.is_finished:
			raise Exception() #!!!!! Создавать внятные исключения
			
		return self._result
		
		
		
	@abstractmethod
	def _measure(self, machine_state, target, delta_time):
		pass
		
		
	@abstractproperty
	def _result(self):
		pass
		
		
		
class MovementTest(Test):
	def __init__(self, state_space, finishing_time):
		super(MovementTest, self).__init__(state_space)
		
		self.__finishing_time       = finishing_time
		self.__accumulated_time     = 0.0
		self.__accumulated_movement = 0.0
		
		
	@property
	def is_finished(self):
		return self.__accumulated_time >= self.__finishing_time
		
		
	@property
	def _result(self):
		return self.__accumulated_movement
		
		
	def _measure(self, machine_state, target, delta_time):
		if self._target is not None:
			self.__accumulated_time     += delta_time
			self.__accumulated_movement += \
				self.state_space.compute_distance(self._target, self._machine_state) \
					- self.state_space.compute_distance(target, machine_state)
					
					
					
class TimeTest(Test):
	def __init__(self,
					state_space,
					finishing_confirmed_targets_number,
					interrupting_time):
		super(TimeTest, self).__init__(state_space)
		
		self.__finishing_confirmed_targets_number   = finishing_confirmed_targets_number
		self.__interrupting_time                    = interrupting_time
		self.__accumulated_confirmed_targets_number = 0
		self.__accumulated_time                     = 0.0
		
		
	@property
	def is_finished(self):
		is_finished = False
		
		is_finished |= \
			self.__accumulated_time \
				>= __interrupting_time
		
		is_finished |= \
			self.__accumulated_confirmed_targets_number \
				>= self.__finishing_confirmed_targets_number
				
		return is_finished
		
		
	@property
	def _result(self):
		return self.__accumulated_time
		
		
	def _measure(self, machine_state, target, delta_time):
		if self._target is not None:
			self.__accumulated_time += delta_time
			
			if self.target != target:
				self.__accumulated_confirmed_targets_number += 1
				