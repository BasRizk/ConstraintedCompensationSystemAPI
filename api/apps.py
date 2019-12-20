import sys
from django.apps import AppConfig

class ApiConfig(AppConfig):
    name = 'api'

    # def ready(self):
    #     if 'runserver' not in sys.argv:
    #         return True

# def load_schedule():
#     import numpy as np
#     def print_progress(iteration_type, iteration_value, end_value=0, upper_bound_exist=False):
#         if(upper_bound_exist):
#             iteration_value = np.around((iteration_value/end_value)*100,
#                                         decimals = 1)
#         print( '\r ' + iteration_type + ' %s' % (str(iteration_value)),
#                 end = '\r')

#     from .models import Slot
#     from .constraint_model_engine import ConstraintModelEngine

#     # Save the object into the database.
#     schedule_solver = ConstraintModelEngine()
#     schedule_solver.connect_schedule()
#     slot_counter = 0
#     num_of_slots = len(schedule_solver.all_slots)
#     for slot in schedule_solver.all_slots:
#         slot_counter += 1
        
#         print_progress("Saving To DB: ", slot_counter,\
#                         end_value=num_of_slots, upper_bound_exist=True)

#         slot_num, slot_subject, slot_type,\
#         slot_group, slot_subgroup, slot_location = slot
#         slot_record = Slot(slot_num=slot_num,\
#                         slot_subject=slot_subject,\
#                         slot_type=slot_type,\
#                         slot_group=slot_group,\
#                         slot_subgroup=slot_subgroup,\
#                         slot_location=slot_location)
#         slot_record.save()
#     print()
#     print("DATABASE INTIALIZED")
