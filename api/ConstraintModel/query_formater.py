"""
QueryFormater
"""
import re


class QueryFormater:
    """
    QueryFormater contains all functions that makes the schedule ready
    for the constraint model injection
    """
    def __init__(self):
        self.subjects_dict = None
        self.groups_dict = None
        self.subgroups_dict = None
        self.teachers_dict = None

    @staticmethod
    def clean_subject(subject):
        """
        Clears up any miss taken text from their subjects
        Ex. data basest -- cut t
            csen tut -- cut tut
            others..
        """
        subject = subject.strip()
        subject = subject.rstrip("tut").strip().rstrip("t").strip()
        subject = subject.rstrip("lab").strip().rstrip("l").strip()
        return subject

    @staticmethod
    def clean_formatted_slots(formatted_slots):
        """
        Clean slots that was already formated into the slot conventions format
        and clears up any miss taken text from their subjects
        Ex. data basest -- cut t
            csen tut -- cut tut
            others..
        """
        cleaned_slots = []
        for (num, subject, slot_type, group, subgroup,
             location, teacher) in formatted_slots:
            subject = QueryFormater.clean_subject(subject)
            slot = (num, subject, slot_type, group, subgroup, location, teacher)
            cleaned_slots.append(slot)
        return cleaned_slots

    def create_dictionaries(self, slots):
        """
        Create digits dictionaries for subjects, groups, subgroups
        """
        # has to begin with 1 to avoid not(0)
        self.subjects_dict = {}
        self.groups_dict = {}
        self.subgroups_dict = {}
        self.teachers_dict = {}

        subject_current_num = 1
        group_current_num = 1
        subgroup_current_num = 1
        teacher_current_num = 1
        
        for (_, subject, _, group, subgroup, _, teacher) in slots:
            if not self.subjects_dict.get(subject):
                self.subjects_dict[subject] = subject_current_num
                subject_current_num += 1
            if not self.groups_dict.get(group):
                self.groups_dict[group] = group_current_num
                group_current_num += 1
            if not self.subgroups_dict.get(subgroup):
                self.subgroups_dict[subgroup] = subgroup_current_num
                subgroup_current_num += 1
            if not self.teachers_dict.get(teacher):
                self.teachers_dict[teacher] = teacher_current_num
                teacher_current_num += 1
                

    def digitize_one_slot(self, slot):
        """
        Digitize one single slot
        """
        num, subject, slot_type, group, subgroup, location, teacher = slot
        digi_subject = self.subjects_dict.get(subject)
        digi_group = self.groups_dict.get(group)
        #        digi_type = types_dict.get(slot_type)
        digi_subgroup = self.subgroups_dict.get(subgroup)
        digi_teacher = self.teachers_dict.get(teacher)

        if not digi_subject:
            print("Subject " + subject + " does not exist.")
        if not digi_group:
            print("Group " + group + " does not exist.")
        if not digi_subgroup:
            print("Subgroup " + subgroup + " does not exist.")
        if not digi_teacher:
            print("Teacher " + teacher + " does not exist.")

        slot = (num, digi_subject, slot_type, digi_group, digi_subgroup,
                location, digi_teacher)

        return slot

    def digitize(self, slots):
        """
        Encodes subjects, subgroups, groups into numbers,
        and creates dictionary of the values
        """

        if not self.subjects_dict:
            self.create_dictionaries(slots)

        digi_slots = []
        for slot in slots:
            slot = self.digitize_one_slot(slot)
            digi_slots.append(slot)

        return digi_slots

    @staticmethod
    def convert_to_query_format(string):
        """
        Clears up any thing that may affect a string for prolog query
        """
        return "".join(re.split(r"['| |\-|.|\"]", str(string)))

    def listify_on_own(self,
                       slots,
                       subjects=True,
                       groups=True,
                       subgroups=True,
                       subjects_inc=None,
                       subgroups_inc=None):
        """
        Listify seperately with no redundancies
        all subjects, all groups, all subgroups
        and may add another subject or subgroup to the set
        """
        all_subjects = set()
        all_groups = set()
        all_subgroups = set()

        for (_, subject, slot_type, group, subgroup, _, teacher) in slots:
            if subject == '':
                print("ERROR: subject is empty!")
                print(group)
                print(slot_type)
                print(subject)
                print(teacher)
            if subjects:
                all_subjects.add(self.convert_to_query_format(subject))
            if groups:
                all_groups.add(group)
            if subgroups:
                all_subgroups.add(group + subgroup)

        if subjects_inc:
            for subject in subjects_inc:
                all_subjects.add(self.convert_to_query_format(subject))
        if subgroups_inc:
            for subgroup in subgroups_inc:
                all_subgroups.add(self.convert_to_query_format(subgroup))

        return list(all_subjects), list(all_groups), list(all_subgroups)

    @staticmethod
    def generate_offslots_nums(holidays):
        """
        Generate list containing all offslot nums according to the modelling
        """
        holidays.sort()
        nums = []
        for holiday in holidays:
            # Note: a day contains 5 slots
            first_slot_in_holiday = holiday * 5
            last_slot_in_holiday = (holiday * 5) + 4
            nums += [i for i in range(first_slot_in_holiday,
                                      last_slot_in_holiday + 1)]
        return nums
            
    def create_query(self, slots, compensation_slots=None, holidays=[]):
        """
        Create a prolog constraint model query
        """
        
        off_nums = self.generate_offslots_nums(holidays)
        slots_string = "["
        for slot in slots:
            slot_num = slot[0]
            if slot_num in off_nums:
                continue
            slots_string += self.convert_to_query_format(slot)
            slots_string += ","

        if not compensation_slots:
            slots_string = slots_string[:-1] + "]"
            subjects, groups, subgroups = self.listify_on_own(slots)
        else:
            comp_slots_strings, comp_subjects, comp_subgroups = compensation_slots
            for comp_string in comp_slots_strings:
                slots_string += comp_string + ","
            slots_string = slots_string[:-1] + "]"

            subjects, groups, subgroups =\
                self.listify_on_own(slots,
                                    subjects_inc=comp_subjects,
                                    subgroups_inc=comp_subgroups)

        subjects = self.convert_to_query_format(subjects)
        groups = self.convert_to_query_format(groups)
        subgroups = self.convert_to_query_format(subgroups)
        return "schedule(%s,%s,%s,%s,%s)." %\
             (slots_string, str(holidays), subjects, groups, subgroups)

    def turn_to_variable_slot(self, slot, index = 0,
                              time_var=True, location_var=True):
        """
        Takes slot to be compensated; and returns it in the required format
        by the constraint model
        """
        time, subject, slot_type, group, subgroup, location, teacher = slot
        
        if time_var:
            time = "NUM" + str(index)
        if location_var:
            location = "LOCATION" + str(index)
        
        return (time, subject, slot_type,
                group, subgroup, location, teacher)
    
    def get_holiday_to_compensate(self, slots, holidays=[0],
                                  specific_group=None, limit=0,
                                  verbose=False):
        """
        Returns one whole day all-slots to be compensated; useful for debugging
        """

        off_nums = self.generate_offslots_nums(holidays)
        compensations_subjects = set()
        compensations_subgroups = set()
        num_of_compensations = 0
        all_compensation_slots = []
        for slot in slots:
            slot_num, _, _, group, subgroup, _, _ = slot
            if specific_group:
                    if specific_group != group:
                        continue
                    
            if slot_num in off_nums:
                    
                digitized_slot = self.digitize_one_slot(slot)
            
                _, subject, _, _, subgroup, _, _ = digitized_slot
                compensations_subjects.add(subject)
                compensations_subgroups.add(subgroup)

                slot_string =\
                    self.convert_to_query_format(\
                        self.turn_to_variable_slot(digitized_slot,
                                                   index =\
                                                       num_of_compensations))
                
                if verbose:
                    print(str(slot))
                    
                num_of_compensations += 1
                all_compensation_slots.append(slot_string)    
                if limit == num_of_compensations:
                    break
        
        if verbose:
            print("Got " + str(num_of_compensations) + " compensation slots.")
        
        return all_compensation_slots,\
                list(compensations_subjects),\
                list(compensations_subgroups)
                
        
    
    # def get_random_slot_to_compensate(self, slots,
    #                                   # holiday=0,
    #                                   randomized=False, slot_index=0):
    #     """
    #     Returns random or not slot to be compensated; useful for debugging
    #     """
    #     all_compensation_slots = slots
        
    #     if randomized:
    #         from random import random as rand
    #         slot_index = int(rand() * len(all_compensation_slots))

    #     slot = all_compensation_slots[slot_index]
        
    #     holiday = 0
    #     for day_i in range(4, 30, 5):
    #         if slot[0] <= day_i:
    #             break
    #         holiday += 1
            
    #     print("Compensation slot = " + str(slot))
        
    #     digitized_slot =\
    #                 self.digitize_one_slot(slot)
    #     slot_string =\
    #         self.convert_to_query_format(self.turn_to_variable_slot(digitized_slot))

    #     _, subject, _, _, subgroup, _, _ = digitized_slot

    #     return ([slot_string], [subject], [subgroup]), holiday

    def decode_subject(self, encoding):
        """
        Decode subject based on past encoding
        """
        key_list = list(self.subjects_dict.keys())
        val_list = list(self.subjects_dict.values())
        return key_list[val_list.index(encoding)]

    def decode_group(self, encoding):
        """
        Decode group based on past encoding
        """
        key_list = list(self.groups_dict.keys())
        val_list = list(self.groups_dict.values())
        return key_list[val_list.index(encoding)]

    def decode_subgroup(self, encoding):
        """
        Decode group based on past encoding
        """
        key_list = list(self.subgroups_dict.keys())
        val_list = list(self.subgroups_dict.values())
        return key_list[val_list.index(encoding)]
    
    def decode_teacher(self, encoding):
        """
        Decode teacher based on past encoding
        """
        key_list = list(self.teachers_dict.keys())
        val_list = list(self.teachers_dict.values())
        return key_list[val_list.index(encoding)]
    
    def get_all_groups(self, all_slots):
        """
        Listify groups
        """
        all_groups = set()
        for slot in all_slots:
            (slot_num, _, _, group, _, _, _) = slot
            all_groups.add(group)
        all_groups = sorted(all_groups)
        return all_groups
    