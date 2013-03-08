from bge                 import logic
from mathutils           import Vector, Matrix
from controlOptimization import Controls
from ship                import set_ship_right_engine_force,      \
									set_ship_left_engine_force,   \
									set_ship_top_engine_force,    \
									switch_off_ship_right_engine, \
									switch_off_ship_left_engine,  \
									switch_off_ship_top_engine
									
import control
import math
import random



# Получение объектов модели
scene         = logic.getCurrentScene()
ship          = scene.objects["Ship"]
navigation    = scene.objects["Navigation"]
target_marker = scene.objects["Target_marker"]



# Коллекция целей
class Targets:
	def __init__(self):
		self.targets = []
		
		
	#!!!!! Временный метод
	def reset_targets(self):
		self.targets = []
		
	def load_targets(self, targets_number = 1):
		#!!!!! Заменить на загрузку из файла
		targets = []
		
		while len(targets) < targets_number:
			targets.append([
				random.uniform(-30, 30),
				random.uniform(-30, 30),
				random.uniform(-10, -5)
			])
			
		self.targets += targets
		
		#!!!!! True - загружено targets_number целей
		#!!!!! 	Если не получилось загрузить хотя бы одну цель,
		#!!!!! 	то нужно откатить все загруженные и вернуть False
		return True
		
		
	def get_current_target(self):
		if self.targets:
			has_target = True
		else:
			has_target = self.load_targets()
			
		if has_target:
			target = self.targets[0]
		else:
			target = None
			
		return target
		
	def get_future_target(self, target_offset = 1):
		if len(self.targets) > target_offset:
			has_target = True
		else:
			has_target = \
				self.load_targets(
					target_offset - len(self.targets) + 1
				)
				
		if has_target:
			target = self.targets[target_offset]
		else:
			target = None
			
		return target
		
	def confirm_current_target(self):
		if self.targets:
			has_target = True
		else:
			has_target = self.load_targets()
			
		if has_target:
			self.targets.pop(0)
		else:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
			
# Функции управления
def generate_control():
	return control.generate_control(
		15,
		[
			"ship_x_world_position",
			"ship_y_world_position",
			"ship_z_world_position",
			"ship_x_world_orientation",
			"ship_y_world_orientation",
			"ship_z_world_orientation",
			"target_x_world_position",
			"target_y_world_position",
			"target_z_world_position",
			"target_x_local_position",
			"target_y_local_position",
			"horizontal_angle",
			"target_z_local_position"
		]
	)
	
	
targets             = Targets()
boosters_controls   = Controls(generate_control, 10, 5, 0.1)
top_engine_controls = Controls(generate_control, 10, 5, 0.1)




#class Test
# Данные тестирования функций управления
confirmed_targets_number = [0] #!!!!!
tests_number             = [1] #!!!!!

ship_transitional_position = [ship.worldPosition.copy()]
ship_accumulated_distance  = [0.0]

test_tic      = [0]
test_stop_tic = 500


