# -*- coding: utf-8 -*-

import pandas as pd
import re

filename = "MET_Winter19_schedule_31131.xlsx"
sheet_names = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
headers = ["GROUP", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH"]
columns_to_use = [1,2,3,4,5,6]

def parse_schedule():
    schedule_file = pd.read_excel(filename, sheet_name = sheet_names, index=None,
                                  names=headers, header=None, usecols=columns_to_use)    
    return extract_days(schedule_file), sheet_names, headers

def clean_rows(schedule):
    schedule = schedule.dropna(how="all", subset=headers[1:])
    schedule = schedule.apply(lambda x: x.astype(str).str.lower())
    list_of_dumb = ["rooms", "large lecture halls", "small lecture halls", "cs labs",
                    "1architecture", "1Engineering I", "1Engineering II",
                    "1Engineering III", "1Engineering IV"]
    for to_dumb in list_of_dumb:
        schedule =\
            schedule[schedule["GROUP"] != to_dumb]
    
    schedule = schedule[schedule["FIRST"] != "day off"]
    
    return schedule

def extract_groups(schedule):
    groups_zero_indices =\
        schedule.index[schedule["GROUP"]!="nan"].tolist()
    groups_schedules = {}
    for i_index in range(len(groups_zero_indices)):
        start_exist_index = groups_zero_indices[i_index]
        if i_index == (len(groups_zero_indices)-1):
            group_schedule =\
                schedule[start_exist_index:]
        else:
            end_exist_index = groups_zero_indices[i_index+1]
            group_schedule =\
                schedule[start_exist_index:end_exist_index]
        group_name = group_schedule["GROUP"].iloc[0]
        groups_schedules[group_name] = group_schedule
    return groups_schedules

def extract_days(schedule):
    days_schedules = {}
    for i_day in range(len(sheet_names)):
        day_name = sheet_names[i_day]
        day_schedule = schedule[sheet_names[i_day]]
        day_schedule = clean_rows(day_schedule).reset_index(drop=True)
        groups_schedules = extract_groups(day_schedule)
        days_schedules[day_name] = groups_schedules
    return days_schedules
# =============================================================================
#  EXTRACT ACCORDING TO SLOTS IN THE PROLOG SCHEDULER FILE FORMAT
#       (NUM, SUBJECT, TYPE, GROUP, SUBGROUP, LOCATION)
#
#    A SLOT is to be assigned to a LOCATION and a NUM (if possible), Or it cannot exist
#    
#    VARIABLES:
#    
#    A SLOT = (NUM, SUBJECT, TYPE, GROUP, SUBGROUP, LOCATION)
#    EX (3, GRAPHICS, LAB, 7 CSEN, 7 CSEN T18, 1)
#    
#    NUM: {0..29} .. 5X6
#    
#    SUBJECT: Any sort of subject
#    
#    TYPE: {LAB, SMALL_LEC, BIG_LEC, TUT}
#    
#    GROUP: The group taken the course (ex. 7 CSEN)
#    
#    SUBGROUP: The subgroup represents the tut. lab. or a lec. group (basically repeated) (ex. 7 CSEN T18)
#    
#    LOCATION: {0..63}, where 0..49 Rooms, 50..54 Large Halls, 55..55 Small Hall, 56..63 Labs  
# 
# =============================================================================


# RETURNED FORMAT (TYPE, SUBJECT, SUBGROUPS)
def is_tut(title):
    # TODO let tut only be csen as it seems to be csen101    
    matches = re.search("^([a-z&. ]+)(tut)?[ ]*[t]?(\d+[,\d]*)[ \S]*$", title)
    if matches:        
        return ("tut", matches[1], matches[3].split(","))
    # Special case ex. 2 tut
    matches = re.search("^(\d+)*[ ]*([a-z]+)(,[\S ]*)?$", title)
    if matches:
        if matches[2] == "tut":
            return ("tut", "csenarch", matches[1].split(","))
        else:
    #        print("another type of tut")
            return ("tut", matches[2], matches[1].split(","))
    return None

def is_lab(title):
    matches = re.search("^([a-z. ]+)( lab )(\d+[,\/\d]*)$", title)
    if matches:
        return ("lab", matches[1], re.split("[,\/]+", matches[3]))
    matches = re.search("^([a-z ]+)( l )(\d+[,\d]*)$", title)
    if matches:
#        print("another_type_of_lab")
#        print(matches[0])
        return ("lab", matches[1], matches[3].split(","))
    return None

def is_lec(title):
    # Returns subject name and lecture hall    
    matches = re.search("^([a-z& ]*)h(\d+[,\d]*)( \/[\S ]*)?$", title)
    if matches:
        if matches[1] and (matches[1] != ""):
            return ("small_lec", matches[1], matches[2].split(","))
        # Not named lecture       
        return ("small_lec", matches[2], matches[2].split(","))
    # Special case ex.  'what-ever lec[ ]?((room))?'
    matches = re.search("^([a-z&\- ]*)lec[ ]?(\(room\))?$$", title) 
    if matches:
        return ("small_lec", matches[1], matches[1].split(","))

    return None

def get_slot_specific_info(title):
    # NOTE: tut is the least tightened expression
    #       hence left to the end!        
    lab_info = is_lab(title)
    if lab_info:
        return lab_info
    lec_info = is_lec(title)
    if lec_info:
        return lec_info
    tut_info = is_tut(title)
    if tut_info:
        return tut_info

    print("ERROR: with type: " + str(title))
    return None

def allocate_slot(slot_type, available_locations):
    # 0..49 Rooms, 50..54 Large Halls, 55..55 Small Hall, 56..63 Labs  
    if(slot_type == "lab"):
        loc_i = 3
        offset = 56
    elif(slot_type == "tut"):
        loc_i = 0
        offset = 0
    elif("lec" in slot_type):
        loc_i = 1
        offset = 50
        
    if available_locations[loc_i] > 0:
        location = offset + available_locations[loc_i] - 1
        available_locations[loc_i] -= 1
    else:
        print("ERROR: allocation")
        
    return location, available_locations     

def listify_a_slot(time, day, group, title, available_locations):
    time_num = headers.index(time)
    day_num = sheet_names.index(day)
    slot_num = (time_num - 1) + (day_num*5)
    slot_type, slot_subject, subgroups = get_slot_specific_info(title)
    location, available_locations =\
        allocate_slot(slot_type, available_locations)
    all_slots = []
    for subgroup in subgroups:
        if slot_type == "lec":
            subgroup = group + slot_subject
        else:
            subgroup = slot_subject + subgroup
        slot_formatted =\
            (slot_num, slot_subject, slot_type, group, subgroup, location)
        all_slots.append(slot_formatted)
    return all_slots, available_locations

def listify_slots(extracted_schedule):
    list_of_formatted_slots = []
    for day in sheet_names:
        day_schedule = extracted_schedule[day]
        for group in day_schedule.keys():
            group_day = day_schedule[group]
            available_locations = [50, 5, 1, 8]
            for time in headers[1:]:
                slot_contents = group_day[time]
                for title in slot_contents:
                    if title == "nan" or title == "free":
                        continue
                    slots, available_locations =\
                        listify_a_slot(time, day, group, title,
                                       available_locations)
                    for slot in slots:
                        list_of_formatted_slots.append(slot)
    return list_of_formatted_slots   
