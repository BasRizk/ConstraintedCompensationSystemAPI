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

    def query_model(self, compensation_slots):
        """
        Creates a query to the constraint model
        """
        def ids_aside(compensation_slots):
            """
            Split tuples coming from DB and put aside the ids
            """
            slots = []
            ids = []
            for slot in compensation_slots:
                _id, num, subject, _type, subgroup, group, location = slot
                slots.append((num, subject, _type, subgroup, group, location))
                ids.append(_id)
            return slots, ids
            
        slots_digitized = self.query_formater.digitize(self.all_slots)

        compensation_slots_no_ids, compensation_ids = ids_aside(compensation_slots)
        variable_slots, holiday = self.ready_compensation(
            compensation_slots_no_ids)

        if not variable_slots:
            return {"msg": "Not implemented yet to compensate on\
                            different days at the same time"}

        query_statement = self.query_formater.create_query(
            slots_digitized, variable_slots, holiday=holiday)
        # print(query_statement)
        answers = []
        for option in self.prolog.query(query_statement):
            one_answer = {}
            for _id in compensation_ids:
                num_var = "NUM" + str(_id)
                location_var = "LOCATION" + str(_id)
                one_answer[num_var] = str(option[num_var])
                one_answer[location_var] = str(option[location_var])
            answers.append(one_answer)

        # print(answers)
        return answers
    
    def ready_compensation(self, compensation_slots):
        """
        Ensure validity of a slot and make it ready for query
        """
        slot_strings = []
        subjects = set()
        subgroups = set()
        holidays = set()
        # print(compensation_slot)
        for compensation_slot in compensation_slots:
            # if compensation_slot in self.all_slots:
            holiday = 0
            for day_i in range(4, 30, 5):
                if compensation_slot[0] <= day_i:
                    break
                holiday += 1
            holidays.add(holiday)

            digitized_slot =\
                self.query_formater.digitize_one_slot(compensation_slot)
            variable_slot =\
                self.query_formater.turn_to_variable_slot(digitized_slot)
            slot_string =\
                self.query_formater.convert_to_query_format(variable_slot)
            _, subject, _, _, subgroup, _, _ = digitized_slot
            slot_strings.append(slot_string)
            subjects.add(subject)
            subgroups.add(subgroup)
            # else:
            #     print("Slot: " + str(compensation_slot) + " does not exist")
        holidays = list(holidays)
        if len(holidays) != 1:
            print("Not implemented yet compensation on more than one day!")
            return None, -1

        return (slot_strings, list(subjects), list(subgroups)), holiday

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
