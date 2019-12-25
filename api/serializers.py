from rest_framework import serializers
from .models import Slot


class SlotSerializer(serializers.HyperlinkedModelSerializer):
    """
    DB saved slots serializer
    """
    class Meta:
        model = Slot
        fields = ['id', 'slot_num', 'slot_subject', 'slot_type',
                  'slot_group', 'slot_subgroup', 'slot_location',
                  'slot_teacher']

    id = serializers.IntegerField(read_only=True)
    slot_num = serializers.IntegerField(required=True)
    slot_subject = serializers.CharField(required=True, allow_blank=False)
    slot_type = serializers.CharField(required=True, allow_blank=False)
    slot_group = serializers.CharField(required=True, allow_blank=False)
    slot_subgroup = serializers.CharField(required=True, allow_blank=False)
    slot_location = serializers.IntegerField(required=True)
    slot_teacher = serializers.CharField(required=True, allow_blank=False)

    def create(self, validated_data):
        """
        Create and return a new `Slot` instance, given the validated data.
        """
        return Slot.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Slot` instance, given the validated data.
        """
        instance.slot_num = validated_data.get('slot_num', instance.slot_num)
        instance.slot_subject = validated_data.get('slot_subject', instance.slot_subject)
        instance.slot_type = validated_data.get('slot_type', instance.slot_type)
        instance.slot_group = validated_data.get('slot_group', instance.slot_group)
        instance.slot_subgroup = validated_data.get('slot_subgroup', instance.slot_subgroup)
        instance.slot_location = validated_data.get('slot_location', instance.slot_location)
        instance.slot_teacher = validated_data.get('slot_teacher', instance.slot_teacher)
        instance.save()
        return instance

class CompensationSlotSerializer(serializers.HyperlinkedModelSerializer):
    """
    DB saved slots serializer
    """
    class Meta:
        model = Slot
        fields = ['id', 'slot_week', 'slot_id', 'slot_num', 'slot_subject', 'slot_type',
                  'slot_group', 'slot_subgroup', 'slot_location',
                  'slot_teacher']

    id = serializers.IntegerField(read_only=True)
    slot_week = serializers.IntegerField(required=True)
    slot_id = serializers.IntegerField(required=True)
    slot_num = serializers.IntegerField(required=True)
    slot_subject = serializers.CharField(required=True, allow_blank=False)
    slot_type = serializers.CharField(required=True, allow_blank=False)
    slot_group = serializers.CharField(required=True, allow_blank=False)
    slot_subgroup = serializers.CharField(required=True, allow_blank=False)
    slot_location = serializers.IntegerField(required=True)
    slot_teacher = serializers.CharField(required=True, allow_blank=False)

    def create(self, validated_data):
        """
        Create and return a new `Compensation Slot` instance, given the validated data.
        """
        return Slot.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Slot` instance, given the validated data.
        """
        instance.slot_week = validated_data.get('slot_week', instance.slot_week)
        instance.slot_id = validated_data.get('slot_id', instance.slot_id)
        instance.slot_num = validated_data.get('slot_num', instance.slot_num)
        instance.slot_subject = validated_data.get('slot_subject', instance.slot_subject)
        instance.slot_type = validated_data.get('slot_type', instance.slot_type)
        instance.slot_group = validated_data.get('slot_group', instance.slot_group)
        instance.slot_subgroup = validated_data.get('slot_subgroup', instance.slot_subgroup)
        instance.slot_location = validated_data.get('slot_location', instance.slot_location)
        instance.slot_teacher = validated_data.get('slot_teacher', instance.slot_teacher)
        instance.save()
        return instance

# class StaticSlotSerializer(serializers.Serializer):
#     """
#     Excel sheet extracted slots serializer
#     """
#     slot_num = serializers.CharField(required=True)
#     slot_subject = serializers.CharField(required=True, allow_blank=False)
#     slot_type = serializers.CharField(required=True, allow_blank=False)
#     slot_group = serializers.CharField(required=True, allow_blank=False)
#     slot_subgroup = serializers.CharField(required=True, allow_blank=False)
#     slot_location = serializers.CharField(required=True)