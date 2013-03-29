from abc         import ABCMeta, abstractmethod, abstractproperty
from collections import Mapping, Iterator





class StateSpaceCoordinate(object):
	def __new__(state_space_coordinate_class, *args, **kwargs):
		if state_space_coordinate_class is StateSpaceCoordinate:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		try:
			instance = state_space_coordinate_class.__instance
		except AttributeError:
			instance = None
		else:
			if type(instance) is not state_space_coordinate_class:
				instance = None
				
		if instance is None:
			instance = \
				super(StateSpaceCoordinate, state_space_coordinate_class) \
					.__new__(state_space_coordinate_class, *args, **kwargs)
					
			state_space_coordinate_class.__instance = instance
			
		return instance
		
		
		
		
		
class State(Mapping, Iterator):
	def __init__(self, values):
		try:
			state_space = StateSpace(values.iterkeys())
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			self.__state_space = state_space
			self.__values      = dict(values)
			
			
	@property
	def state_space(self):
		return self.__state_space
		
		
	# Реализация интерфейса Mapping
	def __len__(self):
		return len(self.__values)
		
	def __iter__(self):
		return self
		
	def __contains__(self, state_space_coordinate):
		return state_space_coordinate in self.__values
		
	def __getitem__(self, state_space_coordinate):
		if state_space_coordinate in self.__values:
			value = self.__values[state_space_coordinate]
		else:
			raise KeyError() #!!!!! Создавать внятные исключения
			
			
	# Реализация интерфейса Iterator
	def next(self):
		for state_space_coordinate in self.__values:
			yield state_space_coordinate
			
		raise StopIteration
		
		
		
class StateSpace(object):
	__metaclass__ = ABCMeta
	
	
	@abstractproperty
	def state_space_coordinates(self):
		pass
		
		
	# Сравнение пространств состояний
	def __lt__(self, state_space):
		result = \
			self.state_space_coordinates.__lt__(
				state_space.state_space_coordinates
			)
			
		return result
		
	def __le__(self, state_space):
		result = \
			self.state_space_coordinates.__le__(
				state_space.state_space_coordinates
			)
			
		return result
		
	def __eq__(self, state_space):
		result = \
			self.state_space_coordinates.__eq__(
				state_space.state_space_coordinates
			)
			
		return result
		
	def __ne__(self, state_space):
		result = \
			self.state_space_coordinates.__ne__(
				state_space.state_space_coordinates
			)
			
		return result
		
	def __gt__(self, state_space):
		result = \
			self.state_space_coordinates.__gt__(
				state_space.state_space_coordinates
			)
			
		return result
		
	def __ge__(self, state_space):
		result = \
			self.state_space_coordinates.__ge__(
				state_space.state_space_coordinates
			)
			
		return result
		
		
	# Принадлежность состояния аппарата пространству
	def __contains__(self, state):
		return self == state.state_space
		
		
		
class CustomStateSpace(StateSpace):
	def __init__(self, state_space_coordinates):
		self.__state_space_coordinates = frozenset(state_space_coordinates)
		
		if len(self.__state_space_coordinates) == 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
	@property
	def state_space_coordinates(self):
		return self.__state_space_coordinates
		
		
		
class MetricStateSpace(StateSpace):
	__metaclass__ = ABCMeta
	
	
	@abstractmethod
	def _compute_distance(self, first_state, second_state):
		pass
		
		
	def compute_distance(self, first_state, second_state):
		if first_state not in self or second_state not in self:
			raise Exception() #!!!!! Создавать внятные исключения
			
		return self._compute_distance(first_state, second_state)
		
		
		
		
		
class Machine(object):
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
				super(Machine, machine_class) \
					.__new__(machine_class, *args, **kwargs)
					
			machine_class.__instance = instance
			
		return instance
		
		
	@abstractproperty
	def _full_state_space(self):
		pass
		
		
	@abstractmethod
	def _get_current_state(self, state_space):
		pass
		
	def get_current_state(self, state_space):
		if not state_space <= self._full_state_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
		return self._get_current_state(state_space)
		
		
	@abstractmethod
	def _set_state(self, state):
		pass
		
	def set_state(self, state):
		if state not in self._full_state_space:
			raise Exception() #!!!!! Создавать внятные исключения
			
		self._set_state(state)
		
	@abstractmethod
	def reset_state(self):
		pass
		