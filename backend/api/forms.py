# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from .models import Slot  

# class AddressMixin(forms.ModelForm):
#     class Meta:
#         model = Slot
#         fields = ('num', 'subject', 'type', 'group', 'subgroup', 'location')
#         widgets = {
#             'num': forms.NumberInput(attrs={'class':'form-control'}),
#             'subject': forms.TextInput(attrs={'class':'form-control'}),
#             'type': forms.TextInput(attrs={'class':'form-control'}),
#             'group': forms.TextInput(attrs={'class':'form-control'}),
#             'subgroup': forms.TextInput(attrs={'class':'form-control'}),
#             'location': forms.NumberInput(attrs={'class':'form-control'}),
#         }  


# class CompensationSlotForm(AddressMixin, UserCreationForm):
#     slot_num = forms.IntegerField(
#         required=True, widget=forms.NumberInput(attrs={'class':'form-control'})
#     )
#     slot_subject = forms.CharField(
#         required=True, widget=forms.TextInput(attrs={'class':'form-control'})
#     )
#     slot_type = forms.CharField(
#         required=True, widget=forms.TextInput(attrs={'class':'form-control'})
#     )
#     slot_group = forms.CharField(
#         required=True, widget=forms.TextInput(attrs={'class':'form-control'})
#     )
#     slot_subgroup = forms.CharField(
#         required=True, widget=forms.TextInput(attrs={'class':'form-control'})
#     )
#     slot_location = forms.IntegerField(
#         required=True, widget=forms.TextInput(attrs={'class':'form-control'})
#     )