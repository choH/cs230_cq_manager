import json
from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.config import Config
from datetime import datetime
from kivy.uix.progressbar import ProgressBar
from kivy.core.text import Label as CoreLabel
from kivy.lang.builder import Builder
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock
from kivy.lang import Builder




class Profile(Screen):
    def __init__(self, **kwargs):
        super(Profile, self).__init__(**kwargs)

    def switch(self, quest_type):
        shared_data = App.get_running_app().shared_data
        shared_data._screen_pass_string = quest_type


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
                if quest["user_is_complete"] == "True":
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
        #self.ids.user_data.text = 'User: \nDate: \n {}% Level Progress'.format(percent)
        self.ids.progress_tr.text = '{}%\nLevel\nProgress'.format(percent)
        quest_file.close()
        user_file.close()

            #data.append(information)
        #with open(filename, "w") as json_file:
            #json.dump(data, json_file)
            #json_file.close()


class Quests(Screen):
    def check_function(self):
        shared_data = App.get_running_app().shared_data
        if shared_data._screen_pass_string != None:
            self.ids.quests_button.text = 'Filtered by {}'.format(shared_data._screen_pass_string)
            shared_data._screen_pass_string = None


class Completion(Screen):
    pass


class SharedData:
    def __init__(self, screen_passer=None):
        self._screen_pass_string = screen_passer



class managerApp(App):
    shared_data = SharedData()


class ProfileApp(App):
    def build(self):
        self.root = Builder.load_file('profile.kv')
        return Profile()

if __name__ == '__main__':
    #ProfileApp().run()
    managerApp().run()
