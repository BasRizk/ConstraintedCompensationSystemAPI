# -*- coding: utf-8 -*-
"""
This files makes up the main point of the backend of the system

Created on Tue Dec  3 18:02:46 2019

@authors: Basem Rizk, Ibram Medhat, Steven Nassef
"""

# from schedule_parser import ScheduleParser
from schedule_parser_with_teachers import ScheduleParserWithTeachers
from query_formater import QueryFormater
from pyswip import Prolog

parser = ScheduleParserWithTeachers(filename="MET_Winter19_schedule_31131.xlsx",
                                    teachers_filename="modifiedSchedule2.xlsx")
days_schedules, sheet_names, headers = parser.parse_schedule()
teachers_schedules = parser.parse_teachers_schedules()
all_slots = parser.listify_slots()
query_formater = QueryFormater()
all_slots = query_formater.clean_formatted_slots(all_slots)
all_slots = query_formater.digitize(all_slots)
compensation_slot = query_formater.get_random_slot_to_compensate(all_slots, randomized = True)
print("Compensation slot = " + str(compensation_slot))
query_statement = query_formater.create_query(all_slots, compensation_slot)

prolog = Prolog()
prolog.consult("constraint_based_approach.pl")
for soln in prolog.query(query_statement):
    print(soln)
    


def to_json_fixture(all_slots, model_name = "api.slot"):
    import json
    slot_counter = 0
    all_slots_records = []
    for slot in all_slots:
        slot_counter += 1
        slot_num, slot_subject, slot_type,\
        slot_group, slot_subgroup, slot_location = slot
         
        slot_record = {}
        slot_record["slot_num"] = slot_num
        slot_record["slot_subject"] = slot_subject
        slot_record["slot_type"] = slot_type
        slot_record["slot_group"] = slot_group
        slot_record["slot_subgroup"] = slot_subgroup
        slot_record["slot_location"] = slot_location
#        slot_record = json.dumps(slot_record)
        print(slot_record)
        
        db_record = {}
        db_record["model"] = model_name
        db_record["pk"] = slot_counter
        db_record["fields"] = slot_record
#        db_record = json.dumps(db_record)
        all_slots_records.append(db_record)
        print(db_record)
        
    all_slots_records = json.dumps(all_slots_records)
    with open("schedule_slots_fixture.json", "w") as f:
        f.write(all_slots_records)
    

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