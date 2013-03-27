from abc         import ABCMeta, abstractmethod, abstractproperty
from collections import Set, Iterator



class MachineParameter(object):
	__metaclass__ = ABCMeta
	
	
	def __new__(machine_class, *args, **kwargs):
		try:
			instance = machine_class.__instance
		except AttributeError:
			instance = None
		else:
			if type(instance) is not machine_class:
				instance = None
				
		if instance is None:
			instance = \
				super(MachineParameter, machine_class)
					.__new__(machine_class, *args, **kwargs)
					
			machine_class.__instance = instance
			
		return instance
		
		
	@abstractproperty
	def lower_limit(self):
		pass
		
	@abstractproperty
	def upper_limit(self):
		pass
		
		
		
class MachineStateSpace(Set, Iterator):
	def __init__(self, machine_parameters):
		self.__machine_parameters = frozenset(machine_parameters)
		
		
	# Реализация интерфейса множества
	def __contains__(self, machine_parameter):
		return machine_parameter in self.__machine_parameters
		
	def __iter__(self):
		return self
		
	def __len__(self):
		return len(self.__machine_parameters)
		
		
	# Реализация итерирования
	def next(self):
		for machine_parameter in self.__machine_parameters:
			yield machine_parameter
			
		raise StopIteration
		
		
		
class MachineState(object):
	__metaclass__ = ABCMeta
	
	
	def __init__(self, **machine_parameters):
		self.__machine_parameters       = dict()
		self.__machine_parameters_names = \
			frozenset(
				machine_parameters.iterkeys()
			)
			
		for machine_parameter_name in self.__machine_parameters_names:
			self.__machine_parameters[machine_parameter_name] = \
				machine_parameters[machine_parameter_name]
				
				
	def __getitem__(self, machine_parameter_name):
		if machine_parameter_name in self.__machine_parameters_names:
			machine_parameter_value = \
				self.__machine_parameters[machine_parameter_name]
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
	@abstractmethod
	def
	def modify(self, **machine_parameters_changes):
		machine_parameters = dict(self.__machine_parameters)
		
		
		for machine_parameter_name in machine_parameters_changes.iterkeys():
			machine_parameter_value = \
				machine_parameters_changes[machine_parameter_name]
				
			if machine_parameter_value is not None:
				machine_parameters[machine_parameter_name] = \
					machine_parameter_value
			else:
				del machine_parameters[machine_parameter_name]
				
				
		try:
			machine_state = self.__class__(**machine_parameters)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			return machine_state
			
			
			
class Machine(object):
	__metaclass__ = ABCMeta
	
	
	def __init__(self, parameters):
		influences_names = \
			[parameter for parameter
				in parameters
				if isinstance(parameter, InfluenceMachineParameter)]
				
		self.__parameters = frozenset(parameters)
		self.__influences = frozenset(influences)
		
		
	@property
	def influences(self):
		return self.__influences
		
	@property
	def parameters(self):
		return self.__parameters
		
	@abstractproperty
	def initial_state(self):
		pass
		
	@property
	def current_state(self):
		pass
		
	def set_state(self, machine_state):
		pass
		
	def reset_state(self):
		self.set_state(self.initial_state)
s

















class M(type):
	def __init__(self, parameters):
		pass
		
		
class O(object):
	__metaclass__ = M
	
	
	def __init__(self):
		pass
s





