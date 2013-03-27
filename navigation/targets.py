from abc import ABCMeta, abstractmethod



#!!!!! 1. Цели д.б. совместимыми - принадлежать одному пространству состояний
#!!!!! 		Добавить проверку этого:
#!!!!! 			- при загрузке целей



class TargetsSource(object):
	__metaclass__ = ABCMeta
	
	
	
	def __init__(self):
		self.__targets = []
		
		
		
	@abstractmethod
	def _load_targets(self, targets_number):
		#!!!!! Если не получилось загрузить хотя бы одну цель,
		#!!!!! 	то нужно откатить все загруженные и выдать исключение
		pass
		
		
	def load_targets(self, targets_number):
		if targets_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		try:
			targets = self._load_targets(targets_number)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
		else:
			if len(targets) == targets_number:
				#!!!!! Проверка targets
				
				self.__targets += targets
			else:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
				
	@property
	def current_target(self):
		return self.get_target()
		
		
	def get_target(self, target_offset = 0):
		if target_offset < 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		if len(self.__targets) > target_offset:
			has_target = True
		else:
			try:
				self.load_targets(
					target_offset - len(self.__targets) + 1
				)
			except: #!!!!! Учитывать тип исключения
				has_target = False
			else:
				has_target = True
				
				
		if has_target:
			target = self.__targets[target_offset]
		else:
			target = None
			
		return target
		
		
	def confirm_current_target(self):
		if self.__targets:
			has_target = True
		else:
			try:
				self.load_targets()
			except: #!!!!! Учитывать тип исключения
				has_target = False
			else:
				has_target = True
				
		if has_target:
			self.__targets.pop(0)
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
class TargetsSourceView(object):
	def __init__(self, targets_source, tagets_number):
		if tagets_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self.__targets       = []
		self.__tagets_number = tagets_number
		
		try:
			while len(self.__targets) < tagets_number:
				self.__targets.append(
					targets_source.get_target(
						len(self.__targets)
					)
				)
		except:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
	@property
	def tagets_number(self):
		return self.__tagets_number
		
		
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
		