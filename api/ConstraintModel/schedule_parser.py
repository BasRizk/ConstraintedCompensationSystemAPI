# -*- coding: utf-8 -*-
"""
ScheduleParser
"""
import re
import pandas as pd

class ScheduleParser:
    """
    Contains Logic for parsing schedule excel-sheet and
    listifying data up to the slot specific info level
    """
    def __init__(self,
                 filename="api/ConstraintModel/MET_Winter19_schedule_31131.xlsx",
                 sheet_names_list=\
                     ["Saturday", "Sunday", "Monday",
                      "Tuesday", "Wednesday", "Thursday"],
                 headers_list=\
                     ["GROUP", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH"],
                 columns_indices_to_use=[1, 2, 3, 4, 5, 6],
                 list_of_ignored=["1architecture", "9 csen", "9 dmet"]):
        self.filename = filename
        self.sheet_names = sheet_names_list
        self.headers = headers_list
        self.columns_to_use = columns_indices_to_use
        self.list_of_ignored = list_of_ignored

    def parse_schedule(self):
        """
        Reads the excel sheet using pandas according to the given
        sheet_names, headers, and columns_to_use lists,
        and parses recursively extracting the schedule days up to
        the groups slot level
        """
        schedule_file = pd.read_excel(self.filename,
                                      sheet_name=self.sheet_names,
                                      index=None,
                                      names=self.headers,
                                      header=None,
                                      usecols=self.columns_to_use)
        return self.extract_days(schedule_file), self.sheet_names, self.headers

    def clean_rows(self, schedule):
        """
        Cleans the rows read from the schedule excel file,
        deleting some rows such as containing "free", and "day off" in FIRST column
        and clearing up any rows corresponding to the titles refered to in
        list_of_dumb given in the instance intialization of the class
        """
        schedule = schedule.dropna(how="all", subset=self.headers[:])
        schedule = schedule.apply(lambda x: x.astype(str).str.lower())
        list_of_dumb = [
            "rooms", "large lecture halls", "small lecture halls", "cs labs"
        ]
        for to_dumb in list_of_dumb:
            schedule =\
                schedule[schedule["GROUP"] != to_dumb]
        schedule = schedule[schedule["FIRST"] != "day off"]
        schedule = schedule[schedule["FIRST"] != "free"]

        return schedule

    def extract_groups(self, schedule):
        """
        Extracts groups out of the schedule excelsheet,
        cutting basically the schedule into subsets corresponding
        to each group
        """
        groups_zero_indices =\
            schedule.index[schedule["GROUP"]!="nan"].tolist()
        groups_schedules = {}
        for i_index in range(len(groups_zero_indices)):
            start_exist_index = groups_zero_indices[i_index]
            if i_index == (len(groups_zero_indices) - 1):
                group_schedule =\
                    schedule[start_exist_index:]
            else:
                end_exist_index = groups_zero_indices[i_index + 1]
                group_schedule =\
                    schedule[start_exist_index:end_exist_index]
            group_name = group_schedule["GROUP"].iloc[0]
            if group_name in self.list_of_ignored:
                continue
            groups_schedules[group_name] = group_schedule
        return groups_schedules

    def extract_days(self, schedule):
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
            day_schedule = self.clean_rows(day_schedule).reset_index(drop=True)
            groups_schedules = self.extract_groups(day_schedule)
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

    def get_slot_specific_info(self, title):
        """
        Returns extracted information out of excel sheet titled slot
        into the format:
             (TYPE, SUBJECT, SUBGROUPS)
        """
        def is_tut(title):
            matches = re.search("^([a-z&. ]+)(tut)?[ ]*[t]?(\d+[,\d]*)[ \S]*$",
                                title)
            if matches:
                return ("tut", matches[1], matches[3].split(","))
            # Special case ex. 2 tut
            matches = re.search("^(\d+)*[ ]*([a-z]+)(,[\S ]*)?$", title)
            if matches:
                if matches[2] == "tut":
                    return ("tut", "csen101arch", matches[1].split(","))
                else:
                    #        print("another type of tut")
                    return ("tut", matches[2], matches[1].split(","))
            return None

        def is_lab(title):
            matches = re.search("^([a-z. ]+)(lab|l)[ ]*(\d+[,\/\d]*)$", title)
            if matches:
                #        return ("lab", matches[1], re.split("[,\/]+", matches[3]))
                return ("lab", matches[1], re.split("[,\/]+", matches[3]))

        #    matches = re.search("^([a-z ]+)( l )(\d+[,\d]*)$", title)
        #    if matches:
        ##        print("another_type_of_lab")
        ##        print(matches[0])
        #        return ("lab", matches[1], matches[3].split(","))
            return None

        def is_lec(title):
            """
            Returns subject name and lecture hall
            """
            matches = re.search("^([a-z& ]*)h(\d+[,\d]*)( \/[\S ]*)?$", title)
            if matches:
                if matches[1] and (matches[1] != ""):
                    return ("small_lec", matches[1], matches[2].split(","))
                # Not named lecture
                return ("small_lec", matches[2], matches[2].split(","))
            # Special case ex.  'what-ever lec[ ]?((room))?'
            matches = re.search("^([a-z&\- ]*)lec[ ]?(\(room\))?$", title)
            if matches:
                return ("small_lec", matches[1], matches[1].split(","))

            return None

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

    def allocate_slot(self, slot_type, available_locations):
        """
        Assigns a slot location based on the available rooms set at current moment
        and returns left-overs
        0..49 Rooms, 50..54 Large Halls, 55..55 Small Hall, 56..63 Labs
        """
        if (slot_type == "lab"):
            loc_i = 3
            offset = 56
        elif (slot_type == "tut"):
            loc_i = 0
            offset = 0
        elif ("lec" in slot_type):
            loc_i = 1
            offset = 50
    #    print(slot_type)
        if available_locations[loc_i] > 0:
            location = offset + available_locations[loc_i] - 1
            available_locations[loc_i] -= 1

    #        print(location)
        elif ("lec" in slot_type):
            loc_i = 2
            offset = 55
            if (available_locations[loc_i] > 0):
                location = offset + available_locations[loc_i] - 1
                available_locations[loc_i] -= 1
        elif ("lab" in slot_type):
            loc_i = 1
            offset = 0
            if (available_locations[loc_i] > 0):
                location = offset + available_locations[loc_i] - 1
                available_locations[loc_i] -= 1
        else:
            print("ERROR: allocation of type " + slot_type)
            print("Available locations: " + str(available_locations))
        return location, available_locations

    def listify_a_slot(self, time, day, group, title, available_locations):
        """
        Converts one scheduled excel titled slot to one or more slot tuple form
            (NUM, SUBJECT, TYPE, GROUP, SUBGROUP, LOCATION)
        """
        time_num = self.headers.index(time)
        day_num = self.sheet_names.index(day)
        slot_num = (time_num - 1) + (day_num * 5)
        slot_type, slot_subject, subgroups = self.get_slot_specific_info(title)

        all_slots = []
        for subgroup in subgroups:
            if "lec" in slot_type:
                subgroup = group
            else:
                subgroup = group + " " + subgroup

    #        if "lec" in slot_type and slot_num == 6:
    #            print(str(slot_num) + " " + title)
    #            print(str(slot_num) + " " + str(available_locations))
            location, available_locations =\
                self.allocate_slot(slot_type, available_locations)

            slot_formatted =\
                (slot_num, slot_subject, slot_type, group, subgroup, location)
            #        if slot_num == 6 and "lec" in slot_type:
            #            print(str(slot_num)+","+slot_subject+","+slot_type+","+group+","+subgroup + "," + str(location))
            all_slots.append(slot_formatted)

        return all_slots, available_locations

    def define_available_locations(self):
        """
        Returns a fresh list of available locations per one slot time (NUM)
        """
        all_available_locations = {}
        for time in self.headers[1:]:
            all_available_locations[time] = [50, 5, 1, 8]
        return all_available_locations

    def listify_slots(self, extracted_schedule):
        """
        Listify schedule in slots form:
            (NUM, SUBJECT, TYPE, GROUP, SUBGROUP, LOCATION)
        """
        list_of_formatted_slots = []
        for day in self.sheet_names:
            all_available_locations = self.define_available_locations()
            day_schedule = extracted_schedule[day]
            for group in day_schedule.keys():
                group_day = day_schedule[group]
                for time in self.headers[1:]:
                    slot_contents = group_day[time]
                    for title in slot_contents:
                        if title == "nan" or title == "free":
                            continue
                        slots, all_available_locations[time] =\
                            self.listify_a_slot(time, day, group, title,
                                           all_available_locations[time])
                        for slot in slots:
                            list_of_formatted_slots.append(slot)

    #            print(available_locations)
        return list_of_formatted_slots

    def convert_to_excel(self, all_slots, output_filename="formatted_schedule.xlsx"):
        def stringify(multiple_tuples):
            out_str = ""
            for a_tuple in multiple_tuples:
                out_str += str(a_tuple) + "\n"
            return out_str
        
        all_groups = set()
        all_slots_collapsed = {}
        for slot in all_slots:
            (slot_num, _, _, group, _, _) = slot
            one_slot_collapse = all_slots_collapsed.get(slot_num)
            if not one_slot_collapse:
                all_slots_collapsed[slot_num] = []
                one_slot_collapse = all_slots_collapsed[slot_num]
            one_slot_collapse.append(slot)
            all_groups.add(group)
        all_groups = sorted(all_groups)
        
        all_slots_grouped = {}
        for slot_num_key in all_slots_collapsed.keys():
            list_of_slots = all_slots_collapsed.get(slot_num_key)
            all_slots_grouped[slot_num_key] = {}
            for slot in list_of_slots:
                (slot_num, subject, slot_type, group, subgroup, location) = slot
                one_slot_group = all_slots_grouped[slot_num_key].get(group)
                if not one_slot_group:
                    all_slots_grouped[slot_num_key][group] = []
                    one_slot_group = all_slots_grouped[slot_num_key][group]
                # subgroup = subgroup.strip(group)
                one_slot_group.append((slot_num, subject, slot_type, subgroup, location))
        
        writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')
        workbook=writer.book
        wrap_format = workbook.add_format({'text_wrap': True})
     
        slots_grouped_per_day = {}
        for day in self.sheet_names:
            slots_grouped_per_day[day] = {}
            # registered_times = []
            for time in self.headers[1:]:
                time_num = self.headers.index(time)
                day_num = self.sheet_names.index(day)
                slot_num = (time_num - 1) + (day_num * 5)
                
                # groups_at_one_slot = all_slots_grouped.get(slot_num)
                # if not groups_at_one_slot:
                #     continue
                # registered_times.append(time)
                # for group in groups_at_one_slot.keys():
                for group in all_groups:
                    one_group_slots = slots_grouped_per_day[day].get(group)
                    if not one_group_slots:
                        slots_grouped_per_day[day][group] = []
                        one_group_slots = slots_grouped_per_day[day][group]
                    existing_group_slots = all_slots_grouped.get(slot_num)
                    if existing_group_slots:
                        existing_group_slots = existing_group_slots.get(group)
                        if existing_group_slots:
                            one_group_slots.append(stringify(existing_group_slots))
                            continue
                    one_group_slots.append("")
        
            grouped_slot_df = pd.DataFrame.from_dict(slots_grouped_per_day[day],
                                                     orient='index',
                                                     columns=self.headers[1:])
            
            worksheet=workbook.add_worksheet(day)
            writer.sheets[day] = worksheet
            grouped_slot_df.to_excel(writer, sheet_name=day)
            
            for idx, col in enumerate(grouped_slot_df):  # loop through all columns
                # series = grouped_slot_df[col]
                # max_len = max((
                #     series.astype(str).map(len).max(),  # len of largest item
                #     len(str(series.name))  # len of column name/header
                #     )) + 1  # adding a little extra space
                worksheet.set_column(idx, idx, 40, wrap_format)  # set column width

        writer.save()
                