from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty)
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.effects.scroll import ScrollEffect
from kivy.graphics import Rectangle
from kivy.graphics import Color
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import SlideTransition as NoTransition

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


def render_widget(layout, wid, z_index=0):
    layout.add_widget(wid, index=z_index)


def unrender_widget(app, wid):
    app.layout.remove_widget(wid)


class CoreApp(App):

    def build(self):
        self.title = self.window_title
        self.icon = "Resources/icon.png"

        return self.screen_manager

    def init(self, name="NuBuild"):
        self.widgets = {}
        self.window_title = name

        self.screen_manager = ScreenManager(transition=NoTransition())

        self.main_page = Screen(name='main')
        self.layout = FloatLayout()
        self.main_page.add_widget(self.layout)

        self.screen_manager.add_widget(self.main_page)
        self.screen_manager.current = 'main'


class ManeuverableDropdown:
    def __init__(self, client, max_len=50, pos=(0.0392, 0.8431), size=(0.384, 0.0605), default_text=''):
        self.rcpc_text = ''
        self.max_len = max_len
        self.rcpc_input = client.add_input(text=default_text, hpos=pos, hsize=size,
                                           bg_color=[0.898, 0.898, 0.898, 1.0], font_size=17)['manager']
        self.rcpc_input.widget.foreground_color = [0, 0, 0, 1]
        self.rcpc_d = client.add_dropdown(pos, size=(size[0], size[1]*5), draw=True, hide=True,
                                          highlight=True, cursor_wrap=True)
        self.rcpc_d.button_func = self.button_set_rcpc

        self.rcpc_input.widget.bind(text=self.input_func)
        self.rcpc_input.widget.bind(focus=self.focus)
        self.rcpc_input.widget.bind(on_text_validate=self.valdiate)
        Window.bind(on_key_down=self.rcpc_d.process_key_press)

        # change this to whatever produces the dropdown list
        self.get_list_func = self.get_list

        self.select_func = None

    def input_func(self, instance, *args):
        text = instance.text
        for i in ['\n', '\t']:
            text = text.replace(i, '')

        instance.text = text
        if text != self.rcpc_text:
            self.update_list(text)
            self.rcpc_text = text

    def valdiate(self, *args):
        new_text = self.rcpc_d.items[self.rcpc_d.selected].widget.text
        self.rcpc_input.widget.text = new_text
        if self.select_func:
            self.select_func(new_text)

    def focus(self, instance, focus):
        self.rcpc_d.hide(not focus)
        self.input_func(instance, focus)

    def update_list(self, text):
        self.rcpc_d.init_from_list([str(i[0]) for i in self.get_list_func(text)[:self.max_len]])

    def get_list(self, text):
        ret = []
        return ret

    def button_set_rcpc(self, instance, n):
        self.rcpc_input.widget.text = instance.text
        if self.select_func:
            self.select_func(instance.text)


class ButtonDropdown:
    def __init__(self, client, pos=(0.25, 0.7), size=(0.15, 0.05), text='Location', font_size=17, btn_clr="#DDDDDD", text_clr="#FFFFFFF", options=(), appendable=True):
        self.client = client

        self.button = self.client.add_button(text=text, hpos=pos, hsize=size, bg_color=btn_clr, font_size=font_size)['manager']
        self.button.widget.foreground_color = text_clr
        self.dropdown = self.client.add_dropdown(pos, size=(size[0], size[1]*4), draw=True, hide=True)
        self.dropdown.options = options
        self.dropdown.button_func = self.select_text
        if appendable:
            self.dropdown.add_option_func = self.dropdown.add_from_input
        self.dropdown.init_from_list(self.dropdown.options)

        self.button.widget.bind(on_press=self.hide)

        self.select_func = None

    def hide(self, *args):
        self.dropdown.hide(not self.dropdown.hidden)

    def select_text(self, instance, n):
        self.button.widget.text = instance.text
        self.dropdown.hide(True)
        if self.select_func:
            self.select_func(instance.text)