def update_ship_engines_forces():
	# Определение цели
	def is_target_achieved(target):
		if target:
			distance, _, _ = ship.getVectTo(target)
			
			is_target_achieved = \
				distance <= navigation["confirming_distance"]
		else:
			is_target_achieved = False
			
		return is_target_achieved
		
		
	target = targets.get_current_target()
	
	while is_target_achieved(target):
		ship_accumulated_distance[0] += \
			(Vector(target) - ship_transitional_position[0]).magnitude \
				- (Vector(target) - ship.worldPosition).magnitude
				
		ship_transitional_position[0] = ship.worldPosition.copy()
		
		targets.confirm_current_target()
		target = targets.get_current_target()
		
		confirmed_targets_number[0] += 1 #!!!!!
		
		
	# Вычисление сил винтов
	if target:
		target_marker.worldPosition = target
		
		# Тестирование функций управления
		if test_tic[0] == 0:
			a = boosters_controls.get_test_control()
			b = top_engine_controls.get_test_control()
			print("\n\n\n----------------------------")
			print("Испытание:           %s" % tests_number[0])
			print("Функция маршевых двигателей:\n  %s" % str(a).expandtabs(2).replace("\n", "\n  "))
			print("\n")
			print("Функция двигателя вертикальной тяги:\n  %s" % str(b).expandtabs(2).replace("\n", "\n  "))
			print("\n")

		test_tic[0] += 1

		if test_tic[0] == test_stop_tic:
			test_result = \
				ship_accumulated_distance[0] \
					+ (Vector(target) - ship_transitional_position[0]).magnitude \
					- (Vector(target) - ship.worldPosition).magnitude
					
			print("Достигнуто целей:    %s" % confirmed_targets_number[0])
			#print("Расстояние до цели:  %s" % distance)
			print("Результат испытания: %s" % test_result)

			tests_number[0] += 1 #!!!!!
			
			boosters_controls.set_test_control_result(test_result)
			top_engine_controls.set_test_control_result(test_result)
			
			ship_transitional_position[0] = ship.worldPosition.copy()
			ship_accumulated_distance[0]  = 0.0
			test_tic[0]                   = 0
			ship.position = [0,0,0]
			ship.orientation = [0,0,0]
			ship.angularVelocity = [0,0,0]
			ship.linearVelocity = [0,0,0]
			targets.reset_targets()
			
		#horizontal_angle = math.asin(local_target_course.x / local_target_course.magnitude)
		#if local_target_course.y < 0:
		#	if horizontal_angle >= 0:
		#		horizontal_angle = math.pi - horizontal_angle
		#	else:
		#		horizontal_angle = -math.pi - horizontal_angle
		#		
		#		
		#if horizontal_angle > (math.pi / 2):
		#	relative_right_engine_force = -1 / (1 + math.exp(-8 * (horizontal_angle - 3 * math.pi / 4)))
		#else:
		#	relative_right_engine_force = 1 / (1 + math.exp(5 * (horizontal_angle - math.pi / 4)))
		#	
		#if horizontal_angle < (-math.pi / 2):
		#	relative_left_engine_force = -1 / (1 + math.exp(-8 * (-horizontal_angle - 3 * math.pi / 4)))
		#else:
		#	relative_left_engine_force = 1 / (1 + math.exp(5 * (-horizontal_angle - math.pi / 4)))
		#	
		#relative_top_engine_force = \
		#	2 / (1 + 1 * math.exp(-5 * distance * local_target_course.z)) - 1
		#	
		#	
		# Подготовка аргументов для функции управления
		def get_arguments():
			ship_position    = ship.worldPosition
			ship_orientation = ship.worldOrientation.to_euler()
			ship_orientation = Vector([ship_orientation.x, ship_orientation.y, ship_orientation.z])
			distance, _, local_target_course = ship.getVectTo(target)
			target_position  = distance * local_target_course #Vector(target)
			
			horizontal_angle = math.asin(local_target_course.x / local_target_course.magnitude)
			if local_target_course.y < 0:
				if horizontal_angle >= 0:
					horizontal_angle = math.pi - horizontal_angle
				else:
					horizontal_angle = -math.pi - horizontal_angle
			arguments = \
				{
					"ship_x_world_position"    : ship_position.x,
					"ship_y_world_position"    : ship_position.y,
					"ship_z_world_position"    : ship_position.z,
					"ship_x_world_orientation" : ship_orientation.x,
					"ship_y_world_orientation" : ship_orientation.y,
					"ship_z_world_orientation" : ship_orientation.z,
					"target_x_world_position"  : target_position.x,
					"target_y_world_position"  : target_position.y,
					"target_z_world_position"  : target_position.z,
					"target_x_local_position" : target_position.x,
					"target_y_local_position" : target_position.y,
					"horizontal_angle"        : horizontal_angle,
					"target_z_local_position" : target_position.z,
				}
				
			inverse_arguments = \
				{
					"ship_x_world_position"    : ship_position.x,
					"ship_y_world_position"    : ship_position.y,
					"ship_z_world_position"    : ship_position.z,
					"ship_x_world_orientation" : ship_orientation.x,
					"ship_y_world_orientation" : ship_orientation.y,
					"ship_z_world_orientation" : ship_orientation.z,
					"target_x_world_position"  : target_position.x,
					"target_y_world_position"  : target_position.y,
					"target_z_world_position"  : target_position.z,
					"target_x_local_position" : - target_position.x,
					"target_y_local_position" :   target_position.y,
					"horizontal_angle"        : - horizontal_angle,
					"target_z_local_position" :   target_position.z,
				}
				
			return arguments, inverse_arguments
			
		arguments, inverse_arguments = get_arguments()
		
		
		
		a = boosters_controls.get_test_control()
		b = top_engine_controls.get_test_control()
		
		# Установка сил винтов
		try:
			set_ship_right_engine_force(a.invoke(arguments)) #relative_right_engine_force)
			set_ship_left_engine_force(a.invoke(inverse_arguments)) #relative_left_engine_force)
			set_ship_top_engine_force(b.invoke(arguments)) #relative_top_engine_force)
		except:
			boosters_controls.set_test_control_result(None)
			top_engine_controls.set_test_control_result(None)
	else:
		# Выключение двигателей
		switch_off_ship_right_engine()
		switch_off_ship_left_engine()
		switch_off_ship_top_engine()
		