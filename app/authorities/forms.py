from django import forms

from .models import Authority


class AuthorityForm(forms.ModelForm):
    class Meta:
        model = Authority
        fields = [
            'name',
            'jurisdiction',
            'is_judicial_review',
            'overview',
            'summary',
            'notes',
            'quotes',
            'key_case_reason',
            'keywords',
            'groups',
            'citations',
        ]
        widgets = {
            'overview': forms.Textarea(attrs={'rows': 2}),
            'summary': forms.Textarea(attrs={'rows': 6}),
            'notes': forms.Textarea(attrs={'rows': 4}),
            'quotes': forms.Textarea(attrs={'rows': 4}),
            'keywords': forms.SelectMultiple(attrs={'size': 6, 'class': 'js-multiselect'}),
            'groups': forms.SelectMultiple(attrs={'size': 4, 'class': 'js-multiselect'}),
            'citations': forms.SelectMultiple(attrs={'size': 6, 'class': 'js-multiselect'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['keywords'].queryset = self.fields['keywords'].queryset.order_by('category', 'name')
        self.fields['groups'].queryset = self.fields['groups'].queryset.order_by('name')
        citations_queryset = self.fields['citations'].queryset.order_by('name')
        if self.instance.pk:
            citations_queryset = citations_queryset.exclude(pk=self.instance.pk)
        self.fields['citations'].queryset = citations_queryset
