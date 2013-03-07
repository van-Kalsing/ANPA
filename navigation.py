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



# Функции управления
def generate_control():
	return control.generate_control(
		15,
		[
			"ship_x_position",
			"ship_y_position",
			"ship_z_position",
			"ship_x_orientation",
			"ship_y_orientation",
			"ship_z_orientation",
			"target_x_position",
			"target_y_position",
			"target_z_position"
		]
	)
	
	
class Controls:
	def __init__(self, population_size, generated_controls_number, controls_mutation_probability):
		self.population_size               = population_size
		self.generated_controls_number     = generated_controls_number
		self.controls_mutation_probability = controls_mutation_probability
		
		self.untested_controls = self.generate_controls(population_size)
		self.tested_controls   = []
		self.test_controls     = self.untested_controls.pop(0)
		
		
	def get_test_controls(self):
		return self.test_controls
		
	def set_test_controls_result(self, controls_result):
		self.tested_controls.append((self.test_controls, controls_result))
		
		if self.untested_controls:
			self.test_controls = self.untested_controls.pop(0)
		else:
			if len(self.tested_controls) > self.population_size:
				self.untested_controls = \
					self.select_controls(self.tested_controls, self.population_size)
				self.tested_controls = []
			else:
				try:
					self.untested_controls = \
						self.reproduce_controls(
							self.tested_controls,
							self.generated_controls_number,
							self.controls_mutation_probability
						)
				except:
					self.untested_controls = self.generate_controls(self.population_size)
					
			self.test_controls = self.untested_controls.pop(0)
			
			
	# Генерация случайных функций управления
	def generate_controls(self, controls_number):
		controls = []
		
		while len(controls) < controls_number:
			controls.append(
				(generate_control(), generate_control())
			)
			
		return controls
		
	# Отбор функций управления
	def select_controls(self, tested_controls, population_size):
		def measure_controls(controls):
			controls, controls_result = controls
			
			if controls_result is None:
				controls_result = 0.0
				
			return controls_result
			
			
		untested_controls = sorted(tested_controls, key = measure_controls, reverse = True)
		untested_controls = \
			[controls for controls, controls_result in untested_controls
				if controls_result is not None]
				
		if len(untested_controls) < population_size:
			untested_controls += \
				self.generate_controls(
					population_size - len(untested_controls)
				)
		else:
			untested_controls = untested_controls[0:population_size]
			
		return untested_controls
		
	# Скрещивание функций управления
	def reproduce_controls(self, tested_controls, generated_controls_number, controls_mutation_probability):
		# Фильтрация работоспособных функций управления
		tested_controls = \
			[(controls, controls_result) for controls, controls_result in tested_controls
				if controls_result is not None]
				
				
		# Число родительских функций управления
		controls_number = len(tested_controls)
		
		if controls_number == 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		# Выбор функции управления в соответствии с заданным законом распределния вероятностей
		def choose_controls(controls_probability_distribution):
			chosen_controls                  = None
			accumulated_controls_probability = 0.0
			sample                           = random.random()
			
			
			for controls, controls_probability in controls_probability_distribution:
				if controls_probability != 0.0:
					accumulated_controls_probability += controls_probability
					
					if accumulated_controls_probability >= sample:
						chosen_controls = controls
						break
						
			# Добавлено на случай влияния ошибки округления, когда суммарная вероятность меньше 1;
			# 	в этом случае за результат принимается последняя функция управления,
			# 	вероятность выбора которой отлична от нуля
			if chosen_controls is None:
				for controls, controls_probability in controls_probability_distribution[::-1]:
					if controls_probability != 0.0:
						chosen_controls = controls
						break
						
						
			return chosen_controls
			
			
		# Определение наихудшего и наилучшего результатов
		_, min_controls_result = tested_controls[0]
		_, max_controls_result = tested_controls[0]
		total_controls_result  = 0.0
		
		for _, controls_result in tested_controls[1:]:
			if controls_result < min_controls_result:
				min_controls_result = controls_result
				
			if controls_result > max_controls_result:
				max_controls_result = controls_result
				
			total_controls_result += controls_result
			
		total_controls_result -= controls_number * min_controls_result
		
		
		
		# Вычисление вероятностей функций управления стать "родителем"
		controls_probability_distribution = []
		
		if min_controls_result == max_controls_result:
			# Равномерное распределение вероятностей
			controls_probability = 1.0 / controls_number
			
			for controls, _ in tested_controls:
				controls_probability_distribution.append(
					(controls, controls_probability)
				)
		else:
			# Вероятность пропорциональна вкладу функции в общую сумму
			for controls, controls_result in tested_controls:
				controls_probability = \
					(controls_result - min_controls_result) \
						/ total_controls_result
						
				controls_probability_distribution.append(
					(controls, controls_probability)
				)
				
				
				
		# Генерация новых функций управления
		def reproduce_controls(first_control, second_control, control_mutation_probability):
			sample = random.random()
			
			return controls.reproduce_controls(
				first_control,
					second_control,
					sample < control_mutation_probability
			)
			
			
		generated_controls = []
		
		while len(generated_controls) < generated_controls_number:
			# Выбор "родительской" пары функций управления
			first_controls, second_controls = \
				choose_controls(controls_probability_distribution), \
					choose_controls(controls_probability_distribution)
					
			# Вычисление вероятности мутации одной компоненты функции управления
			# 	(считаем эти события равновероятными)
			control_mutation_probability = 1 - controls_mutation_probability ** 0.5
			
			# Скрещивание функций управления
			controls = (
				reproduce_controls(first_controls[0], second_controls[0], control_mutation_probability),
					reproduce_controls(first_controls[1], second_controls[1], control_mutation_probability)
			)
			
			generated_controls.append(controls)
			
			
		return generated_controls
		
		
