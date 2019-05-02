from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button

import json


def get_next_user_quest():
    with open('user.data') as user_file:
        user_data = json.load(user_file)
        for entry in user_data:
            yield entry


class DetailsScreen(Screen):
    def popup(self):
        """
        This function implements popup widget functionality, whereby should an
        exception be thrown, a popup will be created to alert the user the
        error. The user then must acknowledge the popup by clicking the 'Ok'
        button. This physical instantiation of this includes a general
        BoxLayout for the entire popup, a Label widget to display the error
        message, and an 'Ok' button to accept the error.
        :param: None
        :return: None
        """
        
        content = BoxLayout(orientation='vertical')
        error_label = Label(text="Please fill all required fields")
        dismiss_button = Button(text='Ok')
        content.add_widget(error_label)
        content.add_widget(dismiss_button)
        popup = Popup(title='You must have a response to submit quest', content=content, size_hint=(.3, .25),
                      auto_dismiss=False)
        dismiss_button.bind(on_press=popup.dismiss)
        popup.open()

    def entry(self):
        quest_holder = False
        for quest in get_next_user_quest():
            if quest["user_quest_id"] == 2:
                quest_holder = quest
                break
        self.ids.description.text = 'Quest Description: \n' + '    ' + str(quest_holder["quest_description"])
        self.ids.hint.text = 'Hint: \n' + '     ' + str(quest_holder["quest_hint"])
        self.ids.drive.text = 'Drive: ' + str(quest_holder["quest_drive"])
        self.ids.knowledge.text = 'Knowledge: ' + str(quest_holder["quest_knowledge"])
        self.ids.strategy.text = 'Strategy: ' + str(quest_holder["quest_strategy"])
        self.ids.action.text = 'Action: ' + str(quest_holder["quest_action"])

    def process_submit(self):
        quest_holder = False
        for quest in get_next_user_quest():
            if quest["user_quest_id"] == 2:
                quest_holder = quest
                break

        if self.ids.response.text == '':
            self.popup()
        else:
            quest_holder["user_reflection"] = self.ids.response.text
            quest_holder["user_is_complete"] = True

        user_data = json.load(open("user.data"))
        for i in xrange(len(user_data)):
            if user_data[i]["user_quest_id"] == 2:
                user_data.pop(i)
                break

        user_data.append(quest_holder)
        with open("user.data", "w") as json_file:
            json.dump(user_data, json_file, indent=4)
            json_file.close()


class DetailsApp(App):
    pass


if __name__ == '__main__':
    DetailsApp().run()
