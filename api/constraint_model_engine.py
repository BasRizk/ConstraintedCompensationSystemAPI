"""Constraint Model Engine"""
from pyswip import Prolog
# from .ConstraintModel.schedule_parser import ScheduleParser
from .ConstraintModel.query_formater import QueryFormater
# import os
from .ConstraintModel.prolog_mt import PrologMT


class ConstraintModelEngine:
    """
    Contains high level logic of preparing and quering the Prolog constraint model
    """
    PL_FILENAME = "api\\\\ConstraintModel\\\\constraint_based_approach.pl"

    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if ConstraintModelEngine.__instance is None:
            ConstraintModelEngine()
        return ConstraintModelEngine.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if ConstraintModelEngine.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.query_formater = QueryFormater()
            self.prolog = PrologMT()
            # print('PROLOG INTIALIZED')
            # if os.path.exists(self.PL_FILENAME):
            #     print("AWESOME")
            self.prolog.consult(self.PL_FILENAME)
            # print('PROLOG CONSULTED')
            self.all_slots = None
            ConstraintModelEngine.__instance = self

    def connect_schedule(self, all_slots):
        # self.days_schedules = None
        self.all_slots = all_slots

    # def connect_schedule(self):
    #     """
    #     Reads the static schedule saved in the system
    #     """
    #     self.days_schedules, sheet_names, headers = self.parser.parse_schedule(
    #     )
    #     self.all_slots = self.parser.listify_slots(self.days_schedules)
    #     self.all_slots = self.query_formater.clean_formatted_slots(
    #         self.all_slots)

    def query_model(self, compensation_slot):
        """
        Creates a query to the constraint model
        """
        slots_digitized = self.query_formater.digitize(self.all_slots)
        var_compensation_slot, holiday = self.ready_compensation(
            compensation_slot)
        query_statement = self.query_formater.create_query(
            slots_digitized, var_compensation_slot, holiday=holiday)
        # print(query_statement)
        answers = {}
        answer_id = 0
        for option in self.prolog.query(query_statement):
            answer_id += 1
            answers[answer_id] = {
                "NUM": str(option["NUM"]),
                "LOCATION": str(option["LOCATION"])
            }
        print(answers)
        return answers

    def ready_compensation(self, compensation_slot):
        """
        Ensure validity of a slot and make it ready for query
        """
        # print(compensation_slot)
        if compensation_slot in self.all_slots:
            holiday = 0
            for day_i in range(4, 30, 5):
                if slot[0] <= day_i:
                    break
                holiday += 1

            digitized_slot =\
                self.query_formater.digitize_one_slot(compensation_slot)
            variable_slot =\
                self.query_formater.turn_to_variable_slot(digitized_slot)
            slot_string =\
                self.query_formater.convert_to_query_format(variable_slot)
            _, subject, _, _, subgroup, _, _ = digitized_slot

            return (slot_string, subject, subgroup), holiday

    def decode_slot(self, slot):
        """
        Decodes an encoded (digitized) slot
        - a slot that has been queried
        """
        num, subject, slot_type, subgroup, group, location, teacher = slot
        subject = self.query_formater.decode_subject(subject)
        group = self.query_formater.decode_group(group)
        subgroup = self.query_formater.decode_subgroup(subgroup)
        return num, subject, slot_type, group, subgroup, location, teacher

    # def get_all_groups(self):
    #     """
    #     Lists the set of all study groups
    #     """
    #     _, groups, _ =\
    #         self.query_formater.listify_on_own(self.all_slots,
    #                                            subjects=False,
    #                                            subgroups=False)
    #     return sorted(groups)

    # def get_group_slots(self, target_group, json_format=False):
    #     """
    #     Lists all slots of specific group
    #     """

    #     # import json

    #     target_group = target_group.replace("_", " ").lower()
    #     group_slots = []
    #     for slot in self.all_slots:
    #         num, subject, slot_type, group, subgroup, location = slot
    #         if group.lower() == target_group:
    #             if json_format:
    #                 slot = {
    #                     "slot_num": str(num),
    #                     "slot_subject": str(subject),
    #                     "slot_type": str(slot_type),
    #                     "slot_group": str(group),
    #                     "slot_subgroup": str(subgroup),
    #                     "slot_location": str(location)
    #                 }
    #                 group_slots.append(slot)
    #             else:
    #                 group_slots.append(slot)

    #     if json_format:
    #         group_slots = json.dumps(group_slots)

    #     return group_slots