class Dropdown:
    def __init__(self, client, pos=(0.0333, 0.756), size=(0.2667, 0.3), draw=True, hide=False, bg="#AAAAAA", selected_bg="#BCD8D6", highlight=False, cursor_wrap=False, spacing=1):
        width, height = size
        self.hidden = False
        self.button_select = True
        self.input = None
        self.button_func = None
        self.add_option_func = None
        self.on_init_func = None
        self.options = []
        self.selected = 0
        self.cursor_wrap = cursor_wrap
        self.items = []
        self.max_items = 8
        self.pos = [0.5, 0.5]
        self.size = [width, height]
        self.bg = bg
        self.selected_bg = selected_bg
        self.client = client
        self.highlight = highlight
        self.spacing = spacing
        self.scroll = self.client.add_scroll(hpos=(self.pos[0], self.pos[1]), hsize=(width, height), spacing=self.spacing, layout_width=1)
        self.move(pos)
        if draw:
            self.init_items()
        self.hide(hide)

    def add_from_input(self, instance):
        text = instance
        if text is not str:
            text = instance.text
        self.options.append(text)
        self.init_from_list(self.options)

    def move(self, pos):
        x, y = pos
        y = y - self.size[1]
        self.scroll['manager'].widget.pos_hint = {'x': x, 'y': y}

    def test(self):
        pass

    def init_from_list(self, options):  # , add_option_func=None
        self.max_items = len(options)
        self.init_items()
        ret = []
        for opt, item in zip(options, self.items):
            item.widget.text = opt
            ret.append([opt, item])
        if self.add_option_func:
            inp = self.client.add_input(hsize=(self.size[0], 0), custom=True, text='', layout=self.scroll['manager'], halign='center', bg_color=self.bg)
            inp['widget'].bind(on_text_validate=self.add_option_func)
            inp['widget'].foreground_color = [1, 1, 1, 1]
            self.input = inp
        return ret

    def init_items(self):
        self.clear()
        for i in range(self.max_items):
            button = self.create_option()['manager']
            self.items.append(button)

        if self.highlight:
            self.highlight_line(0)

        if self.on_init_func:
            self.on_init_func()

    def create_option(self):
        text = 'R530856'
        button = self.client.add_button(hsize=(self.size[0],0), text=text, bg_color=self.bg, halign='center', layout=self.scroll['manager'])
        button['widget'].bind(on_press=self.button_clicked)

        return button

    def hide(self, do_hide=True):
        self.hidden = do_hide
        self.scroll['manager'].hide(do_hide)

    def clear(self):
        self.selected = 0
        self.scroll['manager'].layout.clear_widgets()
        del self.items
        del self.input
        self.items = []
        self.input = None

    def deselect(self):
        wid = self.items[self.selected].widget
        wid.background_color = self.bg

    def highlight_line(self, line_idx):
        try:
            wid = self.items[line_idx].widget
            wid.background_color = self.selected_bg
            self.set_scroll(line_idx)
        except IndexError:
            pass

    def get_scroll_space(self):
        try:
            height = self.items[0].widget.height
        except IndexError:
            return 0

        y = (height+self.spacing)*len(self.items)
        return max(0, y - 1*self.scroll['widget'].height)

    def button_clicked(self, instance):
        for n, i in enumerate(self.items):
            if instance is not i.widget:
                continue
            self.selected = n
            try:
                self.button_func(instance, n)
            except TypeError:
                pass
            if not self.button_select:
                return -1
            return n

    def set_scroll(self, idx):
        space = self.get_scroll_space()
        if not space:
            return
        row_height = self.items[0].widget.height+self.spacing
        scroll_height = self.scroll['widget']

        s = idx*row_height
        s = s-scroll_height.height
        s = s/space

        scroll_y = 1-s
        # shift by height of row so we see it as the bottom option
        scroll_y = scroll_y - row_height/space

        scroll_y = max(0, min(1, scroll_y))

        self.scroll['widget'].scroll_y = scroll_y

    def move_cursor(self, delta):
        if self.cursor_wrap:
            selected = (self.selected + delta ) % len(self.items)
        else:
            selected = max(0, min(self.selected + delta, len(self.items)-1))
        self.set_cursor(selected)

    def set_cursor(self, pos):
        self.deselect()
        self.selected = pos
        self.highlight_line(self.selected)

    def button_hide(self, *args):
        self.hide(True)

    def process_key_press(self, window_instance, key, scancode, codepoint, modifiers):
        delta = 1
        if 'shift' in modifiers:
            delta *= -1
        # down is 274
        # up is 273
        if key == 273:
            # Up pressed
            # Numbers ascend as they go down the page
            self.move_cursor(delta*-1)
        if key == 274:
            # Down pressed
            self.move_cursor(delta)
        if key == 9:
            # Tab pressed
            self.move_cursor(delta)


