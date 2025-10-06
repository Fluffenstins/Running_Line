from math import pi, asin
from kivy.config import Config
Config.set('graphics', 'resizable', True)

from Frontend import Client
from kivy.core.window import Window

from matplotlib import pyplot as plt
from kivy.garden.matplotlib import FigureCanvasKivyAgg

from Line import LineCalculator


class GUI:
	def __init__(self):

		self.calc = LineCalculator()
		self.calc.set_uom('m')

		self.nodes = []

		self.client = Client(bc='#ffffffff')
		Window.size = [700, 400.0]

		self.header = self.client.add_label(line_width=0.2, text='Running Line', hpos=[0.1, 0.86], hsize=[0.375, 0.14], bg_color=[0.4433, 0.7246, 0.7246, 1.0], halign='left', font_size=28)['manager']
		self.header.widget.color = [0.0, 0.0, 0.0, 1]

		# button that adds a node
		self.button2 = self.client.add_button(text='', hpos=[0.35, 0.9], hsize=[0.0357, 0.06], bg_color=[0.4433, 0.7246, 0.7246, 1.0], font_size=17)['manager']
		self.button2.widget.bind(on_press=self.add_node)
		# button that displays
		self.button2 = self.client.add_button(text='', hpos=[0.4, 0.9], hsize=[0.0357, 0.06], bg_color=[0.2433, 0.5246, 0.7246, 1.0], font_size=17)['manager']
		self.button2.widget.bind(on_press=self.render)

		self.scroll = self.client.add_scroll(hpos=[0.6,0.5], hsize=[0.3,0.5])['manager']

		self.output_lbl = self.client.add_label(hpos=[0.6,0.5], hsize=[0.3,0.5], font_size=14, layout=self.scroll)['manager']
		self.output_lbl.draw_background('666666')

		# plot
		self.plot = FigureCanvasKivyAgg(plt.gcf())
		self.client.add_widget(self.plot, hsize=[1, 0.5], hpos=[0, 0.05], z_index=10)

		for point, angle in zip([[0, 0], [80, -5], [200, 0]], [-25, 0, 25]):
			self.add_node()
			self.nodes[-1].x.widget.text = str(point[0])
			self.nodes[-1].y.widget.text = str(point[1])
			self.nodes[-1].theta.widget.text = str(angle)
		# self.calc.calc_line([[0, 0], [80, -10], [200, 0]], [-25, 0, 25])
		# self.display_info()
		self.render()
		# --

		self.client.start()

	def add_node(self, *args):
		node = Node(self.client, self.nodes)
		self.nodes.append(node)
		node.move(len(self.nodes)-1)

	def render(self, *args):
		self.client.remove_widget(self.plot)
		plt.clf()

		points = []
		angles = []

		for node in self.nodes:
			try:
				points.append(node.coords())
			except ValueError:
				print("Empty input detected.")
				return
			angles.append(node.angle())

		if points:
			try:
				self.calc.calc_line(points, angles)
			except ZeroDivisionError:
				print("Bad Input!")

		self.plot = FigureCanvasKivyAgg(plt.gcf())
		self.client.add_widget(self.plot, hsize=[1, 0.5], hpos=[0, 0.05], z_index=10)

		self.display_info()

	def display_info(self):
		self.output_lbl.widget.text = f"Max Angle Change: {round(self.calc.max_delta,2)}°\nNum Rods: {self.calc.num_rods}"
		instructs = []
		prev = None
		for num_rods, rad in self.calc.instructions:
			deg = round(rad*180/pi, 2)

			if deg == 0:
				word = 'Straight'
			else:
				word = f'Curve {deg}°'

			if word == prev:
				instructs[-1][1] += num_rods
			else:
				instructs.append([word, num_rods])
			prev = word

		self.output_lbl.widget.text += '\n\n'
		self.output_lbl.widget.text += '\n'.join([f"{i} {j} rod{'s' if j > 1 else ''}." for i, j in instructs])
		self.output_lbl.widget.text += f"\n\nMax Radius: {round(self.calc.max_radius, 2)}"

		# print at each rod

		prev = [0, 0]
		for rod, angle in zip(self.calc.rods, self.calc.angles):
			mag = sum([(i-j)**2 for i, j in zip(prev, rod)])**0.5
			prev = rod[:]
			# print(self.calc.readable_rod_info(rod, angle, percent=True), mag)


class Node:
	def __init__(self, client, nodes):
		self.client = client
		self.nodes = nodes
		self.pos = 0
		self.angle_type = 2

		self.scroll = self.client.add_scroll(hsize=[0.05,0.3])['manager']

		self.x = self.client.add_input(layout=self.scroll, height=25, font_size=10)['manager']
		self.y = self.client.add_input(layout=self.scroll, height=25, font_size=10)['manager']
		self.theta = self.client.add_input(layout=self.scroll, height=25, font_size=10)['manager']
		# self.client.add_button(text='<', layout=drop['manager'], height=20)
		# self.client.add_button(text='>', layout=drop['manager'], height=20)
		self.del_btn = self.client.add_button(text='x', layout=self.scroll, height=25)['manager']
		self.del_btn.widget.bind(on_press=self.remove)

		self.move(1)

	def remove(self, *args):
		self.client.remove_widget(self.scroll.widget)
		self.nodes.pop(self.pos)
		for n, i in enumerate(self.nodes):
			i.move(n)

	def move(self, n):
		self.scroll.widget.pos_hint = {'x': 0.15+0.08*n, 'y': 0.52}
		self.pos = n

	def angle(self):
		# by default the calculator accepts radians
		# 0: Degrees, 1: rads, 2: percent
		if self.angle_type == 0:
			return float(self.theta.widget.text)
		if self.angle_type == 1:
			return float(self.theta.widget.text) * 180/pi
		if self.angle_type == 2:
			return asin(float(self.theta.widget.text)/100) * 180/pi

	def coords(self):
		return [float(self.x.widget.text), float(self.y.widget.text)]


gui = GUI()
