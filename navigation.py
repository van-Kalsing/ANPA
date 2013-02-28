from bge       import logic
from mathutils import Vector, Matrix
from ship      import set_ship_right_engine_force, \
						set_ship_left_engine_force, \
						set_ship_top_engine_force
import math



# Получение объектов модели
scene      = logic.getCurrentScene()
ship       = scene.objects["Ship"]
navigation = scene.objects["Navigation"]



# Коллекция целей
class Targets:
	def __init__(self):
		self.reset_targets()
		
		
	#!!!!! Заменить на загрузку из файла
	#!!!!! Изменить подход к хранению списка целей (не в виде пар), т.к. не удобно отображать цели
	def reset_targets(self):
		self.current_target_number = 0
		self.targets               = []
		
		
		scene   = logic.getCurrentScene()
		targets = \
			[[30, 30, -5], [40, 25, -5]] #[-30, -30, 0], [30, -30, -5], [-30, 30, 0]]
			
		for target in targets:
			target_marker               = scene.addObject("Target_marker", "Target_marker")
			target_marker.worldPosition = target
			
			self.targets.append((target, target_marker))			
			
			
	def has_unconfirmed_targets(self):
		return self.current_target_number < len(self.targets)
		
	def get_current_target(self):
		if self.current_target_number < len(self.targets):
			target, _ = self.targets[self.current_target_number]
			
			return target
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
	def confirm_current_target(self):
		if self.current_target_number < len(self.targets):
			_, target_marker           = self.targets[self.current_target_number]
			self.current_target_number = self.current_target_number + 1
			
			if not target_marker.invalid:
				target_marker.endObject()
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
targets = Targets()



def update_ship_engines_forces():
	# Определение цели
	has_target = False
	
	while targets.has_unconfirmed_targets():
		target                           = targets.get_current_target()
		distance, _, local_target_course = ship.getVectTo(target)
		
		# Определение достижения цели
		if distance <= navigation["confirming_distance"]:
			targets.confirm_current_target()
			
			if (not targets.has_unconfirmed_targets()) and navigation["looping_toggle"]:
				targets.reset_targets()
		else:
			has_target = True
			break
			
			
			
	# Вычисление сил винтов
	if has_target:
		horizontal_angle = math.asin(local_target_course.x / local_target_course.magnitude)
		if local_target_course.y < 0:
			if horizontal_angle >= 0:
				horizontal_angle = math.pi - horizontal_angle
			else:
				horizontal_angle = -math.pi - horizontal_angle
				
				
		if horizontal_angle > (math.pi / 2):
			relative_right_engine_force = -1 / (1 + math.exp(-8 * (horizontal_angle - 3 * math.pi / 4)))
		else:
			relative_right_engine_force = 1 / (1 + math.exp(5 * (horizontal_angle - math.pi / 4)))
			
		if horizontal_angle < (-math.pi / 2):
			relative_left_engine_force = -1 / (1 + math.exp(-8 * (-horizontal_angle - 3 * math.pi / 4)))
		else:
			relative_left_engine_force = 1 / (1 + math.exp(5 * (-horizontal_angle - math.pi / 4)))
			
		relative_top_engine_force = \
			2 / (1 + 1 * math.exp(-5 * distance * local_target_course.z)) - 1
			
			
		# Установка сил винтов
		set_ship_right_engine_force(relative_right_engine_force)
		set_ship_left_engine_force(relative_left_engine_force)
		set_ship_top_engine_force(relative_top_engine_force)
	else:
		# Выключение двигателей
		switch_off_ship_right_engine_force()
		switch_off_ship_left_engine_force()
		switch_off_ship_top_engine_force()
		