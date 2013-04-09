class Singleton(object):
	def __new__(cls, *args, **kwargs):
		if cls is Singleton:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
		try:
			instance = cls.__instance
		except AttributeError:
			instance = None
		else:
			if type(instance) is not cls:
				instance = None
				
		if instance is None:
			cls.__instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
			
			
		return cls.__instance
		