from django import forms

from .models import Finca, Actuacion
from django.db.models.fields import BLANK_CHOICE_DASH

class FincaPreparaForm(forms.ModelForm):

    aclaraciones = forms.CharField(required=False, widget=forms.Textarea)

    COMENTARIO_GABITEL_CHOICES_AND_EMPTY = tuple(BLANK_CHOICE_DASH + list(Finca.COMENTARIO_GABITEL_CHOICES))
    comentario_gabitel = forms.ChoiceField(required=False, choices=COMENTARIO_GABITEL_CHOICES_AND_EMPTY)

    class Meta:
        model = Finca
        fields = ('numero_uuii_definitivo', 'resultado_preparacion','comentario_gabitel','aclaraciones')


class FincaReplanteaForm(forms.ModelForm):

    aclaraciones = forms.CharField(required=False, widget=forms.Textarea)

    COMENTARIO_GABITEL_CHOICES_AND_EMPTY = tuple(BLANK_CHOICE_DASH + list(Finca.COMENTARIO_GABITEL_CHOICES))
    comentario_gabitel = forms.ChoiceField(required=False, choices=COMENTARIO_GABITEL_CHOICES_AND_EMPTY)

    class Meta:
        model = Finca
        fields = ('numero_uuii_definitivo', 'resultado_replanteo','comentario_gabitel','aclaraciones')



class FincaAAIIForm(forms.ModelForm):

    aclaraciones = forms.CharField(required=False, widget=forms.Textarea)

    COMENTARIO_GABITEL_CHOICES_AND_EMPTY = tuple(BLANK_CHOICE_DASH + list(Finca.COMENTARIO_GABITEL_CHOICES))

    comentario_gabitel = forms.ChoiceField(required=False, choices=COMENTARIO_GABITEL_CHOICES_AND_EMPTY)

    class Meta:
        model = Finca
        fields = ('numero_uuii_definitivo', 'estado_aaii','comentario_gabitel','aclaraciones')
