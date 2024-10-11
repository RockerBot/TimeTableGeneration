from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

from gui_helpfull import add_widgets, add_colour


class CustomScrollView(ScrollView):
    def on_scroll_start(self, touch, check_children=True):
        if self.collide_point(*touch.pos):
            if self.do_scroll_x and touch.button == 'scrolldown':
                self.scroll_x += 0.1
                self.scroll_x = max(min(1, self.scroll_x), 0)
            elif self.do_scroll_x and touch.button == 'scrollup':
                self.scroll_x -= 0.1
                self.scroll_x = max(min(1, self.scroll_x), 0)
        return super().on_scroll_start(touch, check_children)


class ListEntry(BoxLayout):
    def __init__(self, text, scrn_obj, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.scrn_obj = scrn_obj
        self.label = Label(text=text, size_hint=(0.8, 1))
        self.button_apply = Button(text='Apply', size_hint_x=None, width=dp(50)
        )
        self.button_apply.bind(on_release=self.apply_avail)

        add_widgets(
            self.label,
            self.button_apply,
            to=self
        )
        # add_colour(self, (1, 0, 0, 1))

    def get_text(self):
        return self.label.text

    def apply_avail(self, instance):
        avail = [[0] *self.scrn_obj.n_slots for _ in range(self.scrn_obj.n_days)]
        for i, child in enumerate(self.scrn_obj.grid.children):
            day_ndx = self.scrn_obj.n_days - (i // self.scrn_obj.n_slots) - 1
            slot_ndx = self.scrn_obj.n_slots - (i % self.scrn_obj.n_slots) - 1
            if child.state == 'down':
                avail[day_ndx][slot_ndx] = 1
        self.scrn_obj.faculty_availability_dict[self.label.text] = avail
        print(avail)


class AvailabilityScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.pass_data = None
        self.teachers = 0
        self.n_days = 1
        self.n_slots = 1
        self.faculty_availability_dict = {}
        self.grid = None
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.layout_nav = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(40))
        self.layout_main = BoxLayout(orientation='horizontal', size_hint=(1, 1))
        self.layout_teachers = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)

        self.scroll_view_teachers = CustomScrollView(size_hint=(0.2, 1))
        # add_colour(self.scroll_view_teachers, (1, 1, 0, 1))

        self.button_back = Button(text='Back', size_hint=(None, 1), width=dp(70))
        self.button_continue = Button(text='Continue', size_hint=(None, 1), width=dp(70), pos_hint={'right':1})

        self.layout_teachers.bind(minimum_height=self.layout_teachers.setter('height'))
        self.button_back.bind(on_press=self.goto_prev_screen)
        self.button_continue.bind(on_press=self.goto_next_screen)

        add_widgets(
            self.button_back,
            Widget(size_hint=(1, 1)),
            self.button_continue,
            to=self.layout_nav
        )
        self.scroll_view_teachers.add_widget(self.layout_teachers)
        add_widgets(
            self.layout_nav,
            self.layout_main,
            to=self.layout
        )
        self.add_widget(self.layout)

    def set_data(self, n_days, n_slots, teacher_list):
        self.teachers = teacher_list
        self.n_days = n_days
        self.n_slots = n_slots
        self.faculty_availability_dict = {}

        self.layout_teachers.clear_widgets()
        for teacher in teacher_list:
            self.faculty_availability_dict[teacher] = [[0] * self.n_slots for _ in range(self.n_days)]
            list_entry = ListEntry(teacher, self, spacing=10, size_hint_y=None, height=dp(30))
            self.layout_teachers.add_widget(list_entry)

        self.layout_main.clear_widgets()
        self.grid = GridLayout(cols=self.n_slots)
        for row in range(self.n_slots):
            for col in range(self.n_days):
                btn = ToggleButton(text=f'day {col + 1}\nslot {row + 1}',
                                   text_size=(None, None), size_hint=(1, 1),
                                   halign='center', valign='middle')
                btn.bind(size=lambda b, value: setattr(b, 'text_size', (b.width, None)))
                self.grid.add_widget(btn)

        add_widgets(
            self.scroll_view_teachers,
            self.grid,
            to=self.layout_main
        )

    def goto_prev_screen(self, instance):
        self.manager.current = 'teacher'

    def goto_next_screen(self, instance):
        print('faculty_availability_dict', self.faculty_availability_dict)
        self.pass_data(self.faculty_availability_dict)
        self.manager.current = 'wfc'