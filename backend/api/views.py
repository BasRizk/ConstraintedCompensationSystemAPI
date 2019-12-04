""" To turn list outputs to json for response"""
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from django.http import Http404
from .constraint_model_engine import ConstraintModelEngine
from .models import Slot
from .serializers import SlotSerializer

class AllSlots(APIView):
    """
    List all slots
    """
    def get(self, request, format=None):
        """
        Respond with all existing slots
        """
        slots = Slot.objects.all()    
        serializer = SlotSerializer(slots, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        print("here is the request")
        if request.body and request.body["group"]:
            schedule_solver = ConstraintModelEngine()
            schedule_solver.connect_schedule()
            group_slots = schedule_solver.get_group_slots(request.body["group"]) 
            print("There is request body group parameter!")
            # TODO let serializer take care of this somehow!
            serializer = SlotSerializer(group_slots, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class AllGroups(APIView):
    """
    List all groups
    """
    def get(self, request, format=None):
        """
        Respond with all existing slots
        """
        schedule_solver = ConstraintModelEngine()
        schedule_solver.connect_schedule()
        all_groups = schedule_solver.get_all_groups()
        all_groups_json = json.dumps(all_groups)
        # serializer = SlotSerializer(slots, many=True)
        return Response(all_groups_json)


class CompensateSlot(APIView):
    """
    Retrieve, update or delete a slot instance.
    """
    # def get_object(self, pk):
    #     try:
    #         return Slot.objects.get(pk=pk)
    #     except Slot.DoesNotExist:
    #         raise Http404

    def convert_slot_from_json(self, slot_json):
        """
        Turn a slot json format to format that is used by ConstraintEngine
        """
        num = slot_json["slot_num"]
        subject = slot_json["slot_name"]
        slot_type = slot_json["slot_type"]
        group = slot_json["slot_group"]
        subgroup = slot_json["slot_subgroup"]
        location = slot_json["slot_location"]
        slot_tuple = (num, subject, slot_type, group, subgroup, location)
        return slot_tuple

    def post(self, request):
        """
        Post Body containing slot to compensate
        """
        to_compensate_slot = request.body
        serializer = SlotSerializer(to_compensate_slot, data=request.data)
        if serializer.is_valid():
            schedule_solver = ConstraintModelEngine()
            schedule_solver.connect_schedule()
            to_compensate_slot = self.convert_slot_from_json(to_compensate_slot)
            compensation = schedule_solver.query_model(to_compensate_slot)
            # serializer = SlotSerializer(compensation)
            return Response(compensation)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk, format=None):
    #     slot = self.get_object(pk)
    #     slot.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)