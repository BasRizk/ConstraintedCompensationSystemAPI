"""
API Views - Http Responses Handlers
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .constraint_model_engine import ConstraintModelEngine
from .models import Slot
from .models import CompensatedSlot
from .serializers import SlotSerializer
from .serializers import CompensationSlotSerializer
from django.core.paginator import Paginator
from itertools import chain


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

class AllSlots_Weeks(APIView):
    """
    List all slots
    """

    def get(self, request, group_name=None, week=None, format=None):
        """
        Respond with all existing slots or group-specific
        """
        if group_name:
            if week > 0:
                compensatedSlots = CompensatedSlot.objects.filter(
                    slot_week = week
                )

                compensatedSlots_ids = compensatedSlots.values_list('slot_id')

                print(compensatedSlots_ids)
                compensatedSlots = compensatedSlots.defer("slot_week")
                print(compensatedSlots)
                

                slots = Slot.objects.exclude(id__in = compensatedSlots_ids)

                print(slots)

                slots = chain(slots , compensatedSlots)

                 
            else:
                slots = Slot.objects.filter(slot_group=group_name)\
                    .order_by('slot_num')

            print(slots)
            # serializer = SlotSerializer(slots, many=True)
            return Response(slots, status=status.HTTP_200_OK)
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


class CompensateSlot(APIView):
    """
    Retrieve, update or delete a slot instance.
    """

    def get_object(self, slot_id):
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

    def get_all_objects(self):
        return tuple(Slot.objects.all()
                     .order_by('slot_num')
                     .values_list('slot_num',
                                  'slot_subject',
                                  'slot_type', 'slot_group',
                                  'slot_subgroup', 'slot_location',
                                  'slot_teacher'))

    def post(self, request):
        if request.method == 'POST':
            ids_to_compensate = request.data.get('id')
            if ids_to_compensate:

                limit = request.data.get('limit')
                if not limit:
                    limit = 2

                to_compensate_slots = []
                for slot_id in ids_to_compensate:
                    slot = self.get_object(slot_id=slot_id)
                    if(slot):
                        slot_tuple = self.get_object(slot_id=slot_id)
                        slot_tuple = (slot_id,) + slot_tuple
                        to_compensate_slots.append(slot_tuple)

                if to_compensate_slots:
                    schedule_solver = ConstraintModelEngine.get_instance()
                    all_slots = self.get_all_objects()
                    schedule_solver.connect_schedule(all_slots)
                    possiblities =\
                        schedule_solver.query_model(to_compensate_slots,
                                                    answers_limit=limit)
                    return Response(possiblities, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk, format=None):
    #     slot = self.get_object(pk)
    #     slot.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
class CompensateSlotWithWeek(APIView):
    """
    Retrieve, update or delete a slot instance.
    """

    def get_object(self, slot_id):
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

    def get_all_objects(self, week):
        compensatedSlots = CompensatedSlot.objects.filter(
            slot_week = week
        )

        compensatedSlots_ids = compensatedSlots.values_list('slot_id')

        compensatedSlots = compensatedSlots.values_list('slot_num',
                                  'slot_subject',
                                  'slot_type', 'slot_group',
                                  'slot_subgroup', 'slot_location',
                                  'slot_teacher')

        

        slots = Slot.objects.exclude(id__in = compensatedSlots_ids).values_list('slot_num',
                                  'slot_subject',
                                  'slot_type', 'slot_group',
                                  'slot_subgroup', 'slot_location',
                                  'slot_teacher')

        slots = chain(slots , compensatedSlots)
        
        return tuple(slots)

    def post(self, request):
        if request.method == 'POST':
            ids_to_compensate = request.data.get('id')
            if ids_to_compensate:

                limit = request.data.get('limit')
                if not limit:
                    limit = 2

                to_compensate_slots = []
                for slot_id in ids_to_compensate:
                    slot = self.get_object(slot_id=slot_id)
                    if(slot):
                        slot_tuple = self.get_object(slot_id=slot_id)
                        slot_tuple = (slot_id,) + slot_tuple
                        to_compensate_slots.append(slot_tuple)

                if to_compensate_slots:
                    schedule_solver = ConstraintModelEngine.get_instance()
                    all_slots = self.get_all_objects()
                    schedule_solver.connect_schedule(all_slots)
                    possiblities =\
                        schedule_solver.query_model(to_compensate_slots,
                                                    answers_limit=limit)
                    return Response(possiblities, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk, format=None):
    #     slot = self.get_object(pk)
    #     slot.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
