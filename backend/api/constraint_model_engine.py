"""Constraint Model Engine"""
from pyswip import Prolog
from .ConstraintModel.schedule_parser import ScheduleParser
from .ConstraintModel.query_formater import QueryFormater


class ConstraintModelEngine:
    """
    Contains high level logic of preparing and quering the Prolog constraint model
    """
    def __init__(self):
        PL_FILENAME = "api/ConstraintModel/constraint_based_approach.pl"
        self.parser = ScheduleParser()
        self.query_formater = QueryFormater()
        self.prolog = Prolog()
        # self.prolog.consult(PL_FILENAME)
        self.days_schedules = None
        self.all_slots = None

    def connect_schedule(self):
        """
        Reads the static schedule saved in the system
        """
        self.days_schedules, sheet_names, headers = self.parser.parse_schedule(
        )
        self.all_slots = self.parser.listify_slots(self.days_schedules)

    def query_model(self, compensation_slot):
        """
        Creates a query to the constraint model
        """
        slots_cleaned = self.query_formater.clean_formatted_slots(
            self.all_slots)
        slots_digitized = self.query_formater.digitize(slots_cleaned)
        # compensation_slot = self.query_formater.get_random_slot_to_compensate(all_slots, randomized=False)
        # print("Compensation slot = " + str(compensation_slot))
        ready_compensation_slot, holiday = self.ready_compensation(
            compensation_slot)
        query_statement = self.query_formater.create_query(
            slots_digitized, holiday, ready_compensation_slot)
        return self.prolog.query(query_statement)

    def ready_compensation(self, compensation_slot):
        """
        Ensure validity of a slot and make it ready for query
        """
        if compensation_slot in self.all_slots:
            return self.query_formater.turn_to_variable_slot(compensation_slot)
        else:
            return "Error"

    def decode_slot(self, slot):
        """
        Decodes an encoded (digitized) slot
        - a slot that has been queried 
        """
        num, subject, slot_type, subgroup, group, location = slot
        subject = self.query_formater.decode_subject(subject)
        group = self.query_formater.decode_group(group)
        subgroup = self.query_formater.decode_subgroup(subgroup)
        return num, subject, slot_type, group, subgroup, location

    def get_all_groups(self):
        """
        Lists the set of all study groups
        """
        _, groups, _ =\
            self.query_formater.listify_on_own(self.all_slots,
                                               subjects=False,
                                               subgroups=False)
        return sorted(groups)

    def get_group_slots(self, target_group):
        """
        Lists all slots of specific group
        """
        group_slots = []
        for slot in self.all_slots:
            _, _, _, group, _, _ = slot
            if group == target_group:
                group_slots.append(slot)
        return group_slots