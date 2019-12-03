# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 18:02:46 2019

@author: Basem Rizk
"""

from schedule_parser import parse_schedule, listify_slots
from query_creator import clean_formatted_slots, digitize
from query_creator import get_random_slot_to_compensate, create_query

days_schedules, sheet_names, headers = parse_schedule()
all_slots = listify_slots(days_schedules)
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