class WidgetManager:
    def __init__(self, wid_id, wid):
        self.id = wid_id
        self.widget = wid
        self.parent = None
        self.layout = None
        self.data = None
        self.hidden = False
        self.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
        self.subitems = {}
        self.shapes = {}

    def draw_rectangle(self):
        with self.widget.canvas:
            Color(1, 1, 0, 1, mode="rgba")
            shape_id = self.shapes
            self.shapes[len(shape_id)] = Rectangle(pos=(200, 300), size=(100, 50))
            return shape_id

    def draw_background(self, bc="fff9ff"):

        rgba = get_color_from_hex(bc)

        with self.widget.canvas.before:
            rect_properties = {'color': Color(rgba[0], rgba[1], rgba[2], rgba[3], mode='rgba'),
                               'rectangle': Rectangle(size=self.widget.size, pos=self.widget.pos)}
            self.shapes['background'] = rect_properties

        def update_rect(instance, value):
            rect_properties['rectangle'].pos = instance.pos
            rect_properties['rectangle'].size = instance.size
            # rect_properties['rectangle'].color = None

        # listen to size and position changes
        self.widget.bind(pos=update_rect, size=update_rect)

    def hide(self, dohide=True):
        wid = self.widget
        if hasattr(self, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled = self.saved_attrs
        if dohide:
            if not self.hidden:
                self.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True

        self.hidden = dohide


class Client:
    def __init__(self, bc='CFFBE7', window_size=None, name='NuBuild'):
        self.App = CoreApp()
        self.App.init(name=name)
        self.screens = {'main': {'layout': self.App.layout, 'screen': self.App.main_page}}
        self.current_screen = self.screens['main']
        self.widgets = {}
        self.mouse_move_func = None
        self.running = False
        self.default_text_color = [1, 1, 1, 1]

        if bc:
            Window.clearcolor = get_color_from_hex(bc)
        if window_size:
            Window.size = window_size

    def insert_widget(self, wid, wid_id=None, z_index=0):
        if not wid_id:
            wid_id = len(self.App.widgets)
        self.App.widgets[wid_id] = wid
        render_widget(self.current_screen['layout'], wid, z_index=z_index)
        return {'id': wid_id, 'widget': wid}

    def new_screen(self, title=None):
        if not title:
            for title in range(len(self.screens) + 1):
                if str(title) not in self.screens.keys():
                    break

        screen = Screen(name=str(title))
        float_layout = FloatLayout()
        screen.add_widget(float_layout)
        self.App.screen_manager.add_widget(screen)
        self.screens[str(title)] = {'layout': float_layout, 'screen': screen}
        return str(title)

    def transition(self, title, view=True):
        self.current_screen = self.screens[title]
        self.App.current = self.current_screen['screen'].name
        if view:
            self.App.screen_manager.current = title

    def incorporate_widget(self, wid, layout, hsize, hpos, center, include=True, z_index=0, height=30):
        if not include:
            return wid
        if layout is None:
            ret = self.add_widget(wid, hsize, hpos, center=center, z_index=z_index)
            wid_m = WidgetManager(ret['id'], wid)
            ret['manager'] = wid_m

            return ret
        else:
            wid.pos_hint = {'x': 0, 'y': 0}
            self.append_scroll(layout, wid, height)  # wid.text_size[1])
            wid_id = len(layout.subitems)
            wid_m = WidgetManager(wid_id, wid)
            layout.subitems[wid_id] = wid_m
            return {'id': wid_id, 'widget': wid, 'manager': wid_m}

    def add_button(self, text='But', bg_color='E7B8F9', hsize=(0.20, 0.15), hpos=(0.5, 0.5), center=False, height=10,
                   halign='center', valign='center', layout=None, font_size=17, include=True, z_index=0):
        wid = Button(text=text, size_hint_y=None, height=40, font_size=font_size)
        wid.background_normal = ''
        if type(bg_color) is str:
            new_color = get_color_from_hex(bg_color)
        else:
            new_color = bg_color
        wid.background_color = new_color

        if height:
            wid.height = height
        if hsize:
            wid.size_hint = hsize

        wid.text_size = [i[0] * i[1] for i in zip(wid.size_hint, Window.size)]
        wid.halign = halign
        wid.valign = valign

        return self.incorporate_widget(wid, layout, hsize, hpos, center, include=include, z_index=z_index, height=height)

    def add_image(self, source='', bg_color='E7B8F9', hsize=(0.20, 0.15), hpos=(0.5, 0.5), center=False, height=10,
                  layout=None, include=True):
        wid = Image(source=source, size_hint_y=None, height=40)
        wid.background_normal = ''
        if type(bg_color) is str:
            new_color = get_color_from_hex(bg_color)
        else:
            new_color = bg_color
        wid.background_color = new_color

        return self.incorporate_widget(wid, layout, hsize, hpos, center, include)

    def add_input(self, text='', bg_color='E5E5E5', hsize=(0.15, 0.05), hpos=(0.5, 0.5), center=False, multiline=False,
                  custom=False, layout=None, font_size=17, include=True, halign='left', valign='center', height=30):
        wid = TextInput(text=text, multiline=multiline, font_size=font_size)
        if custom:
            wid.background_normal = ''
        if type(bg_color) is str:
            new_color = get_color_from_hex(bg_color)
        else:
            new_color = bg_color
        wid.background_color = new_color
        wid.halign = halign
        wid.valign = valign

        return self.incorporate_widget(wid, layout, hsize, hpos, center, include=include, height=height)

    def add_label(self, text='test_text', halign='center', valign='center', bg_color='E5E5E5',
                  hsize=(0.2, 0.2), hpos=(0.5, 0.5), center=False, custom=False, layout=None, line_width=1,
                  font_size=17, auto_size=True, include=True, z_index=0):
        wid = Label(text=text, halign=halign, valign=valign, markup=True, outline_width=line_width, font_size=font_size)
        wid.size_hint = hsize
        # wid.text_size = [i[0]*i[1] for i in zip(wid.size_hint, Window.size)]
        wid.text_size = [wid.size_hint[0] * Window.size[0], None]

        def handle_texture(instance, texture_size):
            wid.height = texture_size[1]

        if auto_size:
            wid.bind(texture_size=handle_texture)

        if custom:
            wid.background_normal = ''
        if type(bg_color) is str:
            new_color = get_color_from_hex(bg_color)
        else:
            new_color = bg_color
        wid.background_color = new_color

        return self.incorporate_widget(wid, layout, hsize, hpos, center, include, z_index=z_index)

    def add_scroll(self, hsize=(0.15, 0.05), hpos=(0.5, 0.5), layout_width=1, spacing=4, cols=1):
        layout = GridLayout(cols=cols, spacing=spacing, size_hint_y=None, size_hint_x=layout_width)
        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        root.effect_cls = ScrollEffect
        root.add_widget(layout)

        ret = self.add_widget(root, hsize, hpos, center=False)
        wid_m = WidgetManager(ret['id'], root)
        wid_m.layout = layout
        ret['manager'] = wid_m

        return ret

    def add_labelled_input(self, lbl_txt='Question', btn_txt='Go', hpos=(0.1, 0.1), hsize=(0.5, 0.15),
                           include_btn=True):

        btn_width = Window.size[1] / Window.size[0]

        inp_hpos = hpos
        if include_btn:
            height = hsize[1] - 0.05
            inp_hsize = (hsize[0] - height * btn_width, height)
        else:
            inp_hsize = (hsize[0], hsize[1] - 0.05)

        lbl_hpos = (hpos[0], hpos[1] + inp_hsize[1] * 1.1)
        lbl_hsize = (hsize[0] * 0.9, hsize[1] - 0.05)

        inp_dict = self.add_input(hpos=inp_hpos, hsize=inp_hsize)
        lbl_dict = self.add_label(text=lbl_txt, hpos=lbl_hpos, hsize=lbl_hsize)

        lbl_dict['widget'].valign = 'bottom'
        lbl_dict['widget'].halign = 'left'

        if include_btn:
            btn_hpos = (hpos[0] + inp_hsize[0], hpos[1])
            btn_hsize = (inp_hsize[1] * btn_width, inp_hsize[1])
            btn_dict = self.add_button(text=btn_txt, hpos=btn_hpos, hsize=btn_hsize, bg_color="565656")

            return inp_dict, lbl_dict, btn_dict

        return inp_dict, lbl_dict

    def add_dropdown(self, pos=(0.0333, 0.756), size=(0.2667, 0.3), draw=True, hide=False, highlight=False, cursor_wrap=False, spacing=1):
        return Dropdown(client=self, pos=pos, size=size, draw=draw, hide=hide, highlight=highlight, cursor_wrap=cursor_wrap, spacing=spacing)

    def add_widget(self, wid, hsize=(0.15, 0.15), hpos=(0.5, 0.5), center=False, z_index=0):
        # print(wid, hsize, hpos)
        if hsize:
            wid.size_hint = hsize
        if hpos:
            if center:
                wid.pos_hint = {'center_x': hpos[0], 'center_y': hpos[1]}
            else:
                wid.pos_hint = {'x': hpos[0], 'y': hpos[1]}

        return self.insert_widget(wid, z_index=z_index)

    def append_scroll(self, layout, wid, height=25):
        wid.size_hint_y = None
        wid.height = height
        layout.layout.add_widget(wid)
        wid.pos_hint['x'] = 1
        # print(wid.pos, wid.pos_hint)
        return {'id': layout.id, 'widget': wid}

    def remove_widget(self, wid):
        unrender_widget(self.App, wid)

    def start(self):
        # mouse = Mouse()
        # Window.bind(on_motion=mouse.on_motion)
        self.running = True
        self.App.run()


if __name__ == "__main__":
    c = Client(bc='D8D8D8', window_size=(1400, 800))

    b = c.add_label()
    btn = b['manager']
    btn.draw_background('ff330f')
    b['widget'].size_hint = (0.1, 0.1)
    print(dir(b['widget']))

    d = c.add_dropdown()
    d.clear()
    d.init_items()

    c.start()
