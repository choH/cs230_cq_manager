from kivy.config import Config
Config.set('graphics', 'width', '563')
Config.set('graphics', 'height', '1218')


from kivy.app import App
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.clock import mainthread
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.progressbar import ProgressBar
from kivy.core.text import Label as CoreLabel
from kivy.lang.builder import Builder
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock
from kivy.lang import Builder

import json, requests, datetime, time
import pandas






import excel_parser as ep

input_file_path = '/Users/zhonghenry/Desktop/cq_manager/cq_input.xlsx'

df = ep.to_parse_excel(input_file_path)
quest_list = ep.df_to_list(df)
quest_list = ep.clean_quest_list(quest_list)
with open("quest.data", "w") as quest_file:
    json.dump(quest_list, quest_file, indent = 4)
    quest_file.close()

empty_list = []
with open("user.data", "w") as user_file:
    json.dump(empty_list, user_file, indent = 4)
    user_file.close()


















class ShareData:
    def __init__(self):
        self.current_user_quest_id = 0
        self.searching_user_quest_id = 0
        self.now = datetime.datetime.now()


filter_status = {'drive_status': 0, 'knowledge_status':0, 'action_status': 0, 'strategy_status': 0}



def get_next_entry():
    with open('/Users/zhonghenry/Desktop/cq_manager/quest.data') as json_file:
        json_data = json.load(json_file)
        for entry in json_data:
            yield entry




def get_matched_entry(drive_status, knowledge_status, action_status, strategy_status):
# def get_matched_entry():
    for entry in get_next_entry():
        entry_holder = entry
        if drive_status != 0:
            if entry['quest_drive'] == 0:
                print("entered_drive")
                continue
        if knowledge_status != 0:
            if entry['quest_knowledge'] == 0:
                continue
        if action_status != 0:
            if entry['quest_action'] == 0:
                continue
        if strategy_status != 0:
            if entry['quest_strategy'] == 0:
                continue
        yield entry_holder

def entry_to_str(entry):
    entry_description_str = entry['quest_description']
    entry_description_str = entry_description_str[0:70] + '...'
    entry_str = str (entry['quest_id'] + '\n' +
                str(entry_description_str) +
                '\n' + 'Drive: ' + str(int(round(entry['quest_drive'])))
                + '     Knowledge: ' + str(int(round(entry['quest_knowledge'])))
                + '     Action: ' + str(int(round(entry['quest_action'])))
                + '     Strategy: ' + str(int(round(entry['quest_strategy']))))
    return entry_str

def entry_to_display(mode = 0):
    # print("before call {}".format((c_drive_status, c_knowledge_status, c_action_status, c_strategy_status)))
    if mode == 0:
        for entry in get_matched_entry(filter_status['drive_status'], filter_status['knowledge_status'], filter_status['action_status'], filter_status['strategy_status']):
            entry_str = entry_to_str(entry)
            yield entry_str
    else:
        with open("user.data", "r") as user_file:
            user_data = json.load(user_file)
        for entry in user_data:
            entry_str = entry_to_str(entry)
            entry_str = entry_str + '   #   ' + str(entry['user_quest_id'])
            yield entry_str



def add_new_user_quest(self, entry):
    user_entry = entry
    shared_data = App.get_running_app().shared_data
    user_quest_id = shared_data.current_user_quest_id + 1
    # user_quest_id = shared_data.current_user_quest_id
    shared_data.current_user_quest_id += 1
    user_entry['user_quest_id'] = user_quest_id

    user_repeat_time = get_user_repeat_time(user_entry['quest_id'])
    user_entry['user_repeat_time'] = user_repeat_time
    user_entry['user_reflection'] = 'N/A'
    user_entry['user_is_complete'] = False
    user_entry['user_complete_date'] = False

    with open('/Users/zhonghenry/Desktop/cq_manager/user.data') as user_file:
        user_data = json.load(user_file)
        user_file.close()
    user_data.append(user_entry)
    with open('/Users/zhonghenry/Desktop/cq_manager/user.data', "w") as user_file:
        json.dump(user_data, user_file, indent = 4)
        user_file.close()
    return user_entry['user_quest_id']

def get_user_repeat_time(quest_id):
    repeat_counter = 1
    with open('/Users/zhonghenry/Desktop/cq_manager/user.data') as user_file:
        user_data = json.load(user_file)
        user_file.close()
    for an_entry in user_data:
        if len(user_data) == 0:
            print('The user file is empty')
            break
        elif an_entry['quest_id'] == quest_id:
            repeat_counter += 1
    return repeat_counter






















