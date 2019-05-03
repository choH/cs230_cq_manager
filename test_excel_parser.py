import excel_parser as ep
import pandas, json


input_file_path = '/Users/zhonghenry/Desktop/cq_manager/test_excel.xlsx'


df = ep.to_parse_excel(input_file_path)
quest_list = ep.df_to_list(df)
quest_list = ep.clean_quest_list(quest_list)

with open("test_excel_json.data", "w") as test_file:
    json.dump(quest_list, test_file, indent = 4)
    test_file.close()

def test_excel_parser():
    with open("test_excel_json.data", "r") as test_file:
        test_data = json.load(test_file)
    assert test_data[0]['quest_description'] == 'Sign up for the CQ Mobile App!'
    assert test_data[1]['quest_is_repeatable'] == 'Yes'
    assert test_data[3]['quest_drive'] == 2
    assert test_data[5]['quest_hint'] == 'Invite a friend tojoin you for dinner with someone in your CQ Network.'


test_excel_parser()