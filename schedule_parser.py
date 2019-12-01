# -*- coding: utf-8 -*-

import pandas as pd

filename = "MET_Winter19_schedule_31131.xlsx"
sheet_names = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
headers = ["GROUP", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH"]
columns_to_use = [1,2,3,4,5,6]

def clean_rows(schedule):
    schedule = schedule.dropna(how="all", subset=headers[1:])
    schedule = schedule.apply(lambda x: x.astype(str).str.lower())
    list_of_dumb = ["rooms", "large lecture halls", "small lecture halls", "cs labs"]
    for to_dumb in list_of_dumb:
        schedule =\
            schedule[schedule["GROUP"] != to_dumb]

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
        day_schedule = schedule_file[sheet_names[i_day]]
        day_schedule = clean_rows(day_schedule).reset_index(drop=True)
        groups_schedules = extract_groups(day_schedule)
        days_schedules[day_name] = groups_schedules
    return days_schedules
# =============================================================================
# TODO EXTRACT ACCORDING TO SLOTS IN THE PROLOG SCHEDULER FILE FORMAT
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
def convert_slots():  
    return None

schedule_file = pd.read_excel(filename, sheet_name = sheet_names, index=None,
                              names=headers, header=None, usecols=columns_to_use)
days_schedules = extract_days(schedule_file)