class QuestScreen(Screen):

    def __int__(self, **kwargs):
        super(QuestScreen, self).__init__(**kwargs)
        now = datetime.datetime.now()
        self.current_time = int(str(self.now.year) + str(self.now.month) + str(self.now.day) + str(self.now.hour) + str(self.now.minute) + str(self.now.second) + str(self.now.microsecond))
        self.c_drive_status = 1
        self.c_knowledge_status = 1
        self.c_action_status = 1
        self.c_strategy_status = 1

    def to_details(self, instance):
        quest_id = int(instance.text[0:3])
        print('The instance has a quest id of #{}'.format(quest_id))
        for entry in get_next_entry():
            if int(entry['quest_id']) == quest_id:
                user_quest_id = add_new_user_quest(self, entry)
                # ShareData.current_user_quest_id = user_quest_id
                # print('Proceed to the details for user_quest #{}'.format(ShareData.current_user_quest_id))
                print('Proceed to the details for user_quest #{}'.format(user_quest_id))
                break

    def set_drive(self):
        if self.ids.filter_drive.state == 'down':
            filter_status['drive_status'] = 1
            print("Down: {}".format(filter_status))
        else:
            filter_status['drive_status'] = 0
            print("Down: {}".format(filter_status))
        self.on_enter()

    def set_knowledge(self):
        if self.ids.filter_knowledge.state == 'down':
            filter_status['knowledge_status'] = 1
        else:
            filter_status['knowledge_status'] = 0
        self.on_enter()

    def set_action(self):
        if self.ids.filter_action.state == 'down':
            filter_status['action_status'] = 1
        else:
            filter_status['action_status'] = 0
        self.on_enter()

    def set_strategy(self):
        if self.ids.filter_strategy.state == 'down':
            filter_status['strategy_status'] = 1
        else:
            filter_status['strategy_status'] = 0
        self.on_enter()

    def set_registered(self):
        if self.ids.filter_registered.state == 'down':
            self.on_enter(1)
        else:
            self.on_enter()

    def show_in_details(self, instance):
        shared_data = App.get_running_app().shared_data
        this_user_quest_id = int(instance.text[-3:])
        with open("user.data", "r") as user_file:
            user_data = json.load(user_file)
        for entry in user_data:
            if entry['user_quest_id'] == this_user_quest_id:
                entry['user_quest_id'] = shared_data.current_user_quest_id + 1
                break
        with open("user.data", "w") as user_file:
            json.dump(user_data, user_file, indent = 4)
            user_file.close()

        shared_data.current_user_quest_id += 1



    @mainthread
    def on_enter(self, mode = 0):
        self.ids.entry_layout.clear_widgets()
        if mode == 0:
            for entry_str in entry_to_display(mode):
            # for entry_str in entry_to_display():
                a_button = Button(text = entry_str, halign='center')
                a_button.bind(on_release = self.to_details)
                self.ids.entry_layout.add_widget(a_button)
        else:
            for entry_str in entry_to_display(mode):
            # for entry_str in entry_to_display():
                a_button = Button(text = entry_str, halign='center')
                a_button.bind(on_release = self.show_in_details)
                self.ids.entry_layout.add_widget(a_button)





    def on_leave(self):
        filter_status['drive_status'] = 0
        filter_status['knowledge_status'] = 0
        filter_status['action_status'] = 0
        filter_status['strategy_status'] = 0
























class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)


    def file_import(self):

        pass

    def file_export(self):
        pandas.read_json("user.data").to_excel("output.xlsx")
        pass



















    def switch(self, quest_type):
        # shared_data = App.get_running_app().shared_data
        # shared_data._screen_pass_string = quest_type
        if quest_type == 'Drive':
            filter_status['drive_status'] = 1

        if quest_type == 'Knowledge':
            filter_status['knowledge_status'] = 1

        if quest_type == 'Action':
            filter_status['action_status'] = 1

        if quest_type == 'Strategy':
            filter_status['strategy_status'] = 1

        print('current filter_status: {}'.format(filter_status))


    def information_func(self):

        drive_p_total = 0
        drive_p = 0

        knowledge_p_total = 0
        knowledge_p = 0

        strategy_p_total = 0
        strategy_p = 0

        action_p_total = 0
        action_p = 0


        with open("quest.data", "r") as quest_file:
            quest_data = json.load(quest_file)

            for quest in quest_data:
                drive_p_total += int(quest["quest_drive"])
                knowledge_p_total += int(quest["quest_knowledge"])
                strategy_p_total += int(quest["quest_strategy"])
                action_p_total += int(quest["quest_action"])

        with open("user.data", "r") as user_file:
            user_data = json.load(user_file)

            for quest in user_data:
                if quest["user_is_complete"]:
                    drive_p += int(quest["quest_drive"])
                    knowledge_p += int(quest["quest_knowledge"])
                    strategy_p += int(quest["quest_strategy"])
                    action_p += int(quest["quest_action"])


        self.ids.prog_drive.max = 150
        self.ids.prog_drive.value = drive_p

        self.ids.drive.text = 'Drive\n' + str(drive_p) + '/' + str(150)

        self.ids.prog_knowledge.max = 150
        self.ids.prog_knowledge.value = knowledge_p

        self.ids.knowledge.text = 'Knowledge\n' + str(knowledge_p) + '/' + str(
            150)

        self.ids.prog_strategy.max = 150
        self.ids.prog_strategy.value = strategy_p

        self.ids.strategy.text = 'Strategy\n' + str(strategy_p) + '/' + str(
            150)

        self.ids.prog_action.max = action_p_total
        self.ids.prog_action.value = action_p

        self.ids.action.text = 'Action\n' + str(action_p) + '/' + str(
            150)

        percent = float(drive_p + action_p + strategy_p + knowledge_p)
        percent = int((percent / 600.0) * 100.0)
        self.ids.progress_tr.text = '{}%\nLevel\nProgress'.format(percent)
        quest_file.close()
        user_file.close()



















