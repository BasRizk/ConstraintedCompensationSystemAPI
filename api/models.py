from django.db import models

# Create your models here.
from django.core.validators import MaxValueValidator, MinValueValidator

SLOT_NUM_VALIDATORS = [MinValueValidator(0), MaxValueValidator(29)]
SLOT_LOCATION_VALIDATORS = [MinValueValidator(0), MaxValueValidator(63)]
SLOT_WEEK_VALIDATORS = [MinValueValidator(0), MaxValueValidator(14)]
# SLOT_TYPE_CHOICES = ["big_lec", "small_lec", "lab", "tut"]


class Slot(models.Model):
    """
    DB Model representing a single slot in schedule
    """
    id = models.AutoField(primary_key=True)
    slot_num = models.IntegerField(validators=SLOT_NUM_VALIDATORS)
    slot_subject = models.CharField(max_length=60)
    slot_type = models.CharField(max_length=32)
    slot_group = models.CharField(max_length=60)
    slot_subgroup = models.CharField(max_length=60)
    slot_location = models.IntegerField(validators=SLOT_LOCATION_VALIDATORS)
    slot_teacher = models.CharField(max_length=60)
    slot_week = models.IntegerField(validators=SLOT_WEEK_VALIDATORS)

    def __str__(self):
        return '{}, {}, {}, {}, {}, {}'.format(self.slot_num,
                                            self.slot_subject,
                                            self.slot_type,
                                            self.slot_group,
                                            self.slot_subgroup,
                                            self.slot_location,
                                            self.slot_teacher,
                                            self.slot_week)

    class Meta:
        verbose_name_plural = 'slots'
        ordering = ['slot_week', 'slot_num', 'slot_group', 'slot_subgroup']

    def __unicode__(self):
        return u"Slot at time %s in location %s" % (str(
            self.slot_num), str(self.slot_location))
