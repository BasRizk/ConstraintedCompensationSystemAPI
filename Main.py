# -*- coding: utf-8 -*-
"""
This files makes up the main point of the backend of the system

Created on Tue Dec  3 18:02:46 2019

@authors: Basem Rizk, Ibram Medhat, Steven Nassef
"""

from schedule_parser import Schedule_Parser
from query_creator import clean_formatted_slots, digitize
from query_creator import get_random_slot_to_compensate, create_query

parser = Schedule_Parser()
days_schedules, sheet_names, headers = parser.parse_schedule()
all_slots = parser.listify_slots(days_schedules)
all_slots = clean_formatted_slots(all_slots)
all_slots = digitize(all_slots)
compensation_slot = get_random_slot_to_compensate(all_slots)
query_statement = create_query(all_slots, compensation_slot)

from pyswip import Prolog
prolog = Prolog()
prolog.consult("constraint_based_approach.pl")
for soln in prolog.query(query_statement):
    print(soln)
#