class DetailsScreen(Screen):

    def __init__(self, **kwargs):
        super(DetailsScreen, self).__init__(**kwargs)


    def on_enter(self):
        shared_data = App.get_running_app().shared_data

        with open("user.data", "r") as user_file:
            user_data = json.load(user_file)
        if len(user_data) > 0:
            target_entry = user_data[-1]

        for entry in user_data:
            if entry['user_quest_id'] == shared_data.current_user_quest_id:
                target_entry = entry


                self.ids.label_quest_id.text = 'Quest ID: ' + str(target_entry['quest_id'])
                self.ids.label_unique_id.text = str(target_entry['user_quest_id'])


                self.ids.label_drive.text = 'Drive: ' + str(target_entry['quest_drive'])
                self.ids.label_knowledge.text = 'Knowledge: ' + str(target_entry['quest_knowledge'])
                self.ids.label_action.text = 'Action: ' + str(target_entry['quest_action'])
                self.ids.label_strategy.text = 'Strategy: ' + str(target_entry['quest_strategy'])

                self.ids.label_repeatable.text = 'Repeatable: ' + str(target_entry['quest_is_repeatable'])
                self.ids.label_max_repeat.text = 'Max Repeat: ' + str('Infinity' if not target_entry['quest_max_repeat'] else target_entry['quest_max_repeat'])
                self.ids.label_repeat_time.text = 'Repeat Time: ' + str(target_entry['user_repeat_time'])
                self.ids.label_completion.text = 'Completion: ' + ('Yes' if target_entry['user_is_complete'] else 'No')

                self.ids.label_description.text = 'Quest Description: ' + '\n\n' + str(target_entry['quest_description'])
                self.ids.label_hint.text = 'Quest Hint: ' + '\n\n' + str(target_entry['quest_hint'])
                self.ids.label_reflection.text = 'Reflection ' + '\n\n' + str(target_entry['user_reflection'])
                break

    def submit_reflection(self):
        shared_data = App.get_running_app().shared_data
        with open("user.data", "r") as user_file:
            user_data = json.load(user_file)
        print('id is: {}'.format(int(self.ids.label_unique_id.text)))
        for entry in user_data:
            if entry['user_quest_id'] == int(self.ids.label_unique_id.text):
                # print('before: {}'.format(entry))
                entry['user_reflection'] = self.reflection_input.text
                entry['user_is_complete'] = True
                entry['user_complete_date'] = str(shared_data.now)
                # print('after: {}'.format(entry))
                break
        with open("user.data", "w") as user_file:
            json.dump(user_data, user_file, indent = 4)
            user_file.close()

        self.on_enter()

    def delete_quest(self):
        shared_data = App.get_running_app().shared_data
        with open("user.data", "r") as user_file:
            user_data = json.load(user_file)
        # print('id is: '.format(int(self.ids.label_unique_id.text[-2:])))
        for entry in user_data:
            if entry['user_quest_id'] == int(self.ids.label_unique_id.text[-2:]):
                user_data.remove(entry)
                break
        with open("user.data", "w") as user_file:
            json.dump(user_data, user_file, indent = 4)
            user_file.close()

        self.on_enter()

    def on_leave(self):
        self.reflection_input.text = ''


class PopUpBoard():
    def __init__(self, error_message_input = ''):
        self.error_message = str(error_message_input)

    def show_popup(self):
        """
        This function pop a pop-up window with error_message displayed.
        """
        content = BoxLayout(orientation='vertical')
        message_label = Label(text=self.error_message)
        dismiss_button = Button(text='OK')
        content.add_widget(message_label)
        content.add_widget(dismiss_button)
        popup = Popup(title='Error', content=content, size_hint=(0.3, 0.25))
        dismiss_button.bind(on_press=popup.dismiss)
        popup.open()



class quest_boardApp(App):
    shared_data = ShareData()

if __name__ == '__main__':
    quest_boardApp().run()