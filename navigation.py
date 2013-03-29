from bge                 import logic
from mathutils           import Vector, Matrix
from controlOptimization import ControlOptimizer, ControlsPopulation #!!!!!
from ship                import set_ship_right_engine_force,      \
									set_ship_left_engine_force,   \
									set_ship_top_engine_force,    \
									switch_off_ship_right_engine, \
									switch_off_ship_left_engine,  \
									switch_off_ship_top_engine,   \
									reset_ship_state
									
import control
import math
import random



#!!!!! Временно
need_logging     = False # Включение логирования
targets_x_limits = 25, 30
targets_y_limits = 25, 30
targets_z_limits = -6, -5


# Получение объектов модели
scene         = logic.getCurrentScene()
ship          = scene.objects["Ship"]
navigation    = scene.objects["Navigation"]
target_marker = scene.objects["Target_marker"]



# Источники целей
class RandomTargetsSource(TargetsSource):
	def load_targets(self, targets_number):
		if targets_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		targets = []
		
		while len(targets) < targets_number:
			targets.append(
				Vector([
					random.uniform(*targets_x_limits),
					random.uniform(*targets_y_limits),
					random.uniform(*targets_z_limits)
				])
			)
			
		self.targets += targets
		
		
		
		
		
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
		
	control_optimizer = \
		ControlOptimizer(
			control_factory              = generate_control,
			selected_controls_number     = 10,
			reproduced_controls_number   = 5,
			control_mutation_probability = 0.1,
			control_tests_number         = 3
		)
		
	return control_optimizer
	
	
def update_ship_engines_force(target,
								right_engine_control,
								left_engine_control,
								top_engine_control):
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
			
			
		# Установка сил винтов
		try:
			set_ship_right_engine_force(right_engine_control.invoke(arguments))
			set_ship_left_engine_force(left_engine_control.invoke(arguments))
			set_ship_top_engine_force(top_engine_control.invoke(arguments))
		except:
			raise Exception() #!!!!! Создавать внятные исключения
	else:
		# Выключение двигателей
		switch_off_ship_right_engine()
		switch_off_ship_left_engine()
		switch_off_ship_top_engine()
		
		
		
test = \
	Test(
		final_tic_number          = 100,
		control_optimizer_factory = generate_control_optimizer, 
		update_ship_engines_force = update_ship_engines_force
	)
	
def navigate_ship():
	