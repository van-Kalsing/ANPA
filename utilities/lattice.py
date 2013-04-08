import random





class Lattice(object):
	def __init__(self, container):
		for lower_bound, upper_bound in container:
			if lower_bound > upper_bound:
				raise Exception() #!!!!! Создавать внятные исключения
				
				
		self.__containers = \
			(
				[container],
				[]
			)
			
			
			
	def generate_node(self):
		def divide_container(container):
			generated_containers = [[]]
			
			for lower_bound, upper_bound in container:
				containers           = generated_containers
				generated_containers = []
				
				center = 0.5 * (lower_bound + upper_bound)
				
				for container in containers:
					generated_containers.append(
						list(container) + [(lower_bound, center)]
					)
					
					generated_containers.append(
						list(container) + [(center, upper_bound)]
					)
					
					
			return generated_containers
			
			
		def compute_central_vertex(container):
			central_vertex = []
			
			for lower_bound, upper_bound in container:
				central_vertex.append(
					0.5 * (lower_bound + upper_bound)
				)
				
				
			return central_vertex
			
			
			
		if not bool(self.__containers[0]):
			self.__containers = \
				(
					self.__containers[1],
					[]
				)
				
				
		containers_number = len(self.__containers[0]) - 1
		container_number  = random.randint(0, containers_number)
		
		container = \
			self.__containers[0].pop(
				container_number
			)
			
			
		generated_containers = divide_container(container)
		generated_node       = compute_central_vertex(container)
		
		self.__containers[1].extend(
			generated_containers
		)
		
		
		return generated_node
		