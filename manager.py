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
import os
import excel_parser as ep

# Default CQ spreadsheet.
input_file_path = 'cq_input.xlsx'

# Parsing the spreadsheet into JSON and write it into the quest.data file.
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

















#Share Data among the application.
class ShareData:
    def __init__(self):
        self.current_user_quest_id = 0
        self.searching_user_quest_id = 0
        self.now = datetime.datetime.now()
        self.new_spreadsheet_path = ''

#Filter status indicator.
filter_status = {'drive_status': 0, 'knowledge_status':0, 'action_status': 0, 'strategy_status': 0}






















# Generator to next quest entry from quest.data file.
def get_next_entry():
    with open('quest.data') as json_file:
        json_data = json.load(json_file)
        for entry in json_data:
            yield entry



# Generator to filter entries against filers.
def get_matched_entry(drive_status, knowledge_status, action_status, strategy_status):
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

# Converting JSON entry to a displable string for button on Quest Screen.
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

#Filter matched entries, generater the string, and yield to its caller.
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
            entry_str = entry_str + '     Completion: ' + ('Yes' if entry['user_is_complete'] else 'No') + '     #   ' + str(entry['user_quest_id'])
            yield entry_str


#Add user-specific key to a quest entry from quest.data and write such entry into user.data
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

    with open('user.data') as user_file:
        user_data = json.load(user_file)
        user_file.close()
    user_data.append(user_entry)
    with open('user.data', "w") as user_file:
        json.dump(user_data, user_file, indent = 4)
        user_file.close()
    return user_entry['user_quest_id']

#Get how many time a quest is already repeated.
def get_user_repeat_time(quest_id):
    repeat_counter = 1
    with open('user.data') as user_file:
        user_data = json.load(user_file)
        user_file.close()
    for an_entry in user_data:
        if len(user_data) == 0:
            print('The user file is empty')
            break
        elif an_entry['quest_id'] == quest_id:
            repeat_counter += 1
    return repeat_counter















# To add a new spreadsheet of quests into quest.data file.
class ImportScreen(Screen):

    def __int__(self, **kwargs):
        super(ImportScreen, self).__init__(**kwargs)

    # Parse the selected file into a JSON and add such JSON to the quest.data file, with continous quest_id given.
    def select_file(self, filename):
        new_file_path = filename[0]
        self.parent.transition.direction = 'left'
        self.parent.current = 'quest_screen'

        with open("quest.data", "r") as current_quest_file:
            current_quest_data = json.load(current_quest_file)
            current_quest_file.close()

        existed_quest_id = []
        for check_quest in current_quest_data:
            if 'quest_id' in check_quest.keys():
                existed_quest_id.append(int(check_quest['quest_id']))
        next_quest_id = max(existed_quest_id) + 1

        df = ep.to_parse_excel(new_file_path)
        new_quest_list = ep.df_to_list(df)
        new_quest_list = ep.clean_quest_list(new_quest_list, next_quest_id)

        current_quest_data.extend(new_quest_list)
        with open("quest.data", "w") as quest_file:
            json.dump(current_quest_data, quest_file, indent = 4)
            quest_file.close()

        print ('The path from select_file() after completion is: {}'.format(new_file_path))












