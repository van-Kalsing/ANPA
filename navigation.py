from bge       import logic
from mathutils import Vector, Matrix
from ship      import set_ship_right_engine_force, \
						set_ship_left_engine_force, \
						set_ship_top_engine_force
import control
import math
import random



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
			[[random.uniform(-30,30), random.uniform(-30,30), -5],]# [40, 25, -5]] #[-30, -30, 0], [30, -30, -5], [-30, 30, 0]]
			
		for target in targets:
#			target_marker               = scene.addObject("Target_marker", "Target_marker")
			target_marker = scene.objects["Target_marker"]
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
	
	
class Controls:
	def __init__(self, population_size, generated_controls_number, control_mutation_probability):
		self.population_size              = population_size
		self.generated_controls_number    = generated_controls_number
		self.control_mutation_probability = control_mutation_probability
		self.control_tests_number         = 3 #!!!!!
		
		self.untested_controls = \
			[(generated_control, []) for generated_control
				in self.generate_controls(population_size)]
		self.tested_controls   = []
		self.test_control      = self.untested_controls.pop(0)
		
		
	def get_test_control(self):
		test_control, test_control_results = self.test_control
		
		return test_control
		
	def set_test_control_result(self, test_control_result):
		# Сохранение результатов тестируемой функции управления
		test_control, test_control_results = \
			self.test_control
			
		test_control_results.append(test_control_result)
		
		if len(test_control_results) == self.control_tests_number:
			# Вычисление среднего результата тестируемой функции управления
			test_control_results = \
				[test_control_result for test_control_result in test_control_results
					if test_control_result is not None]
					
			if test_control_results:
				test_control_result = sum(test_control_results) / len(test_control_results)
			else:
				test_control_result = None
				
			self.tested_controls.append((test_control, test_control_result))
		else:
			self.untested_controls.append((test_control, test_control_results))
			
			
		# Создание нового поколения функций управления
		if not self.untested_controls:
			untested_controls = []
			
			try:
				# Скрещивание функций управления
				untested_controls += \
					self.reproduce_controls(
						self.tested_controls,
						self.generated_controls_number,
						self.control_mutation_probability
					)
			except:
				# Генерация случайных функций управления,
				# 	т.к. отсутствуют функции пригодные для скрещивания
				untested_controls += \
					self.generate_controls(self.generated_controls_number)
					
			# Селекция функций управления
			untested_controls += \
				self.select_controls(
					self.tested_controls,
					self.population_size
				)
				
				
			self.tested_controls   = []
			self.untested_controls = \
				[(untested_control, []) for untested_control in untested_controls]
				
				
		# Выбор новой тестируемой функции управления
		untested_control_number = \
			random.randint(0, len(self.untested_controls) - 1)
			
		self.test_control = self.untested_controls.pop(untested_control_number)
		
		
		
	# Генерация случайных функций управления
	def generate_controls(self, controls_number):
		controls = []
		
		while len(controls) < controls_number:
			controls.append(generate_control())
			
		return controls
		
	# Отбор функций управления
	def select_controls(self, tested_controls, population_size):
		def measure_control(tested_control):
			_, tested_control_result = tested_control
			
			if tested_control_result is None:
				tested_control_result = 0.0
				#!!!!! Добавить позже
				#else:
				#	tested_control_result = abs(tested_control_result)
				
			return tested_control_result
			
			
		controls = sorted(tested_controls, key = measure_control, reverse = True)
		controls = \
			[control for control, control_result in controls
				if control_result is not None]
				
		if len(controls) < population_size:
			controls += \
				self.generate_controls(
					population_size - len(controls)
				)
		else:
			controls = controls[0:population_size]
			
		return controls
		
	# Скрещивание функций управления
	def reproduce_controls(self, tested_controls, generated_controls_number, control_mutation_probability):
		# Фильтрация работоспособных функций управления
		tested_controls = \
			[(control, control_result) for control, control_result in tested_controls
				if control_result is not None]
				
				
		# Число родительских функций управления
		controls_number = len(tested_controls)
		
		if controls_number == 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		# Выбор функции управления в соответствии с заданным законом распределния вероятностей
		def choose_control(controls_probability_distribution):
			chosen_control                   = None
			accumulated_controls_probability = 0.0
			sample                           = random.random()
			
			
			for control, control_probability in controls_probability_distribution:
				if control_probability != 0.0:
					accumulated_controls_probability += control_probability
					
					if accumulated_controls_probability >= sample:
						chosen_control = control
						break
						
			# Добавлено на случай влияния ошибки округления, когда суммарная вероятность меньше 1;
			# 	в этом случае за результат принимается последняя функция управления,
			# 	вероятность выбора которой отлична от нуля
			if chosen_control is None:
				for control, control_probability in controls_probability_distribution[::-1]:
					if control_probability != 0.0:
						chosen_control = control
						break
						
						
			return chosen_control
			
			
		# Определение наихудшего и наилучшего результатов
		_, min_control_result = tested_controls[0]
		_, max_control_result = tested_controls[0]
		total_controls_result  = 0.0
		
		for _, controls_result in tested_controls[1:]:
			if controls_result < min_control_result:
				min_control_result = controls_result
				
			if controls_result > max_control_result:
				max_control_result = controls_result
				
			total_controls_result += controls_result
			
		total_controls_result -= controls_number * min_control_result
		
		
		
		# Вычисление вероятностей функций управления стать родителем
		controls_probability_distribution = []
		
		if min_control_result == max_control_result:
			# Равномерное распределение вероятностей
			control_probability = 1.0 / controls_number
			
			for control, _ in tested_controls:
				controls_probability_distribution.append(
					(control, control_probability)
				)
		else:
			# Вероятность пропорциональна вкладу функции в общую сумму
			for control, control_result in tested_controls:
				control_probability = \
					(control_result - min_control_result) \
						/ total_controls_result
						
				controls_probability_distribution.append(
					(control, control_probability)
				)
				
				
				
		# Генерация новых функций управления
		generated_controls = []
		
		while len(generated_controls) < generated_controls_number:
			# Выбор родительской пары функций управления
			first_control, second_control = \
				choose_control(controls_probability_distribution), \
					choose_control(controls_probability_distribution)
					
			# Скрещивание функций управления
			sample = random.random()
			
			control = \
				reproduce_controls(
					first_control,
					second_control,
					sample < control_mutation_probability
				)
				
				
			generated_controls.append(control)
			
			
		return generated_controls
		
		
