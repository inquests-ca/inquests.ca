from django import forms

from .models import Inquest, Participant, Role


class InquestForm(forms.ModelForm):
    class Meta:
        model = Inquest
        fields = [
            'name',
            'jurisdiction',
            'presiding_officer',
            'start_date',
            'end_date',
            'sitting_days',
            'recommendation_count',
            'response_to_recommendations',
            'overview',
            'summary',
            'key_case_reason',
            'keywords',
            'groups',
            'recommendation_recipients',
            'participants',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'overview': forms.Textarea(attrs={'rows': 2}),
            'summary': forms.Textarea(attrs={'rows': 6}),
            'response_to_recommendations': forms.Textarea(attrs={'rows': 4}),
            'keywords': forms.SelectMultiple(attrs={'size': 6, 'class': 'js-multiselect'}),
            'groups': forms.SelectMultiple(attrs={'size': 4, 'class': 'js-multiselect'}),
            'recommendation_recipients': forms.SelectMultiple(attrs={'size': 5, 'class': 'js-multiselect'}),
            'participants': forms.SelectMultiple(attrs={'size': 5, 'class': 'js-multiselect'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['presiding_officer'].queryset = (
            Participant.objects.filter(roles__category=Role.Category.POI)
            .distinct().order_by('last_name', 'first_name')
        )
        self.fields['participants'].queryset = Participant.objects.order_by('last_name', 'first_name')
        self.fields['keywords'].queryset = self.fields['keywords'].queryset.order_by('category', 'name')
        self.fields['groups'].queryset = self.fields['groups'].queryset.order_by('name')
        self.fields['recommendation_recipients'].queryset = (
            self.fields['recommendation_recipients'].queryset.select_related('party_type')
            .order_by('party_type__name', 'name')
        )
