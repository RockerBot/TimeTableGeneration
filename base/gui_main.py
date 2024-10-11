import threading
import time
import copy

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from gui_screen1 import InputScreen
from gui_screen2 import TableScreen
from gui_screen3 import TeacherScreen
from gui_screen4 import AvailabilityScreen
from gui_screen5 import WFCScreen

import cli_main as cli_main_test

n_semesters, n_days, n_slots, n_electives = 1, 1, 1, 1
n_sections = (1,)
subject_list = []
teacher_list = []
elective_slots = []
blocked_slots = []
subject_dict = {}
teacher_dict = {}
elective_nms = []
semester_subjects_list = []
semester_electives_list = []
faculty_availability_dict = {}

def run_algo(self):
    if len(elective_nms):
        for i in range(n_electives):
            if f'elective{i+1}' in elective_nms[i][0]:
                continue
            elective_nms[i][0].append(f'elective{i+1}')
    else:
        for i in range(n_electives):
            elective_nms.append(([f'elective{i+1}'], [6, 3]))
    print(
        (n_sections, n_days, n_slots),
        (len(subject_list), len(teacher_list)),
        n_electives,
        subject_dict,
        [elective_nms[i] for i in range(n_electives)]
    )
    print(elective_slots)
    print(teacher_dict)
    print(semester_electives_list)
    print(semester_subjects_list)
    print(blocked_slots)
    print(faculty_availability_dict)


    thrd = threading.Thread(target=cli_main_test.main, args=(
        n_days, n_slots, len(n_sections), n_sections,
        len(subject_list), len(teacher_list),
        n_electives,
        {k: subject_dict[k] for k in subject_dict.keys()},
        [elective_nms[i] for i in range(n_electives)],
        copy.deepcopy(elective_slots),
        {k: teacher_dict[k] for k in teacher_dict.keys()},
        copy.deepcopy(semester_subjects_list),
        copy.deepcopy(semester_electives_list),
        copy.deepcopy(blocked_slots),
        {k: faculty_availability_dict[k] for k in faculty_availability_dict.keys()},
        self.set_states,
        copy.deepcopy(self.modified_states)
    ))
    thrd.start()
    pass


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        input_screen = InputScreen(cli_main_test.input_file, name='input')
        table_screen = TableScreen(name='table')
        teacher_screen = TeacherScreen(name='teacher')
        availability_screen = AvailabilityScreen(name='availability')
        wfc_screen = WFCScreen(name='wfc')

        def pass_data_input(sec, day, slot, elec, subjects, subject_d, teachers):
            global n_semesters, n_sections, n_days, n_slots, n_electives, subject_list, subject_dict, teacher_list
            n_sections, n_days, n_slots, n_electives = sec, day, slot, elec
            n_semesters = len(sec)
            subject_list = subjects
            subject_dict = subject_d
            teacher_list = teachers
            table_screen.set_data(n_sections, n_days, n_slots, n_electives, subject_list, teacher_list)

        def pass_data_table(electives, blocked, sem_elecs):
            global elective_slots, blocked_slots, semester_electives_list
            elective_slots = electives
            blocked_slots = blocked
            semester_electives_list = sem_elecs
            teacher_screen.set_data(subject_list, teacher_list, n_electives, n_sections)

        def pass_data_teacher(teachers, sem_subjs):
            global teacher_dict, semester_subjects_list
            teacher_dict = teachers
            semester_subjects_list = sem_subjs
            availability_screen.set_data(n_days, n_slots, teacher_list)

        def pass_data_availability(avail_d):
            global faculty_availability_dict
            faculty_availability_dict = avail_d
            wfc_screen.set_data(
                n_sections, n_days, n_slots, n_electives,
                subject_list, teacher_dict,
                run_algo)

        def pass_all_data(day, slot, sems, sec, n_subject, n_faculty, elec,
                          subject_d, electives, slots_elective, teacher_d,
                          sem_subjs, sem_elecs,
                          slots_blocked, teach_avail_d):
            global n_sections, n_days, n_slots, n_electives, \
                subject_list, subject_dict, \
                teacher_list, teacher_dict, \
                elective_slots, blocked_slots, elective_nms,\
                semester_subjects_list, semester_electives_list,\
                faculty_availability_dict

            elective_nms = electives

            pass_data_input(sec, day, slot, elec, [*subject_d.keys()], subject_d, [*teacher_dict.keys()])
            pass_data_table(slots_elective, slots_blocked, sem_elecs)
            pass_data_teacher(teacher_d, sem_subjs)
            pass_data_availability(teach_avail_d)

        # pass data
        input_screen.pass_data = pass_data_input
        table_screen.pass_data = pass_data_table
        teacher_screen.pass_data = pass_data_teacher
        availability_screen.pass_data = pass_data_availability

        input_screen.pass_all_data = pass_all_data

        # adding screens to screen manager
        sm.add_widget(input_screen)
        sm.add_widget(table_screen)
        sm.add_widget(teacher_screen)
        sm.add_widget(availability_screen)
        sm.add_widget(wfc_screen)

        return sm


if __name__ == '__main__':
    MyApp().run()
    print("Program Finished Execution")
