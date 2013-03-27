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
		
		
		
class RevolvingRandomTargetsSource(TargetsSource):
	def __init__(self):
		self.__base_targets_source = RandomTargetsSource()
		self.__base_target_offset  = 0
		
		
	def reset(self):
		self.__target_offset = 0
		
		
	def load_targets(self, targets_number):
		if targets_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		targets_offsets = \
			xrange(
				self.__base_target_offset,
				self.__base_target_offset + targets_number
			)
			
		for target_offset in targets_offsets:
			self.targets.append(
				self.__base_targets_source.get_target(target_offset)
			)
			
		self.__base_target_offset += targets_number
		
		
		
#!!!!! -----------------------------------------
reset_ship_state()

a = self.right_engine_controls.get_test_control()
b = self.left_engine_controls.get_test_control()
c = self.top_engine_controls.get_test_control()
print("\n\n")
print("----------------------------")
print("Номер испытания: %s\n" % self.finished_tests_number)
print("Функция правого двигателя:\n  %s\n"           % str(a).expandtabs(2).replace("\n", "\n  "))
print("Функция левого двигателя:\n  %s\n"            % str(b).expandtabs(2).replace("\n", "\n  "))
print("Функция двигателя вертикальной тяги:\n  %s\n" % str(c).expandtabs(2).replace("\n", "\n  "))

#!!!!!
if need_logging:
	f=open("/tmp/log",'a')
	f.write("<tr><td>%s</td><td><pre>%s</pre></td><td><pre>%s</pre></td><td><pre>%s</pre></td>" % (self.finished_tests_number, 
																									str(a).expandtabs(2).replace("\n", "\n  "),
																									str(b).expandtabs(2).replace("\n", "\n  "),
																									str(c).expandtabs(2).replace("\n", "\n  ")))
	f.close()
#!!!!! -----------------------------------------
# class ControlsTesting:
	# def __init__(self,
					# right_engine_control,
					# left_engine_control,
					# top_engine_control,
					# targets_source,
					# test):
		# if test.is_initialized():
			# raise Exception() #!!!!! Создавать внятные исключения
			
		# self.is_interrupted       = False
		# self.right_engine_control = right_engine_control
		# self.left_engine_control  = left_engine_control
		# self.top_engine_control   = top_engine_control
		# self.targets_source       = targets_source
		# self.test                 = test
		
		
	# def is_finished(self):
		# return self.test.is_finished() or self.is_interrupted
		
		
	# def get_result(self):
		# if not self.is_finished():
			# raise Exception() #!!!!! Создавать внятные исключения
			
		# if self.is_interrupted:
			# return None
		# else:
			# return self.test.get_result()
			
			
	# def test(self):
		# if self.is_finished():
			# raise Exception() #!!!!! Создавать внятные исключения
			
			
		# if not self.test.is_initialized():
			# target     = self.targets_source.get_current_target()
			# ship_state = None #!!!!!
			
			# self.test.initialize(ship_state, target)
		# else:
			# def is_target_achieved(target):
				# if target:
					# is_target_achieved = \
						# (target - ship.worldPosition).magnitude \
							# <= navigation["confirming_distance"]
				# else:
					# raise Exception() #!!!!! Создавать внятные исключения
					
				# return is_target_achieved
				
				
			# target     = self.targets_source.get_current_target()
			# ship_state = None #!!!!!
			# delta_time = 1 / logic.getPhysicsTicRate()
			
			# while target and is_target_achieved(target):
				# self.test.measure(ship_state, target, delta_time)
				# self.targets_source.confirm_current_target()
				
				# target = self.targets_source.get_current_target()
				
			# self.test.measure(ship_state, target, delta_time)
			
			
			# if target:
				# target_marker.worldPosition = [target.x, target.y, target.z]
			# target_marker.visible = bool(target)
			
			
			# try:
				# update_ship_engines_force(
					# target,
					# right_engine_control,
					# left_engine_control,
					# top_engine_control
				# )
			# except:
				# self.is_interrupted = True
				
				
				
