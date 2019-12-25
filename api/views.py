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

    def get(self, request, group_name=None, format=None):
        """
        Respond with all existing slots or group-specific
        """
        if group_name:
            slots = Slot.objects.filter(slot_group=group_name)\
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
        return Response({"groups": groups}, status=status.HTTP_200_OK)


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

def get_all_objects():
    return tuple(Slot.objects.all()
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
    def post(self, request):
        if request.method == 'POST':

            ids_to_compensate = request.data.get('id')
            if ids_to_compensate:

                limit = request.data.get('limit')
                if not limit:
                    limit = 2

                to_compensate_slots = []
                for slot_id in ids_to_compensate:
                    slot = get_object(slot_id=slot_id)
                    if(slot):
                        slot_tuple = get_object(slot_id=slot_id)
                        slot_tuple = (slot_id,) + slot_tuple
                        to_compensate_slots.append(slot_tuple)

                if to_compensate_slots:
                    schedule_solver = ConstraintModelEngine.get_instance()
                    all_slots = get_all_objects()
                    schedule_solver.connect_schedule(all_slots)
                    extra_holidays = request.data.get('extra_holidays')
                    # if not extra_holidays:
                    #     extra_holidays = None
                    possiblities =\
                        schedule_solver.query_model(to_compensate_slots,
                                                    answers_limit=limit,
                                                    extra_holidays=extra_holidays)
                    return Response(possiblities, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk, format=None):
    #     slot = self.get_object(pk)
    #     slot.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class ConfirmCompensation(APIView):
    """
    Confirm compensation possibilities and save into DB
    """
    def save_compensations(self, ids, compensations_possibility, week):
        not_updated = set()
        for _id in ids:
            num_key = "NUM" + str(_id)
            location_key = "LOCATION" + str(_id)
            new_num = compensations_possibility.get(num_key)
            new_location = compensations_possibility.get(location_key)

            if new_num and new_location:
                # TODO update using both values, _id, and the week
                pass
            elif new_num:
                # TODO update one only
                pass
            elif new_location:
                # TODO update one only (dumb but it is fine)
                pass
            else:
                not_updated.add(_id)
        # Maybe return not updated to notify users, regarding the warning!