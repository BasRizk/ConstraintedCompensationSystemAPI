# -*- coding: utf-8 -*-
"""
This files makes up the main point of the backend of the system

Created on Tue Dec  3 18:02:46 2019

@authors: Basem Rizk, Ibram Medhat, Steven Nassef
"""

from schedule_parser import ScheduleParser
from query_formater import QueryFormater
from pyswip import Prolog

parser = ScheduleParser()
days_schedules, sheet_names, headers = parser.parse_schedule()
all_slots = parser.listify_slots(days_schedules)
query_formater = QueryFormater()
all_slots = query_formater.clean_formatted_slots(all_slots)
all_slots = query_formater.digitize(all_slots)
compensation_slot = query_formater.get_random_slot_to_compensate(all_slots, randomized = False)
print("Compensation slot = " + str(compensation_slot))
query_statement = query_formater.create_query(all_slots, compensation_slot)

prolog = Prolog()
prolog.consult("constraint_based_approach.pl")
for soln in prolog.query(query_statement):
    print(soln)
    
    
#   

#with open("query_example.txt", "w") as f:
#    query_rest = query_statement
#    while(True):
#        limit = 1000
#        if len(query_rest) < limit:
#            break
#        f.write(query_rest[:limit])
#        f.write("\n")
#        query_rest = query_rest[limit:]
#    f.write(query_rest)