boosters_controls   = Controls(10, 5, 0.1)
top_engine_controls = Controls(10, 5, 0.1)



# Данные тестирования функций управления
confirmed_targets_number = [0] #!!!!!
tests_number             = [1] #!!!!!

ship_transitional_position = [ship.worldPosition.copy()]
ship_accumulated_distance  = [0.0]

test_tic      = [0]
test_stop_tic = 500


def update_ship_engines_forces():
	# Определение цели
	has_target = False
	
	while targets.has_unconfirmed_targets():
		target                           = targets.get_current_target()
		distance, _, local_target_course = ship.getVectTo(target)
		
		# Определение достижения цели
		if distance <= navigation["confirming_distance"]:
			confirmed_targets_number[0] += 1 #!!!!!
			
			ship_accumulated_distance[0] += \
				(Vector(target) - ship_transitional_position[0]).magnitude \
					- (Vector(target) - ship.worldPosition).magnitude
					
			ship_transitional_position[0] = ship.worldPosition.copy()
			
			
			targets.confirm_current_target()
			
			if (not targets.has_unconfirmed_targets()) and navigation["looping_toggle"]:
				targets.reset_targets()
		else:
			has_target = True
			break
			
			
			
	# Вычисление сил винтов
	if has_target:
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
			print("Расстояние до цели:  %s" % distance)
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
					#"ship_x_world_position"    : ship_position.x,
					#"ship_y_world_position"    : ship_position.y,
					#"ship_z_world_position"    : ship_position.z,
					#"ship_x_world_orientation" : ship_orientation.x,
					#"ship_y_world_orientation" : ship_orientation.y,
					#"ship_z_world_orientation" : ship_orientation.z,
					#"target_x_world_position"  : target_position.x,
					#"target_y_world_position"  : target_position.y,
					#"target_z_world_position"  : target_position.z
					#"target_x_local_position" : target_position.x,
					#"target_y_local_position" : target_position.y,
					"horizontal_angle"        : horizontal_angle,
					"target_z_local_position" : target_position.z
				}
				
			inverse_arguments = \
				{
					#"ship_x_world_position"    : ship_position.x,
					#"ship_y_world_position"    : ship_position.y,
					#"ship_z_world_position"    : ship_position.z,
					#"ship_x_world_orientation" : ship_orientation.x,
					#"ship_y_world_orientation" : ship_orientation.y,
					#"ship_z_world_orientation" : ship_orientation.z,
					#"target_x_world_position"  : target_position.x,
					#"target_y_world_position"  : target_position.y,
					#"target_z_world_position"  : target_position.z
					#"target_x_local_position" : - target_position.x,
					#"target_y_local_position" :   target_position.y,
					"horizontal_angle"        : - horizontal_angle,
					"target_z_local_position" :   target_position.z
				}
				
			return arguments, inverse_arguments
			
		arguments, inverse_arguments = get_arguments()
		
		
		
		a = boosters_controls.get_test_control()
		b = top_engine_controls.get_test_control()
		#c,d,e = \
		#	(0.25 - 0.01 * arguments["target_x_local_position"]) * arguments["target_y_local_position"], \
		#		(0.25 + 0.01 * arguments["target_x_local_position"]) * arguments["target_y_local_position"], \
		#		0.1 * arguments["target_z_local_position"]
		#c = max(min(c, 1), -1)
		#d = max(min(d, 1), -1)
		#e = max(min(e, 1), -1)
		# Установка сил винтов
		try:
			set_ship_right_engine_force(a.invoke(arguments)) #relative_right_engine_force)
			set_ship_left_engine_force(a.invoke(inverse_arguments)) #relative_left_engine_force)
			set_ship_top_engine_force(b.invoke(arguments)) #relative_top_engine_force)
			#set_ship_right_engine_force(c)
			#set_ship_left_engine_force(d)
			#set_ship_top_engine_force(e)
		except:
			boosters_controls.set_test_control_result(None)
			top_engine_controls.set_test_control_result(None)
	else:
		# Выключение двигателей
		set_ship_right_engine_force(0) #relative_right_engine_force)
		set_ship_left_engine_force(0) #relative_left_engine_force)
		set_ship_top_engine_force(0) #relative_top_engine_force)
		
