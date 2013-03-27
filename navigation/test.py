from abc       import ABCMeta, abstractmethod, abstractproperty
from bge       import logic
from mathutils import Vector



class Test(object):
	__metaclass__ = ABCMeta
	
	
	def __init__(self):
		self.ship_state = None
		self.target     = None
		
		
	@property
	def is_initialized(self):
		return (
			self.ship_state is not None
				and self.target is not None
		)
		
	@abstractproperty
	def is_finished(self):
		pass
		
		
	def initialize(self, ship_state, target):
		self.ship_state = ship_state
		self.target     = target
		
	@abstractmethod
	def measure(self, ship_state, target, delta_time):
		pass
		
	@property
	def result(self):
		if not self.is_finished():
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			result = self._get_result()
			
		return result
		
		
	@abstractmethod
	def _get_result(self):
		pass
		
		
		
class MovementTest(Test):
	def __init__(self, finishing_time):
		super(MovementTest, self).__init__()
		
		self.finishing_time       = finishing_time
		self.accumulated_time     = 0.0
		self.accumulated_movement = 0.0
		
		
	@property
	def is_finished(self):
		return self.accumulated_time >= self.finishing_time
		
		
	def _get_result(self):
		if self.is_finished():
			return self.accumulated_movement
			
			
	def measure(self, ship_state, target, delta_time):
		if not self.is_initialized():
			raise Exception() #!!!!! Создавать внятные исключения
			
		if self.is_finished():
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		if self.target:
			# Определение приращения расстояния до цели предыдущего шага
			self.accumulated_time     += delta_time
			self.accumulated_movement += \
				(self.target - self.ship_state.world_position).magnitude \
					- (target - ship_state.world_position).magnitude
					
    	self.ship_state = ship_state
		self.target     = target
		
		
		
class TimeTest(Test):
	def __init__(self,
					finishing_confirmed_targets_number,
					interrupting_time):
		super(TimeTest, self).__init__()
		
		self.finishing_confirmed_targets_number   = finishing_confirmed_targets_number
		self.interrupting_time                    = interrupting_time
		self.accumulated_confirmed_targets_number = 0
		self.accumulated_time                     = 0.0
		
		
	@property
	def is_finished(self):
		return (
			self.accumulated_confirmed_targets_number
				>= self.finishing_confirmed_targets_number
		)
		
		
	def _get_result(self):
		if self.is_finished():
			return self.accumulated_time
			
			
	def measure(self, ship_state, target, delta_time):
		if not self.is_initialized():
			raise Exception() #!!!!! Создавать внятные исключения
			
		if self.is_finished():
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		if self.target:
			self.accumulated_time += delta_time
			
			if self.target != target:
				self.accumulated_confirmed_targets_number += 1
				
    	self.ship_state = ship_state
		self.target     = target
		