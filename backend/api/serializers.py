from rest_framework import serializers
from .models import Slot


class SlotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Slot
        fields = ['id', 'slot_num', 'slot_subject', 'slot_type',
                  'slot_group', 'slot_subgroup', 'slot_location']

    id = serializers.IntegerField(read_only=True)
    slot_num = serializers.IntegerField(required=True)
    slot_subject = serializers.CharField(required=True, allow_blank=False)
    slot_type = serializers.CharField(required=True, allow_blank=False)
    slot_group = serializers.CharField(required=True, allow_blank=False)
    slot_subgroup = serializers.CharField(required=True, allow_blank=False)
    slot_location = serializers.IntegerField(required=True)

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
        instance.save()
        return instance