# Screen that displaying current progress of a student.
class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)
        self.achieved_drive = 0
        self.achieved_knowledge = 0
        self.achieved_action = 0
        self.achieved_strategy = 0

    # Trigger for import feature.
    def file_import(self):
        pass

    # Trigger for export feature, details of registered quests and cumulation of achieved points will be write into output.xlsx file.
    def file_export(self):
        achievement = {'Achieved Drive': self.achieved_drive,
                        'Achieved Knowldge': self.achieved_knowledge,
                        'Achieved Action': self.achieved_action,
                        'Achieved Strategy': self.achieved_strategy}



        with open("user.data") as user_file:
            user_data = json.load(user_file)
            user_file.close()

        user_data.append(achievement)
        df = pandas.DataFrame.from_dict(user_data)
        df.to_excel('output.xlsx')

        user_data.remove(achievement)
        with open("user.data", "w") as user_file:
            json.dump(user_data, user_file, indent = 4)
            user_file.close()

        a_popup = PopUpBoard('Current status exported to output.xls')
        a_popup.show_popup()




























    # Trigger the filter feature in Quest Screen.
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


    # Counting current achievement, in terms of four catagory.
    def information_func(self):

        drive_p_total = 0
        drive_p = 0

        knowledge_p_total = 0
        knowledge_p = 0

        strategy_p_total = 0
        strategy_p = 0

        action_p_total = 0
        action_p = 0

        with open("user.data", "r") as user_file:
            user_data = json.load(user_file)

            for quest in user_data:
                if quest["user_is_complete"]:
                    drive_p += int(quest["quest_drive"])
                    knowledge_p += int(quest["quest_knowledge"])
                    strategy_p += int(quest["quest_strategy"])
                    action_p += int(quest["quest_action"])

        self.achieved_drive = drive_p
        self.achieved_knowledge = knowledge_p
        self.achieved_action = action_p
        self.achieved_strategy = strategy_p

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

        self.ids.prog_action.max = 150
        self.ids.prog_action.value = action_p
        self.ids.action.text = 'Action\n' + str(action_p) + '/' + str(
            150)

        percent = float(drive_p + action_p + strategy_p + knowledge_p)
        percent = int((percent / 600.0) * 100.0)
        self.ids.progress_tr.text = '{}%\nLevel\nProgress'.format(percent)
        quest_file.close()
        user_file.close()

































# Screen that display all available quests and registered quests.
class QuestScreen(Screen):

    def __int__(self, **kwargs):
        super(QuestScreen, self).__init__(**kwargs)
        now = datetime.datetime.now()
        self.current_time = int(str(self.now.year) + str(self.now.month) + str(self.now.day) + str(self.now.hour) + str(self.now.minute) + str(self.now.second) + str(self.now.microsecond))
        self.c_drive_status = 1
        self.c_knowledge_status = 1
        self.c_action_status = 1
        self.c_strategy_status = 1

    # Register a new quest, send to Details Screen for completion.
    def to_details(self, instance):
        quest_id = int(instance.text[0:3])
        print('The instance has a quest id of #{}'.format(quest_id))
        for entry in get_next_entry():
            if int(entry['quest_id']) == quest_id:

                # Check if the quest (the user is tring to register) reach maxinum allow repetition time.
                if entry['quest_max_repeat'] is not False:
                    if entry['quest_max_repeat'] == 0:
                        max_allowed_repetition = entry['quest_max_repeat'] + 1
                    else:
                        max_allowed_repetition = entry['quest_max_repeat']

                    with open("user.data", "r") as user_file:
                        user_data = json.load(user_file)
                        user_file.close()

                    repeat_counter = 0
                    for user_entry in user_data:
                        if int(user_entry['quest_id']) == quest_id:
                            repeat_counter += 1

                    under_repeat_flag = True
                    if repeat_counter >= max_allowed_repetition:
                        under_repeat_flag = False
                        a_popup = PopUpBoard('Maxnium repition reached. \n' + 'Allow: ' + str(max_allowed_repetition) + '    Current: ' + str(repeat_counter))
                        a_popup.show_popup()


                if under_repeat_flag:
                    user_quest_id = add_new_user_quest(self, entry)
                    print('Proceed to the details for user_quest #{}'.format(user_quest_id))
                    self.parent.transition.direction = 'left'
                    self.parent.current = 'details_screen'

                break


    # Filter for quest with point(s) reward on Drive.
    def set_drive(self):
        if self.ids.filter_drive.state == 'down':
            filter_status['drive_status'] = 1
            print("Down: {}".format(filter_status))
        else:
            filter_status['drive_status'] = 0
            print("Down: {}".format(filter_status))
        self.on_enter()

    # Filter for quest with point(s) reward on Knowledge.
    def set_knowledge(self):
        if self.ids.filter_knowledge.state == 'down':
            filter_status['knowledge_status'] = 1
        else:
            filter_status['knowledge_status'] = 0
        self.on_enter()

    # Filter for quest with point(s) reward on Action.
    def set_action(self):
        if self.ids.filter_action.state == 'down':
            filter_status['action_status'] = 1
        else:
            filter_status['action_status'] = 0
        self.on_enter()

    # Filter for quest with point(s) reward on Strategy.
    def set_strategy(self):
        if self.ids.filter_strategy.state == 'down':
            filter_status['strategy_status'] = 1
        else:
            filter_status['strategy_status'] = 0
        self.on_enter()

    # Display already registered quest(s) in Details Screen.
    def set_registered(self):
        if self.ids.filter_registered.state == 'down':
            self.on_enter(1)
        else:
            self.on_enter()

    # Show already registered quest(s) in Details Screen.
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
        self.parent.transition.direction = 'left'
        self.parent.current = 'details_screen'


    # Dynamically generate button (with info regarding quests) with respect to filters.
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




    # Clean out all activating filters when exit from Quest Screen.
    def on_leave(self):
        filter_status['drive_status'] = 0
        filter_status['knowledge_status'] = 0
        filter_status['action_status'] = 0
        filter_status['strategy_status'] = 0


        self.ids.filter_drive.state = 'normal'
        self.ids.filter_knowledge.state = 'normal'
        self.ids.filter_action.state = 'normal'
        self.ids.filter_strategy.state = 'normal'
        self.ids.filter_registered.state = 'normal'






































