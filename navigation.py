from bge                 import logic
from mathutils           import Vector, Matrix
from controlOptimization import ControlOptimizer
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



# Источник целей
class TargetsSource:
	def __init__(self):
		self.targets = []
		
		
	#!!!!! Временный метод
	def reset_targets(self):
		self.targets = []
		
	def load_targets(self, targets_number = 1):
		#!!!!! Заменить на загрузку из файла
		targets = []
		
		while len(targets) < targets_number:
			targets.append(
				Vector([
					random.uniform(-30, 30),
					random.uniform(-30, 30),
					random.uniform(-10, -5)
				])
			)
			
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
			
			
			
class Test:
	def __init__(self,
					final_tic_number,
					control_optimizer_factory,
					update_ship_engines_forces):
		#
		self.targets_source             = TargetsSource()
		self.final_tic_number           = final_tic_number
		self.boosters_controls          = control_optimizer_factory()
		self.top_engine_controls        = control_optimizer_factory()
		self.update_ship_engines_forces = update_ship_engines_forces
		
		# Статистика за все время тестирования
		self.finished_tests_number    = 0
		
		# Данные испытания
		self.tics_number              = 0
		self.last_target              = None
		self.last_target_distance     = None
		self.accumulated_movement     = 0.0
		self.confirmed_targets_number = 0
		
		
	def navigate_ship(self):
		if self.last_target:
			# Определение приращения расстояния до цели предыдущего шага
			self.accumulated_movement += \
				self.last_target_distance \
					- (self.last_target - ship.worldPosition).magnitude
					
					
		self.tics_number += 1
		
		if self.tics_number != self.final_tic_number:
			if self.tics_number == 1:
				self.targets_source.reset_targets()
				
				self.last_target              = None
				self.last_target_distance     = None
				self.accumulated_movement     = 0.0
				self.confirmed_targets_number = 0
				
				ship.position        = [0.0, 0.0, 0.0]
				ship.orientation     = [0.0, 0.0, 0.0]
				ship.angularVelocity = [0.0, 0.0, 0.0]
				ship.linearVelocity  = [0.0, 0.0, 0.0]
				
				
				# Вывод информации о новом тесте
				#!!!!!
				a = self.boosters_controls.get_test_control()
				b = self.top_engine_controls.get_test_control()
				print("\n\n")
				print("----------------------------")
				print("Номер испытания: %s\n" % self.finished_tests_number)
				print("Функция маршевых двигателей:\n  %s\n" % str(a).expandtabs(2).replace("\n", "\n  "))
				print("Функция двигателя вертикальной тяги:\n  %s\n" % str(b).expandtabs(2).replace("\n", "\n  "))
				
				
				
			def is_target_achieved(target):
				if target:
					target_distance = (target - ship.worldPosition).magnitude
					
					is_target_achieved = \
						target_distance <= navigation["confirming_distance"]
				else:
					is_target_achieved = False
					
				return is_target_achieved
				
				
			target = self.targets_source.get_current_target()
			
			while is_target_achieved(target):
				self.targets_source.confirm_current_target()
				self.confirmed_targets_number += 1
				
				target = self.targets_source.get_current_target()
				
				
			if target:
				target_marker.worldPosition = [target.x, target.y, target.z]
				target_marker.visible       = True
				
				self.last_target          = target
				self.last_target_distance = (target - ship.worldPosition).magnitude
			else:
				target_marker.visible = False
				
				self.last_target          = None
				self.last_target_distance = None
				
				
			try:
				self.update_ship_engines_forces(
					target,
					self.boosters_controls.get_test_control(),
					self.top_engine_controls.get_test_control()
				)
			except:
				self.boosters_controls.set_test_control_result(None)
				self.top_engine_controls.set_test_control_result(None)
				
				self.finished_tests_number += 1
				self.tics_number            = 0
				
				
				# Вывод результатов завершенного теста
				#!!!!!
				print("Результат испытания: -")
				print("Достигнуто целей:    -")
		else:
			self.boosters_controls.set_test_control_result(self.accumulated_movement)
			self.top_engine_controls.set_test_control_result(self.accumulated_movement)
			
			self.finished_tests_number += 1
			self.tics_number            = 0
			
			
			# Вывод результатов завершенного теста
			#!!!!!
			print("Результат испытания: %s" % self.accumulated_movement)
			print("Достигнуто целей:    %s" % self.confirmed_targets_number)
			
			
			
#!!!!! Дальше нужно править
def generate_control_optimizer():
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
				"target_x_local_position",
				"target_y_local_position",
				"target_z_local_position"
				"horizontal_angle",
			]
		)
		
	return ControlOptimizer(generate_control, 10, 5, 0.1)
	
	
def update_ship_engines_forces(target, boosters_control, top_engine_control):
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
	
	
	
	if target:
		ship_position    = ship.worldPosition
		ship_orientation = ship.worldOrientation.to_euler()
		ship_orientation = Vector([ship_orientation.x, ship_orientation.y, ship_orientation.z])
		distance, _, local_target_course = ship.getVectTo([target.x, target.y, target.z])
		target_position  = distance * local_target_course
		
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
				"target_x_local_position" : target_position.x,
				"target_y_local_position" : target_position.y,
				"target_z_local_position" : target_position.z,
				"horizontal_angle"        : horizontal_angle,
			}
			
		inverse_arguments = \
			{
				"ship_x_world_position"    : ship_position.x,
				"ship_y_world_position"    : ship_position.y,
				"ship_z_world_position"    : ship_position.z,
				"ship_x_world_orientation" : ship_orientation.x,
				"ship_y_world_orientation" : ship_orientation.y,
				"ship_z_world_orientation" : ship_orientation.z,
				"target_x_local_position" : - target_position.x,
				"target_y_local_position" :   target_position.y,
				"target_z_local_position" :   target_position.z,
				"horizontal_angle"        : - horizontal_angle,
			}
			
			
		# Установка сил винтов
		try:
			set_ship_right_engine_force(boosters_control.invoke(arguments))
			set_ship_left_engine_force(boosters_control.invoke(inverse_arguments))
			set_ship_top_engine_force(top_engine_control.invoke(arguments))
		except:
			raise Exception() #!!!!! Создавать внятные исключения
	else:
		# Выключение двигателей
		switch_off_ship_right_engine()
		switch_off_ship_left_engine()
		switch_off_ship_top_engine()
		
		
		
test = Test(500, generate_control_optimizer, update_ship_engines_forces)
navigate_ship = test.navigate_ship
