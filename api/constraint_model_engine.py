"""Constraint Model Engine"""
# from pyswip import Prolog
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
    _query_lock = False
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
            self.weekson_dict = None
            ConstraintModelEngine.__instance = self

    def connect_schedule(self, all_slots):
        self.all_slots = all_slots
        self.sample_weekson_dict(all_slots)

    def query_model(self, compensation_slots, answers_limit=0):
        """
        Creates a query to the constraint model
        """
        while self._query_lock:
            pass
        self._query_lock = True

        slots_digitized = self.query_formater.digitize(self.all_slots)

        variable_slots, compensation_ids, holidays =\
             self.ready_compensation(compensation_slots)
        # print(variable_slots)
        # print(compensation_ids)
        # print(holiday)
        # if not variable_slots:
        #     return {"msg": "Not implemented yet to compensate on" +
        #                     "different days at the same time"}

        query_statement = self.query_formater.create_query(
            slots_digitized, variable_slots, holidays=holidays)
    
        # print(query_statement)

        answers = []
        for option in self.prolog.query(query_statement):
            # print("RESULT: " + str(option))
            one_answer = {}
            for _id in compensation_ids:
                num_var = "NUM" + str(_id)
                location_var = "LOCATION" + str(_id)
                one_answer[num_var] = str(option[num_var])
                one_answer[location_var] = str(option[location_var])
            answers.append(one_answer)
            
            answers_limit -= 1
            if answers_limit == 0:
                break
        
        self._query_lock = False
        # print(answers)
        return answers
    
    def ready_compensation(self, compensation_slots):
        """
        Ensure validity of a slot and make it ready for query
        """

        slot_strings = []
        ids = []

        subjects = set()
        subgroups = set()
        holidays = set()
        # print(compensation_slot)
        for compensation_slot in compensation_slots:
            
            _id, num, subject, _type, subgroup, group, location, teacher = compensation_slot
            compensation_slot = (num, subject, _type, subgroup, group, location, teacher)

            holiday = 0
            for day_i in range(4, 29, 5):
                if compensation_slot[0] <= day_i:
                    break
                holiday += 1
            holidays.add(holiday)

            digitized_slot =\
                self.query_formater.digitize_one_slot(compensation_slot)
            variable_slot =\
                self.query_formater.turn_to_variable_slot(digitized_slot, index=_id)
            slot_string =\
                self.query_formater.convert_to_query_format(variable_slot)
            _, subject, _, _, subgroup, _, _ = digitized_slot
            
            slot_strings.append(slot_string)
            ids.append(_id)
            subjects.add(subject)
            subgroups.add(subgroup)

        # holidays = list(holidays)
        # # print(holidays)
        # if len(holidays) != 1:
        #     print("Not implemented yet compensation on more than one day!")
        #     return None, None, -1

        return (slot_strings, list(subjects), list(subgroups)), ids, list(holidays)

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

    def sample_weekson_dict(self, all_slots):
        all_groups = self.query_formater.get_all_groups(all_slots)
        self.weekson_dict = {}
        for group in list(all_groups):
            if "1engineering" in group:
                self.weekson_dict[group] = [0] + [i for i in range(3, 15)]
            else:
                self.weekson_dict[group] = [0] + [i for i in range(1, 13)]