# Screen for completing, deleting, or simply viewing the details of a specific registered quest.
class DetailsScreen(Screen):

    def __init__(self, **kwargs):
        super(DetailsScreen, self).__init__(**kwargs)

    # Display the staus of a registered quest.
    def on_enter(self):
        shared_data = App.get_running_app().shared_data

        with open("user.data", "r") as user_file:
            user_data = json.load(user_file)

        # If the viewing quest is just canceled/deleted, display the pervious quest.
        target_found_flag = False
        if len(user_data) > 0:
            target_entry = user_data[-1]
            target_found_flag = True

        for entry in user_data:
            if entry['user_quest_id'] == shared_data.current_user_quest_id:
                target_entry = entry
                target_found_flag = True
                break

        # If no registered quest left, pop a warning and exit to Quest Screen.
        if not target_found_flag:
            a_popup = PopUpBoard('No registered quest,\n you may go and register a quest in Quest Screen.')
            a_popup.show_popup()
            return

        self.ids.label_quest_id.text = 'Quest ID: ' + str(target_entry['quest_id'])
        self.ids.label_unique_id.text = str(target_entry['user_quest_id'])


        self.ids.label_drive.text = 'Drive: ' + str(target_entry['quest_drive'])
        self.ids.label_knowledge.text = 'Knowledge: ' + str(target_entry['quest_knowledge'])
        self.ids.label_action.text = 'Action: ' + str(target_entry['quest_action'])
        self.ids.label_strategy.text = 'Strategy: ' + str(target_entry['quest_strategy'])

        self.ids.label_repeatable.text = 'Repeatable: ' + str(target_entry['quest_is_repeatable'])
        self.ids.label_max_repeat.text = 'Max Repeat: ' + str('Infinity' if target_entry['quest_max_repeat'] is False else target_entry['quest_max_repeat'])
        self.ids.label_repeat_time.text = 'Repeated Time(s): ' + str(target_entry['user_repeat_time'])
        self.ids.label_completion.text = 'Completion: ' + ('Yes' if target_entry['user_is_complete'] else 'No')

        self.ids.label_description.text = 'Quest Description: ' + '\n\n' + str(target_entry['quest_description'])
        self.ids.label_hint.text = 'Quest Hint: ' + '\n\n' + str(target_entry['quest_hint'])
        self.ids.label_reflection.text = 'Reflection ' + '\n\n' + str(target_entry['user_reflection'])

    # Complete the current quest and submit the reflection (edit on user.data file).
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

    # Delete the current quest's entry from user.data file.
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

        self.parent.transition.direction = 'right'
        self.parent.current = 'quest_screen'

        self.on_enter()

    # Reset TextInput area for reflection.
    def on_leave(self):
        self.reflection_input.text = ''












# A universally callable function for pop-ups.
class PopUpBoard():
    # Object takes error message as input.
    def __init__(self, error_message_input = ''):
        self.error_message = str(error_message_input)

    # Display a full pop-up window with title, error message, and dismiss button.
    def show_popup(self):
        """
        This function pop a pop-up window with error_message displayed.
        """
        content = BoxLayout(orientation='vertical')
        message_label = Label(text=self.error_message)
        dismiss_button = Button(text='OK')
        content.add_widget(message_label)
        content.add_widget(dismiss_button)
        popup = Popup(title='Error', content=content, size_hint=(0.5, 0.3))
        dismiss_button.bind(on_press=popup.dismiss)
        popup.open()


# App class
class managerApp(App):
    shared_data = ShareData()

# Entrace of the program.
if __name__ == '__main__':
    managerApp().run()