class ControlsOptimizer(object):
	__metaclass__ = ABCMeta
	
	
	def __init__(self,
					controls_evolution_parameters,
					check_target_confirmation,
					navigate_ship,
					reset_ship_state,
					control_tests_number,
					controls_names,
					targets_number):
		if control_tests_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
		if tagets_number <= 0:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self.__controls_evolution_parameters = controls_evolution_parameters
		self.__check_target_confirmation     = check_target_confirmation
		self.__navigate_ship                 = navigate_ship
		self.__reset_ship_state              = reset_ship_state
		self.__control_tests_number          = control_tests_number
		self.__controls_names                = frozenset(controls_names)
		self.__targets_number                = targets_number
		
		self.__buffer_controls_complex_population = None
		self.__controls_complex_population        = None
		self.__controls_complex_population_rating = None
		self.__test_complex_control               = None
		self.__test                               = self.__create_test()
		self.__targets_source                     = RevolvingRandomTargetsSource()
		
		
		controls_populations = \
			dict(
				[(control_name, Control()) for control_name
					in self._controls_names]
			)
			
		self.__buffer_controls_complex_population = \
			ControlsComplexPopulation(**controls_populations)
			
		self.__controls_complex_population = \
			ControlsComplexPopulation(**controls_populations)
			
		self.__controls_complex_population_rating = \
			ControlsComplexPopulationRating(
				self.__controls_complex_population,
				self.__control_tests_number
			)
			
			
			
	@abstractmethod
	def __create_test(self):
		pass
		
		
		
	def update_controls_buffer(self, controls_complex_population):
		controls_populations_names = \
			controls_complex_population.controls_populations_names
			
		if controls_populations_names != self.__controls_names:
			raise Exception() #!!!!! Создавать внятные исключения
			
			
		self.__buffer_controls_complex_population = controls_complex_population
		
		
	def get_controls_complex_population(self):
		return self.__controls_complex_population
		
		
		
	def __check_controls_complex_population_completeness(self):
		is_controls_complex_population_full = True
		
		
		needed_controls_population_size = \
			self.__controls_evolution_parameters.get_population_size()
			
		for control_name in self._controls_names:
			controls_population = \
				self.__controls_complex_population.get_controls_population(
					control_name
				)
				
			if len(controls_population) != needed_controls_population_size:
				is_controls_complex_population_full = False
				break
				
				
		return is_controls_complex_population_full
		
		
	def __replenish_controls_complex_population(self):
		buffer_controls_populations = dict()
		controls_populations        = dict()
		
		
		needed_controls_population_size = \
			self.__controls_evolution_parameters.get_population_size()
			
		for control_name in self._controls_names:
			buffer_controls_population = \
				self.__buffer_controls_complex_population.get_controls_population(
					control_name
				)
			buffer_controls = list(buffer_controls_population)
			
			controls_population = \
				self.__controls_complex_population.get_controls_population(
					control_name
				)
			controls = list(controls_population)
			
			
			while len(controls) < needed_controls_population_size:
				if len(buffer_controls) > 0:
					controls.append(
						buffer_controls.pop()
					)
				else:
					break
					
					
			buffer_controls_populations[control_name] = \
				ControlsPopulation(buffer_controls)
				
			controls_populations[control_name] = \
				ControlsPopulation(controls)
				
				
		self.__buffer_controls_complex_population = \
			ControlsComplexPopulation(**buffer_controls_populations)
			
		self.__controls_complex_population = \
			ControlsComplexPopulation(**controls_populations)
			
			
	def iterate(self, ship_state, delta_time):
		if not self.__test_complex_control:
			if not self.__check_controls_complex_population_completeness():
				self.__replenish_controls_complex_population()
				self.__controls_complex_population_rating = \
					ControlsComplexPopulationRating(
						self.__controls_complex_population,
						self.__control_tests_number
					)
					
				if not self.__check_controls_complex_population_completeness():
					raise Exception() #!!!!! Создавать внятные исключения
					
					
			self.__test_complex_control = \
				random.choice(
					self.__controls_complex_population_rating
						.get_unrated_controls_complex_population()
				)
				
			self.__test = self.__create_test()
			
			
			self.__reset_ship_state()
		else:
			target = self.__targets_source.get_current_target()
			
			while True:
				if self.__test.is_initialized():
					self.__test.measure(ship_state, target, delta_time)
				else:
					self.__test.initialize(ship_state, target)
					
					
				if target and not self.__test.is_finished():
					is_target_confirmed = \
						self.__check_target_confirmation(
							ship_state,
							target
						)
						
					if is_target_confirmed:
						self.__targets_source.confirm_current_target()
						
						target     = self.__targets_source.get_current_target()
						delta_time = 0
					else:
						break
				else:
					break
					
					
			if not self.__test.is_finished():
				targets_source_view = \
					TargetsSourceView(
						self.__targets_source,
						self.__targets_number
					)
					
				try:
					self.__navigate_ship(
						self.__test_complex_control,
						targets_source_view
					)
				except:
					self.__controls_complex_population_rating
						.set_complex_control_test_result(
							self.__test_complex_control,
							None
						)
			else:
				self.__controls_complex_population_rating
					.set_complex_control_test_result(
						self.__test_complex_control,
						self.__test.get_result()
					)
					
					
			if self.__test.is_finished():
				has_unrated_controls = \
					self.__controls_complex_population_rating
						.has_unrated_controls()
						
				if not has_unrated_controls:
					self.__controls_complex_population = \
						evolve_complex_controls_population(
							self.__controls_complex_population_rating,
							self.__controls_evolution_parameters
						)
						
					self.__controls_complex_population_rating = \
						ControlsComplexPopulationRating(
							self.__controls_complex_population,
							self.__control_tests_number
						)
						
					self.__targets_source = RevolvingRandomTargetsSource()
				else:
					self.__targets_source.reset()
					
					
				self.__test_complex_control = None
				
				
				