controls = Controls(10, 5, 0.1)



# Данные тестирования функций управления
ship_transitional_position = [ship.worldPosition.copy()]
ship_accumulated_distance  = [0.0]

test_tic      = [0]
test_stop_tic = 150


def update_ship_engines_forces():
	# Определение цели
	has_target = False
	
	while targets.has_unconfirmed_targets():
		target                           = targets.get_current_target()
		distance, _, local_target_course = ship.getVectTo(target)
		
		# Определение достижения цели
		if distance <= navigation["confirming_distance"]:
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
		test_tic[0] += 1
		
		if test_tic[0] == test_stop_tic:
			controls.set_test_controls_result(
				ship_accumulated_distance[0] \
					+ (Vector(target) - ship_transitional_position[0]).magnitude \
					- (Vector(target) - ship.worldPosition).magnitude
			)
			print(
				ship_accumulated_distance[0] \
					+ (Vector(target) - ship_transitional_position[0]).magnitude \
					- (Vector(target) - ship.worldPosition).magnitude
			)
			
			ship_transitional_position[0] = ship.worldPosition.copy()
			ship_accumulated_distance[0]  = 0.0
			test_tic[0]                   = 0
			
			
			
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
			
			
		# Подготовка аргументов для функции управления
		def get_arguments():
			def get_arguments(ship_position, ship_orientation, target_position):
				return {
					"ship_x_position"    : ship_position.x,
					"ship_y_position"    : ship_position.y,
					"ship_z_position"    : ship_position.z,
					"ship_x_orientation" : ship_orientation.x,
					"ship_y_orientation" : ship_orientation.y,
					"ship_z_orientation" : ship_orientation.z,
					"target_x_position"  : target_position.x,
					"target_y_position"  : target_position.y,
					"target_z_position"  : target_position.z
				}
				
			ship_position    = ship.worldPosition
			ship_orientation = ship.worldOrientation.to_euler()
			ship_orientation = Vector([ship_orientation.x, ship_orientation.y, ship_orientation.z])
			target_position  = Vector(target)
			
			return (
				get_arguments(ship_position, ship_orientation, target_position),
					get_arguments(-1.0 * ship_position, -1.0 * ship_orientation, -1.0 * target_position),
			)
			
		arguments, inverse_arguments = get_arguments()
		
		
		
		a,b = controls.get_test_controls()
		# Установка сил винтов
		try:
			set_ship_right_engine_force(a.invoke(arguments)) #relative_right_engine_force)
			set_ship_left_engine_force(a.invoke(inverse_arguments)) #relative_left_engine_force)
			set_ship_top_engine_force(b.invoke(arguments)) #relative_top_engine_force)
		except:
			controls.set_test_controls_result(None)
	else:
		# Выключение двигателей
		switch_off_ship_right_engine_force()
		switch_off_ship_left_engine_force()
		switch_off_ship_top_engine_force()
		