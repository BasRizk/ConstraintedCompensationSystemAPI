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
        self.sample_weekson_dict()

    def query_model(self, compensation_slots, answers_limit=0,
                    extra_holidays=None,
                    time_preference=False, location_preference=False):
        """
        Creates a query to the constraint model
        """
        # TODO maybe return msg lock if query_lock instead of waiting
        while self._query_lock:
            pass
        self._query_lock = True

        slots_digitized = self.query_formater.digitize(self.all_slots)

        variable_slots, compensation_ids, holidays =\
             self.ready_compensation(compensation_slots,
                                     time_preference=time_preference,
                                     location_preference=location_preference)

        if extra_holidays:
            holidays = list(set(extra_holidays).union(set(holidays)))

        query_statement = self.query_formater.create_query(
            slots_digitized, variable_slots, holidays=holidays)
        
        # with open("query_example.txt", "w") as f:
        #     query_rest = query_statement
        #     while(True):
        #         limit = 1000
        #         if len(query_rest) < limit:
        #             break
        #         f.write(query_rest[:limit])
        #         f.write("\n")
        #         query_rest = query_rest[limit:]
        #     f.write(query_rest)

        answers = []
        # print("About to query")
        # print(variable_slots)
        for option in self.prolog.query(query_statement):
            print(option)
            one_answer = {}
            for _id in compensation_ids:
                num_var = "NUM" + str(_id)
                location_var = "LOCATION" + str(_id)
                num_val = option.get(num_var)
                location_val = option.get(location_var)
                if num_val is not None:
                    one_answer[num_var] = str(num_val)
                if location_val is not None:
                    one_answer[location_var] = str(location_val)
            if len(one_answer) > 0:
                answers.append(one_answer)
            
            answers_limit -= 1
            if answers_limit == 0:
                break
        
        self._query_lock = False

        return answers
    
    def ready_compensation(self, compensation_slots,
                            time_preference=False,
                            location_preference=False):
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
            print(compensation_slot)
            holiday = 0
            for day_i in range(4, 29, 5):
                if compensation_slot[0] <= day_i:
                    break
                holiday += 1
            holidays.add(holiday)

            digitized_slot =\
                self.query_formater.digitize_one_slot(compensation_slot)
            variable_slot =\
                self.query_formater.turn_to_variable_slot(digitized_slot, index=_id,
                                                        time_var=not(time_preference),
                                                        location_var=not(location_preference))
            slot_string =\
                self.query_formater.convert_to_query_format(variable_slot)
            _, subject, _, _, subgroup, _, _ = digitized_slot
            
            slot_strings.append(slot_string)
            ids.append(_id)
            subjects.add(subject)
            subgroups.add(subgroup)
        
        if location_preference or time_preference:
            holidays = [-1]
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

    def sample_weekson_dict(self, all_groups=None):
        """
        Generate list of the default weekon days of each group
        """
        if not all_groups:
            if not self.all_slots:
                print("WARNING:: connect_schedule first.")
                return
            all_groups = self.query_formater.get_all_groups(self.all_slots)
        self.weekson_dict = {}
        for group in list(all_groups):
            if "1engineering" in group:
                self.weekson_dict[group] = [0] + [i for i in range(3, 15)]
            else:
                self.weekson_dict[group] = [0] + [i for i in range(1, 13)]