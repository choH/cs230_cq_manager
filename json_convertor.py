import json
import datetime

now = datetime.datetime.now()

def get_next_entry():
    with open('/Users/zhonghenry/Desktop/cq_manager/quest.data') as json_file:
        json_data = json.load(json_file)
        for entry in json_data:
            yield entry




def add_new_user_quest(entry):
    user_entry = entry
    user_quest_id = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second) + str(now.microsecond)
    user_entry['user_quest_id'] = int(user_quest_id)

    user_repeat_time = get_user_repeat_time(user_entry['quest_id'])
    user_entry['user_repeat_time'] = user_repeat_time
    user_entry['user_reflection'] = 'N/A'
    user_entry['user_is_complete'] = False
    user_entry['user_complete_date'] = False

    with open('/Users/zhonghenry/Desktop/cq_manager/user_dummy.data') as user_file:
        user_data = json.load(user_file)
        user_file.close()

    user_data.append(user_entry)

    with open('/Users/zhonghenry/Desktop/cq_manager/user_dummy.data', "w") as user_file:
        json.dump(user_data, user_file)
        user_file.close()
    return int(user_quest_id)

def get_user_repeat_time(quest_id):
    repeat_counter = 1
    for an_entry in get_next_entry():
        if an_entry['quest_id'] == quest_id:
            repeat_counter += 1
    return repeat_counter

t = 0
for i in get_next_entry():
    if t == 0:
        t += 1
        continue
    else:
        output = add_new_user_quest(i)
        print(output)
        break
