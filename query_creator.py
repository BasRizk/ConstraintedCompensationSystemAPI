# -*- coding: utf-8 -*-
from schedule_parser import parse_schedule, listify_slots
import re
          
def clean_subject(subject):
    subject = subject.strip()
    subject = subject.strip("tut").strip().strip("t").strip()
    subject = subject.strip("lab").strip().strip("l").strip()
    return subject

def clean_formatted_slots(formatted_slots):
    cleaned_slots = []
    for (num, subject, slot_type, group, subgroup, location) in formatted_slots:
        subject = clean_subject(subject)
        slot = (num, subject, slot_type, group, subgroup, location)
        cleaned_slots.append(slot)
    return cleaned_slots

def digitize(slots):
    digi_slots = []
    
    types_dict = {
            "big_lec":1,
            "small_lec":2,
            "tut":3,
            "lab":4
            }
    
    # has to begin with 1 to avoid not(0)    
    subjects_dict = {}
    subject_current_num = 1
    groups_dict = {}
    group_current_num = 1
    subgroups_dict = {}
    subgroup_current_num = 1
    
    for (_, subject, _, group, subgroup, _) in slots:
        if not(subjects_dict.get(subject)):
            subjects_dict[subject] = subject_current_num
            subject_current_num += 1
        if not(groups_dict.get(group)):
            groups_dict[group] = group_current_num
            group_current_num += 1
        if not(subgroups_dict.get(subgroup)):
            subgroups_dict[subgroup] = subgroup_current_num
            subgroup_current_num += 1
            
    for (num, subject, slot_type, group, subgroup, location) in slots:
        digi_subject = subjects_dict.get(subject)
        digi_group = groups_dict.get(group)
        digi_type = types_dict.get(slot_type)
        digi_subgroup = subgroups_dict.get(subgroup)
        if not(digi_subject):
            print("Subject " + subject + " does not exist.")
        if not(digi_group):
            print("Group " + group + " does not exist.")
        if not(digi_type):
            print("Type " + slot_type + " does not exist.")
        if not(digi_subgroup):
            print("Subgroup " + subgroup + " does not exist.")
        print(num)
        slot = (num, digi_subject, digi_type, digi_group, digi_subgroup, location)
        digi_slots.append(slot)
    
    return digi_slots

def convert_to_query_format(string):
    return "".join(re.split("['| |\-|.|\"]",str(string)))
    
def listify_on_own(slots, subjects = True, groups = True, subgroups = True):
    all_subjects = set()
    all_groups = set()
    all_subgroups = set()
    for (_, subject, slot_type, group, subgroup, _) in slots:
        if subject == '':
            print("ERROR: subject is empty!")
            print(group)
            print(slot_type)
            print(subject)
        if subjects:
            all_subjects.add(convert_to_query_format(subject))
        if groups:
            all_groups.add(group)
        if subgroups:
            all_subgroups.add(group + subgroup)
        
    return list(all_subjects), list(all_groups), list(all_subgroups)


def create_query(slots, compensation_slot = None, holiday = 0):
    # Note: a day contains 5 slots    
    first_slot_in_holiday = holiday*5
    last_slot_in_holiday = (holiday*5) + 4
    slots_string = "["
    for slot in slots:
        slot_num = slot[0]
        if (slot_num >= first_slot_in_holiday) and (slot_num <= last_slot_in_holiday):
            continue
        slots_string += convert_to_query_format(slot)
        slots_string +=  ","
    
    slots_string = slots_string[:-1] + "]"
    
    subjects, groups, subgroups = listify_on_own(slots)
    subjects = convert_to_query_format(subjects)
    groups = convert_to_query_format(groups)
    subgroups = convert_to_query_format(subgroups)
    
    return "schedule(%s,%s,%s,%s,%s)" %\
         (slots_string, str(holiday), subjects, groups, subgroups)

days_schedules, sheet_names, headers = parse_schedule()
all_slots = listify_slots(days_schedules)
all_slots = clean_formatted_slots(all_slots)
all_slots = digitize(all_slots)
#compensation_slot = ()
query = create_query(all_slots)
#
with open("query_example.txt", "w") as f:
    query_rest = query
    while(True):
        limit = 1000
        if len(query_rest) < limit:
            break
        f.write(query_rest[:limit])
        f.write("\n")
        query_rest = query_rest[limit:]
    f.write(query_rest)