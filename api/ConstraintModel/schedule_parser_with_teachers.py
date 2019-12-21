# -*- coding: utf-8 -*-

import re
import pandas as pd

from schedule_parser import ScheduleParser

class ScheduleParserWithTeachers(ScheduleParser):
    
    teacher_regex = r"^[\S\s]+\(([A-Za-z\d, ]+)\)$"   
    dummy_teacher_num = 0
    subject_type_dummy_teacher_dict = {}
    
    def __init__(self,
                 filename="api/ConstraintModel/MET_Winter19_schedule_31131.xlsx",
                 teachers_filename="modifiedSchedule2.xlsx",
                 sheet_names_list=\
                     ["Saturday", "Sunday", "Monday",
                      "Tuesday", "Wednesday", "Thursday"],
                 headers_list=\
                     ["GROUP", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH"],
                 columns_indices_to_use=[1, 2, 3, 4, 5, 6],
                 list_of_ignored=["1architecture", "9 csen", "9 dmet"],
                 list_of_discarded_subjects=['ae','as', 'en', 'de']):
        super().__init__(
                 filename=filename,
                 sheet_names_list=sheet_names_list,
                 headers_list=headers_list,
                 columns_indices_to_use=columns_indices_to_use,
                 list_of_ignored=list_of_ignored,
                 list_of_discarded_subjects=list_of_discarded_subjects)
        self.teachers_filename = teachers_filename
        self.teachers_schedule = None
        
    def parse_teachers_schedules(self):
        """
        Extract teachers names as it
        reads the excel sheet using pandas according to the given
        sheet_names, headers, and columns_to_use lists,
        and parses recursively extracting the schedule days up to
        the groups slot level
        """
        def extract_groups(schedule):
            """
            Extracts groups out of the schedule excelsheet,
            cutting basically the schedule into subsets corresponding
            to each group
            """
            def init_schedule_row():
                schedule_row = {}
                for time in self.headers[1:]:
                    schedule_row[time] = []
                return schedule_row
            
            def append_rows(old_rows, new_row):
                for time in self.headers[1:]:
                    old_rows[time].append(new_row[time])
                    
            def leave_only_tas(schedule_row):
                tas_row = {}
                current_slot = 1
                for title in schedule_row:
                    matches = re.search(self.teacher_regex, title)
                    if matches:
                        tas_row[self.headers[current_slot]] = re.split("[,\/]+", matches[1])
                    else:
                        tas_row[self.headers[current_slot]] = ["nan"]
                        # print("Something is wrong with this title:")
                        # print(title)
                    current_slot += 1
                return tas_row
            
            groups_schedules = {}
            for i_index in range(len(schedule)):
                # schedule[i_index]
                group_name = re.sub('[ ]*\(\S+\)[ ]*', '', schedule.iloc[i_index][0])
                if group_name in self.list_of_ignored:
                    continue
                that_group_schedules = groups_schedules.get(group_name)
                if not that_group_schedules:
                    groups_schedules[group_name] = init_schedule_row()
                    that_group_schedules = groups_schedules[group_name]
                append_rows(that_group_schedules, leave_only_tas(schedule.iloc[i_index][1:]))
                # if that_group_schedules:
                #     append_rows(that_group_schedules,
                #                 leave_only_tas(schedule.iloc[i_index][1:]))
                # else:
                #     groups_schedules[group_name] = leave_only_tas(schedule.iloc[i_index][1:])
                    
            return groups_schedules
    
        def extract_days(schedule):
            """
            Extract days out into panadas dataset out of the excel sheet
            - the days are extracted recusively up to the groups schedule per each day
            - the data are cleaned based on the parameters or defaults given
              in the class instance initialization
            """
            days_schedules = {}
            for i_day in range(len(self.sheet_names)):
                day_name = self.sheet_names[i_day]
                day_schedule = schedule[self.sheet_names[i_day]]
                day_schedule = day_schedule.apply(lambda x: x.astype(str).str.lower())
                day_schedule = day_schedule.reset_index(drop=True)
                groups_schedules = extract_groups(day_schedule)
                days_schedules[day_name] = groups_schedules
            return days_schedules
        
        schedule_file = pd.read_excel(self.teachers_filename,
                                      sheet_name=self.sheet_names,
                                      index=None,
                                      # names=headers,
                                      header=None)
        
        self.teachers_schedule = extract_days(schedule_file)
        return self.teachers_schedule
    
    # def assign_teachers(self, all_slots):
    #     subject_type_subgroup_teacher_dict = {}
    #     assigned_slots = []
    #     for slot in all_slots:
    #         num, subject, slot_type, group, subgroup, location = slot
            
    #         assignment = subject_type_subgroup_teacher_dict.get(subject)
    #         if assignment:
    #             assignment = subject_type_subgroup_teacher_dict

    def assign_teachers(self, slots, teachers):
        # TODO assign teachers regularly to subjects and save in dict
        if len(slots) == 0:
            return []
        
        # if len(slots) > len(teachers):
        #     print("there might be no enough teachers!")
        #     print("Slots:\n" + str(slots) + "\nTeachers:\n" + str(teachers))
        if len(slots) < len(teachers):
            print("there might be no enough slots!")
            print("Slots:\n" + str(slots) + "\nTeachers:\n" + str(teachers))
                
        new_slots = []
        for slot, teacher in zip(slots, teachers):
            num, subject, slot_type, group, subgroup, location = slot
            if teacher == "nan":
                self.dummy_teacher_num += 1
                teacher = "t" + str(self.dummy_teacher_num)
            teacher = teacher.lstrip().rstrip()
            new_slots.append((num, subject, slot_type,
                              group, subgroup, location,
                              teacher))
        return new_slots
    
    def listify_slots(self):
        """
        Listify schedule in slots form:
            (NUM, SUBJECT, TYPE, GROUP, SUBGROUP, LOCATION)
        """
        print("..Listifying slots with teachers.")
        list_of_formatted_slots = []
        for day in self.sheet_names:
            all_available_locations = self.define_available_locations()
            day_schedule = self.extracted_schedule[day]
            
            teachers_day_schedule = self.teachers_schedule[day]
            
            for group in day_schedule.keys():
                group_day = day_schedule[group]
                
                teachers_group_day = teachers_day_schedule.get(group)
                if not teachers_group_day:
                    print("WARNING:: group " + str(group) +
                          " @" + str(day) + " discarded.")
                    continue
                
                for time in self.headers[1:]:
                    slot_contents = group_day[time]
                    
                    slot_teachers = teachers_group_day[time]
                    for title, teachers in zip(slot_contents, slot_teachers):
                        if title == "nan" or title == "free":
                            continue
                        
                        slots, all_available_locations[time] =\
                            self.listify_a_slot(time, day, group, title,
                                           all_available_locations[time])
                        new_slots = self.assign_teachers(slots, teachers)
                        # if len(slots) != len(new_slots):
                        #     print("All teachers at this slot: ")
                        #     print(slot_teachers)
                        for slot in new_slots:
                            list_of_formatted_slots.append(slot)
    
        print(str(self.dummy_teacher_num) + " dummy teacher have been assigned.")
        
        return list_of_formatted_slots