"""
API Views - Http Responses Handlers
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .constraint_model_engine import ConstraintModelEngine
from .models import Slot
from .serializers import SlotSerializer
from django.core.paginator import Paginator


class AllSlots(APIView):
    """
    List all slots
    """

    def get(self, request, group_name=None, week=None, format=None):
        """
        Respond with all existing slots or group-specific
        """
        if group_name:
            slots = Slot.objects.filter(slot_group=group_name, slot_week=week)\
                .order_by('slot_num')
            serializer = SlotSerializer(slots, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
        # slots = Slot.objects.all()
        # serializer = SlotSerializer(slots, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)


class AllGroups(APIView):
    """
    List all groups
    """

    def get(self, request, format=None):
        """
        Respond with all existing slots
        """
        groups = Slot.objects.order_by('slot_group').values_list(
            'slot_group', flat=True).distinct()

        # TODO maybe make it more dynamic from the db!
        schedule_solver = ConstraintModelEngine.get_instance()
        schedule_solver.sample_weekson_dict(all_groups=groups)
        back_response = {
            "groups": groups,
            "weekson_dict": schedule_solver.weekson_dict
        }
        return Response(back_response, status=status.HTTP_200_OK)



def get_slotWeek(slot_id):
        try:
            return Slot.objects.values_list('slot_week').get(pk=slot_id)[0]
        except Slot.DoesNotExist:
            raise Http404
        
def get_object(slot_id):
        try:
            return tuple(Slot.objects
                         .values_list('slot_num',
                                      'slot_subject',
                                      'slot_type', 'slot_group',
                                      'slot_subgroup', 'slot_location',
                                      'slot_teacher')
                         .get(pk=slot_id))
        except Slot.DoesNotExist:
            raise Http404

def get_all_objects(week):
    return tuple(Slot.objects.filter(slot_week=week)
                    .order_by('slot_num')
                    .values_list('slot_num',
                                'slot_subject',
                                'slot_type', 'slot_group',
                                'slot_subgroup', 'slot_location',
                                'slot_teacher'))

class CompensateSlot(APIView):
    """
    Ask for a compensation of one or more slots instances.
    """

    @staticmethod
    def get_to_compensate_slots_tuples(ids_to_compensate,
                                       prefered_slot_num=None):
        to_compensate_slots = []
        for slot_id in ids_to_compensate:
            slot_tuple = get_object(slot_id=slot_id)
            if(slot_tuple):

                slot_tuple = (slot_id,) + slot_tuple
                if prefered_slot_num is not None:
                    _id, _, subject, _type, group,\
                    subgroup, location, teacher =\
                         slot_tuple
                    slot_tuple = (_id, prefered_slot_num, subject,
                                 _type, group, subgroup,
                                 location, teacher)
                to_compensate_slots.append(slot_tuple)
        return to_compensate_slots

    def serve_preference_request(self, request):
        id_to_compensate = request.data.get("id")
        back_response = {"msg": ""}
        if id_to_compensate is not None:
            limit = request.data.get('limit')
            if limit is None:
                limit = 2
            prefered_slot_num = request.data.get("prefered_slot_num")
            if prefered_slot_num is not None:
                to_compensate_slots =\
                        self.get_to_compensate_slots_tuples([id_to_compensate],
                                                prefered_slot_num=prefered_slot_num)
                if to_compensate_slots and len(to_compensate_slots) > 0:
                    schedule_solver = ConstraintModelEngine.get_instance()
                    all_slots = get_all_objects(get_slotWeek(id_to_compensate))
                    schedule_solver.connect_schedule(all_slots)

                    possiblities =\
                        schedule_solver.query_model(to_compensate_slots,
                                                    answers_limit=limit,
                                                    time_preference=True)
                    return Response(possiblities, status=status.HTTP_200_OK)
                back_response = {"msg": "id does not exist"}
            else:
                back_response = {"msg": "No prefered_slot_num sent!"}
        return Response(back_response, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        back_response = {"msg": ""}
        if request.method == 'POST':
            if request.data.get('preference'):
                return self.serve_preference_request(request)

            ids_to_compensate = request.data.get('id')
            if ids_to_compensate is not None:

                limit = request.data.get('limit')
                if not limit:
                    limit = 2

                to_compensate_slots =\
                     self.get_to_compensate_slots_tuples(ids_to_compensate)

                if to_compensate_slots and len(to_compensate_slots) > 0:
                    one_of_the_ids = ids_to_compensate[0]
                    schedule_solver = ConstraintModelEngine.get_instance()
                    all_slots = get_all_objects(get_slotWeek(one_of_the_ids))
                    schedule_solver.connect_schedule(all_slots)
                    extra_holidays = request.data.get('extra_holidays')
                    # if not extra_holidays:
                    #     extra_holidays = None
                    possiblities =\
                        schedule_solver.query_model(to_compensate_slots,
                                                    answers_limit=limit,
                                                    extra_holidays=extra_holidays)
                    if possiblities is not None:
                        return Response(possiblities, status=status.HTTP_200_OK)
                    back_response = {"msg": "System is locked at the point!"}
                else:
                    back_response = {"msg": "ids in list of (id) does not exist"}
            else:
                back_response = {"msg": "list of (id) needed"}
        else:
            back_response = {"msg": "only support POST methods"}
        return Response(back_response, status=status.HTTP_400_BAD_REQUEST)

class ConfirmCompensation(APIView):
    """
    Confirm compensation possibilities and save into DB
    """
    def post(self, request):
        back_response = {"msg": ""}
        if request.method == 'POST':
            # print(request.data)
            ids = request.data.get('id')
            compensations_possibility = request.data.get('compensations_possibility')
            not_updated_ids, updated_ids = self.save_compensations(ids, compensations_possibility)
            back_response = {
                "not_updated": not_updated_ids,
                "updated_ids": updated_ids
            }
            return Response(back_response, status=status.HTTP_200_OK)
        back_response = {"msg": "only support POST methods"}
        return Response(back_response, status=status.HTTP_400_BAD_REQUEST)

    def save_compensations(self, ids, compensations_possibility):
        not_updated = set()
        updated = []
        # Updated is a list to expose any error!
        for _id in ids:
            num_key = "NUM" + str(_id)
            location_key = "LOCATION" + str(_id)
            new_num = compensations_possibility.get(num_key)
            new_location = compensations_possibility.get(location_key)
            
            slot_obj = Slot.objects.get(pk=_id)
            if slot_obj is not None and (new_num or new_location):
                if new_num:
                    slot_obj.slot_num = new_num
                if new_location:
                    slot_obj.slot_location = new_location
                slot_obj.save()
                updated.append(_id)
            else:
                # Maybe return not updated to notify users, regarding the warning!
                not_updated.add(_id)
            return list(not_updated), updated
