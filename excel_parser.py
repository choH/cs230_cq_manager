import pandas as pd
import json

# input_file_path = '/Users/zhonghenry/Desktop/cq_manager/cq_dummy.xlsx'
# input_file_path = '/Users/zhonghenry/Desktop/cq_manager/cq_dummy.xlsx'


def to_parse_excel(input_file_path):
    df = pd.read_excel(input_file_path)
    df.set_axis(['quest_description',
                'quest_is_repeatable',
                'quest_drive',
                'quest_knowledge',
                'quest_strategy',
                'quest_action',
                'quest_max_repeat',
                'quest_hint'], axis=1, inplace=True)
    df.fillna('nan', inplace=True)
    return df






def get_next_quest(df):
    df_height = df.shape[0]
    df_width = df.shape[1]
    key_list = tuple(df)
    for i in range(df_height):
        temp_quest = {}
        for j in range (df_width):
            temp_key = key_list[j]
            temp_quest[temp_key] = df.iloc[i,j]
        yield temp_quest


def df_to_list(df):
    quest_list = []
    for a_quest in get_next_quest(df):
        quest_list.append(a_quest)
    return quest_list


def clean_quest_list(quest_list):
    quest_id_counter = 1
    for a_quest in quest_list:
        for k, v in a_quest.items():
            if k == 'quest_hint' and v == 'nan':
                a_quest[k] = 'N/A'
            elif (k == 'quest_drive' or \
                    k == 'quest_knowledge' or \
                    k == 'quest_strategy' or \
                    k == 'quest_action'):
                    if v == 'nan':
                        a_quest[k] = 0
            elif k == 'quest_is_repeatable' and v == 'No':
                    a_quest['quest_max_repeat'] = 0
            elif k == 'quest_is_repeatable' and v == 'Yes':
                    if a_quest['quest_max_repeat'] == 'nan':
                        a_quest['quest_max_repeat'] = False
            else:
                pass
        if a_quest['quest_is_repeatable'] == 'nan':
            quest_list.remove(a_quest)
            continue
        a_quest['quest_id'] = str(quest_id_counter).zfill(3)
        quest_id_counter += 1

    return quest_list



# clean_quest_list(quest_list)
# with open('/Users/zhonghenry/Desktop/cq_manager/quest_dummy.data', "w") as quest_file:
#     json.dump(quest_list, quest_file, indent = 4)
#     quest_file.close()
