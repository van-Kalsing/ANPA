from abc import ABCMeta, abstractmethod, abstractproperty



class TargetsSource(object):
	__metaclass__ = ABCMeta
	
	
	
	def __init__(self):
		self._targets = []
		
		
		
	@abstractmethod
	def _load_targets(self, targets_number):
		#!!!!! Если не получилось загрузить хотя бы одну цель,
		#!!!!! 	то нужно откатить все загруженные и выдать исключение
		pass
		
		
	@abstractproperty
	def targets_state_space(self):
		pass
		
		
	def load_targets(self, targets_number):
		if targets_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
		self._load_targets(targets_number)
		
		
		
	@property
	def current_target(self):
		return self.get_target()
		
		
	def get_target(self, target_offset = 0):
		if target_offset < 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		if len(self._targets) > target_offset:
			has_target = True
		else:
			try:
				self.load_targets(
					target_offset - len(self._targets) + 1
				)
			except: #!!!!! Учитывать тип исключения
				has_target = False
			else:
				has_target = True
				
				
		if has_target:
			target = self._targets[target_offset]
		else:
			target = None
			
		return target
		
		
	def confirm_current_target(self):
		if self._targets:
			has_target = True
		else:
			try:
				self.load_targets()
			except: #!!!!! Учитывать тип исключения
				has_target = False
			else:
				has_target = True
				
		if has_target:
			self._targets.pop(0)
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
class TargetsSourceView(object):
	def __init__(self, targets_source, targets_number):
		if targets_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self.__targets             = []
		self.__targets_number      = targets_number
		self.__targets_state_space = targets_source.targets_state_space
		
		try:
			while len(self.__targets) < self.__targets_number:
				self.__targets.append(
					targets_source.get_target(
						len(self.__targets)
					)
				)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
	@property
	def targets_state_space(self):
		return self.__targets_state_space
		
		
	@property
	def targets_number(self):
		return self.__targets_number
		
		
	@property
	def current_target(self):
		return self.get_target()
		
		
	def get_target(self, target_offset = 0):
		if target_offset < 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		if target_offset < len(self.__targets):
			target = self.__targets[target_offset]
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
		return target
		