class ControlsOptimizersConveyor(object):
	def __init__(self, controls_optimizers):
		pass
s





















def navigate_ship(population_size, test):
	def generate_controls_population(controls_number):
		controls = []
		
		while len(controls) < controls_number:
			controls.append(
				self.control_factory()
			)
			
		return ControlsPopulation(controls)
		
	right_engine_controls    = generate_controls_population(population_size)
	left_engine_controls     = generate_controls_population(population_size)
	top_engine_controls      = generate_controls_population(population_size)
	test                     = generate_controls_population(population_size)
	targets_source           = TargetsSource()
	confirmed_targets_number = 0
	finished_tests_number    = 0
	
	
	def navigate_ship():
		def is_target_achieved(target):
			if target:
				target_distance = (target - ship.worldPosition).magnitude
				
				is_target_achieved = \
					target_distance <= navigation["confirming_distance"]
			else:
				raise Exception() #!!!!! Создавать внятные исключения
				
			return is_target_achieved
			
			
		target = targets_source.get_current_target()
		
		while target and is_target_achieved(target):
			targets_source.confirm_current_target()
			confirmed_targets_number += 1
			
			target = self.targets_source.get_current_target()
			
			
		if target:
			target_marker.worldPosition = [target.x, target.y, target.z]
			
		target_marker.visible = bool(target)
		
		
		try:
			update_ship_engines_force(
				target,
				right_engine_controls.get_test_control(),
				left_engine_controls.get_test_control(),
				top_engine_controls.get_test_control()
			)
		except:
			right_engine_controls.set_test_control_result(None)
			left_engine_controls.set_test_control_result(None)
			top_engine_controls.set_test_control_result(None)
			
			finished_tests_number += 1
			
			
			# Вывод результатов завершенного теста
			#!!!!!
			print("Результат испытания: -")
			print("Достигнуто целей:    -")
			
			#!!!!!
			if need_logging:
				f=open("/tmp/log",'a')
				f.write("<td>-1000</td><td>0</td></tr>\n")
				f.close()
		else:
			self.right_engine_controls.set_test_control_result(self.accumulated_movement)
			self.left_engine_controls.set_test_control_result(self.accumulated_movement)
			self.top_engine_controls.set_test_control_result(self.accumulated_movement)
			
			self.finished_tests_number += 1
			
			
		# Вывод результатов завершенного теста
		#!!!!!
		print("Результат испытания: %s" % self.accumulated_movement)
		print("Достигнуто целей:    %s" % self.confirmed_targets_number)
		
		#!!!!!
		if need_logging:
			f=open("/tmp/log",'a')
			f.write("<td>%s</td><td>%s</td></tr>\n" % (self.accumulated_movement, self.confirmed_targets_number))
			f.close()
			
			
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
	