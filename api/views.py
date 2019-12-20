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


class CompensateSlot(APIView):
    """
    Retrieve, update or delete a slot instance.
    """
    # self.all_slots = self.get_all_objects()
    schedule_solver = ConstraintModelEngine.get_instance()

    def get_object(self, slot_id):
        try:
            return tuple(Slot.objects\
                .values_list('slot_num',\
                    'slot_subject',\
                    'slot_type', 'slot_group',\
                    'slot_subgroup', 'slot_location')\
                        .get(pk=slot_id))
        except Slot.DoesNotExist:
            raise Http404

    def get_all_objects(self):
        return tuple(Slot.objects.all()\
            .order_by('slot_num')\
            .values_list('slot_num',\
                'slot_subject',\
                'slot_type', 'slot_group',\
                'slot_subgroup', 'slot_location'))

    def get(self, request, slot_id=None):
        """
        Get possible compensations of this slot
        """
        to_compensate_slot = self.get_object(slot_id=slot_id)

        if to_compensate_slot:
            all_slots = self.get_all_objects()
            self.schedule_solver.connect_schedule(all_slots)
            possiblities = self.schedule_solver.query_model(to_compensate_slot)
            return Response(possiblities, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk, format=None):
    #     slot = self.get_object(pk)
    #     slot.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)