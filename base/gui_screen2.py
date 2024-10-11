from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton

from gui_helpfull import add_widgets, add_colour, hue_to_rgb

default_tg_btn_args = {
    'group': 'slot_type',
    'size_hint_x': None,
    'width': dp(80)
}
is_dragging = False


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


class DragButton(Button):
    def __init__(self, set_clr, val, **kwargs):
        super().__init__(**kwargs)
        self.set_colour = set_clr
        self.value = val

    def on_touch_down(self, touch):
        global is_dragging
        if self.collide_point(*touch.pos):
            self.set_colour(self)  # Change button color to red
            is_dragging = True
            return True  # Consume the touch event
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if is_dragging and self.collide_point(*touch.pos):
            self.set_colour(self)  # Change button color to red
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        global is_dragging
        if is_dragging:
            is_dragging = False
            return True  # Consume the touch event
        return super().on_touch_up(touch)


class TableScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.n_sections = None
        self.n_days = None
        self.n_slots = None
        self.n_electives = None
        self.subject_list = None
        self.teacher_list = None
        self.hues = []
        self.sem_grids = []
        self.selected_index = 0

        self.pass_data = None

        self.layout_table = None
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.layout_options = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)
        self.layout_tg_buttons = BoxLayout(orientation='horizontal', size_hint_x=None, spacing=10)

        self.scroll_view_tg_buttons = CustomScrollView(do_scroll_x=True, do_scroll_y=False, size_hint=(1, 1))
        self.scroll_view_table = ScrollView(size_hint=(1, 1))

        self.button_back = Button(text='Back', size_hint=(None, 1), width=dp(70))
        self.button_continue = Button(text='Continue', size_hint=(None, 1), width=dp(70))

        self.button_toggle_free = ToggleButton(text='Free', **default_tg_btn_args)
        self.button_toggle_invalid = ToggleButton(text='Invalid', state='down', **default_tg_btn_args)

        self.layout_tg_buttons.bind(minimum_width=self.layout_tg_buttons.setter('width'))
        self.button_back.bind(on_press=self.goto_prev_screen)
        self.button_continue.bind(on_press=self.goto_next_screen)
        self.button_toggle_free.bind(on_press=self.on_tgl_press)
        self.button_toggle_invalid.bind(on_press=self.on_tgl_press)

        self.scroll_view_tg_buttons.add_widget(self.layout_tg_buttons)
        add_widgets(
            self.button_back,
            self.scroll_view_tg_buttons,
            self.button_continue,
            to=self.layout_options
        )

        add_widgets(
            self.layout_options,
            self.scroll_view_table,
            to=self.layout
        )
        # add_colour(self.scroll_view_tg_buttons, (1, 1, 0, 1))
        self.add_widget(self.layout)

    def set_data(self, n_sec, n_day, n_slot, n_elective, subjects, teachers):
        self.n_sections = n_sec
        self.n_days = n_day
        self.n_slots = n_slot
        self.n_electives = n_elective
        self.subject_list = subjects
        self.teacher_list = teachers

        # toggle buttons
        self.layout_tg_buttons.clear_widgets()
        add_widgets(
            self.button_toggle_free,
            self.button_toggle_invalid,
            to=self.layout_tg_buttons
        )
        self.button_toggle_free.index = -1
        self.button_toggle_invalid.index = 0
        self.hues = [[1, 0, 0, 1]]
        for i in range(1, self.n_electives + 1):
            btn_tgl_elec = ToggleButton(text=f'elective {i}', **default_tg_btn_args)
            btn_tgl_elec.bind(on_press=self.on_tgl_press)
            btn_tgl_elec.index = i
            self.layout_tg_buttons.add_widget(btn_tgl_elec)
            self.hues.append(hue_to_rgb((i / (self.n_electives + 1)) * 360))
        self.hues.append([1, 1, 1, 1])

        self.layout_table = BoxLayout(orientation='vertical', size_hint_y=None)
        self.layout_table.bind(minimum_height=self.layout_table.setter('height'))
        self.sem_grids = []
        for i in range(len(self.n_sections)):
            grid = GridLayout(cols=self.n_slots, size_hint=(1, None), height=dp(95*self.n_days + 20))
            for col in range(self.n_days):
                for row in range(self.n_slots):
                    btn = DragButton(
                        self.set_colour, -1, text=f'R{row + 1}C{col + 1}',
                        size_hint_y=None, height=dp(95), padding=5,
                        halign='center', valign='middle'
                    )
                    grid.add_widget(btn)
                    # self.layout_table.add_widget(btn)
            self.sem_grids.append(grid)
            lbl = Label(text=f'semester {i + 1}', font_size='20sp', size_hint_y=None, height=dp(30))
            self.layout_table.add_widget(lbl)
            self.layout_table.add_widget(grid)
        self.scroll_view_table.clear_widgets()
        self.scroll_view_table.add_widget(self.layout_table)

    def on_tgl_press(self, instance):
        if instance.state == 'down':
            self.selected_index = instance.index

    def set_colour(self, btn):
        btn.background_color = self.hues[self.selected_index]
        btn.value = self.selected_index
        if self.selected_index == 0:
            btn.text = f'BLOCKED'
        elif self.selected_index == -1:
            btn.text = f'free (empty)'
        else:
            btn.text = f'elective {btn.value}'


    def goto_prev_screen(self, instance):
        self.manager.current = 'input'

    def goto_next_screen(self, instance):
        # TODO check if valid
        electives = [
            [[0] * self.n_slots for _ in range(self.n_days)]
            for _ in range(self.n_electives)
        ]
        blocked = []
        semester_electives_list = []

        for sem_i in range(len(self.n_sections)):
            blocked_i = [[0] * self.n_slots for _ in range(self.n_days)]
            sem_elec_list = set()
            for i, child in enumerate(self.sem_grids[sem_i].children):
                day_ndx = self.n_days - (i // self.n_slots) - 1
                slot_ndx = self.n_slots - (i % self.n_slots) - 1
                val = child.value
                if val == -1:
                    continue
                if val == 0:
                    blocked_i[day_ndx][slot_ndx] = 1
                else:
                    electives[val-1][day_ndx][slot_ndx] = 1
                    sem_elec_list.add(val-1)
            blocked.append(blocked_i)
            semester_electives_list.append(list(sem_elec_list))

        for i, el in enumerate(electives):
            print('elective', i+1, el)
        for i, bl in enumerate(blocked):
            print('sem', i+1, bl)
        print('semester_electives_list', semester_electives_list)
        self.pass_data(electives, blocked, semester_electives_list)
        self.manager.current = 'teacher'


