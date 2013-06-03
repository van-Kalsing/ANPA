from utilities.singleton import Singleton
from abc                 import ABCMeta, abstractproperty, abstractmethod







class ImprovementDirection(Singleton):
	def __new__(improvement_direction_class, *args, **kwargs):
		if improvement_direction_class is ImprovementDirection:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		improvement_direction = \
			super(ImprovementDirection, improvement_direction_class) \
				.__new__(improvement_direction_class, *args, **kwargs)
				
		return improvement_direction
		
		
		
class Maximization(ImprovementDirection):
	pass
	
	
	
class Minimization(ImprovementDirection):
	pass
	
	
	
	
	
	
	
class CriterionMeter(object):
	__metaclass__ = ABCMeta
	
	
	
	def __init__(self):
		self.__is_initialized = False
		self.__is_interrupted = False
		
		self.__last_machine_state = None
		self.__last_target        = None
		
		
		
	@abstractproperty
	def criterion(self):
		pass
		
		
	@property
	def is_initialized(self):
		return self.__is_initialized
		
		
	@property
	def is_interrupted(self):
		return self.__is_interrupted
		
		
		
	@abstractproperty
	def _value(self):
		pass
		
		
	@property
	def value(self):
		if not self.__is_initialized:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		if self.__is_interrupted:
			value = None
		else:
			value = self._value
			
		return value
		
		
	def _initialize(self, machine_state, target):
		pass
		
		
	def initialize(self, machine_state, target):
		if self.__is_initialized:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self._initialize(machine_state, target)
		
		
		self.__is_initialized = True
		
		self.__last_machine_state = machine_state
		self.__last_target        = target
		
		
	@abstractmethod
	def _measure(self,
					last_machine_state,
					last_target,
					machine_state,
					target,
					delta_time):
		pass
		
		
	def measure(self, machine_state, target, delta_time):
		if not self.__is_initialized:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if self.__is_interrupted:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		if machine_state not in self.criterion.state_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if target not in self.criterion.state_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		try:
			self._measure(
				self.__last_machine_state,
				self.__last_target,
				machine_state,
				target,
				delta_time
			)
		except: #!!!!! Отслеживать тип исключения
			self.__is_interrupted = True
			
		self.__last_machine_state = machine_state
		self.__last_target        = target
		
		
		
		
		
class Criterion(Singleton):
	__metaclass__ = ABCMeta
	
	
	
	@abstractproperty
	def state_space(self):
		pass
		
		
		
	@abstractproperty
	def improvement_direction(self):
		pass
		
		
		
	@abstractmethod
	def create_criterion_meter(self):
		pass
		
		
		
		
		
		
		
class MultipleCriterionMeter(CriterionMeter):
	def __init__(self, multiple_criterion):
		self.__multiple_criterion   = multiple_criterion
		self.__subcriterions_meters = \
			[subcriterion.create_criterion_meter() for subcriterion
				in multiple_criterion.subcriterions]
				
				
				
	@property
	def criterion(self):
		return self.__multiple_criterion
		
		
		
	def _value(self):
		value = \
			self.__multiple_criterion.fold_subcriterions_meters_values(
				self.__subcriterions_meters
			)
			
		return value
		
		
	def _initialize(self, machine_state, target):
		for subcriterion_meter in self.__subcriterions_meters:
			subcriterion_meter.initialize(machine_state, target)
			
			
	def _measure(self,
					last_machine_state,
					last_target,
					machine_state,
					target,
					delta_time):
		for subcriterion_meter in self.__subcriterions_meters:
			subcriterion_meter.measure(
				machine_state,
				target,
				delta_time
			)
			
			if subcriterion_meter.is_interrupted:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
				
				
				
class MultipleCriterion(Criterion):
	__metaclass__ = ABCMeta
	
	
	
	@abstractproperty
	def _subcriterions(self):
		pass
		
		
	def subcriterions(self):
		return frozenset(self._subcriterions)
		
		
		
	@abstractmethod
	def _fold_subcriterions_meters_values(self, subcriterions_meters):
		pass
		
		
	def fold_subcriterions_meters_values(self, subcriterions_meters):
		subcriterions = \
			[subcriterion_meter.criterion for subcriterion_meter
				in subcriterions_meters]
				
		if self.subcriterions != subcriterions:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		is_interrupted = False
		
		
		for subcriterion_meter in subcriterions_meters:
			if not subcriterion_meter.is_initialized:
				raise Exception() #!!!!! Создавать внятные исключения
				
			if subcriterion_meter.is_interrupted:
				is_interrupted = True
				
				
		if is_interrupted:
			value = None
		else:
			value = \
				self._fold_subcriterions_meters_values(
					subcriterions_meters
				)
				
				
		return value
		
		
		
	def create_criterion_meter(self):
		return MultipleCriterionMeter(self)
		