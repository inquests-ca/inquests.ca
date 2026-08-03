from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import TemplateHTMLRenderer

from common.models import Jurisdiction
from common.views import KeywordSearchMixin
from .forms import InquestForm
from .models import CauseOfDeath, Inquest, InquestKeyword, Participant, Party, Role, Deceased
from .serializers import InquestDetailSerializer, InquestSerializer, DeceasedSerializer


class InquestPagination(PageNumberPagination):
    page_size = 10


class InquestListView(KeywordSearchMixin, ListAPIView):
    queryset = Inquest.objects.select_related('jurisdiction', 'presiding_officer').order_by('id')
    serializer_class = InquestSerializer
    pagination_class = InquestPagination
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'inquests/inquest_list.html'

    search_fields = (
        'name',
        'overview',
        'summary',
        'key_case_reason',
        'response_to_recommendations',
        'deceased__first_name',
        'deceased__middle_name',
        'deceased__last_name',
        'keywords__name',
        'keywords__category',
    )
    keyword_model = InquestKeyword
    active_tab = 'inquests'
    sort_fields = {
        'name': 'import_metadata',
        'jurisdiction': 'jurisdiction__name',
        'presiding_officer': ['presiding_officer__last_name', 'presiding_officer__first_name'],
        'date': 'start_date',
        'key_case': 'key_case_reason',
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        jurisdiction_id = params.get('jurisdiction')
        if jurisdiction_id:
            queryset = queryset.filter(jurisdiction__id=jurisdiction_id)

        multiple_deaths = params.get('multiple_deaths')
        if multiple_deaths in ('yes', 'no'):
            queryset = queryset.annotate(_deceased_count=Count('deceased', distinct=True))
            if multiple_deaths == 'yes':
                queryset = queryset.filter(_deceased_count__gt=1)
            else:
                queryset = queryset.filter(_deceased_count__lte=1)

        cause_id = params.get('cause')
        if cause_id:
            queryset = queryset.filter(deceased__cause__id=cause_id).distinct()

        recipient_id = params.get('recipient')
        if recipient_id:
            queryset = queryset.filter(recommendation_recipients__id=recipient_id).distinct()

        presiding_officer_id = params.get('presiding_officer')
        if presiding_officer_id:
            queryset = queryset.filter(presiding_officer__id=presiding_officer_id)

        counsel_id = params.get('counsel')
        if counsel_id:
            queryset = queryset.filter(participants__id=counsel_id).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        params = request.query_params

        response.data['jurisdictions'] = [
            {'id': jurisdiction.id, 'label': jurisdiction.name}
            for jurisdiction in Jurisdiction.objects.filter(does_conduct_inquests=True).order_by('name')
        ]
        response.data['selected_jurisdiction_id'] = self._selected_id(params, 'jurisdiction')

        response.data['multiple_deaths'] = params.get('multiple_deaths', '')

        response.data['causes'] = [
            {'id': cause.id, 'label': cause.name}
            for cause in CauseOfDeath.objects.order_by('name')
        ]
        response.data['selected_cause_id'] = self._selected_id(params, 'cause')

        response.data['recipients'] = [
            {'id': party.id, 'label': str(party)}
            for party in Party.objects.select_related('party_type').order_by('party_type__name', 'name')
        ]
        response.data['selected_recipient_id'] = self._selected_id(params, 'recipient')

        response.data['presiding_officers'] = [
            {'id': participant.id, 'label': str(participant)}
            for participant in Participant.objects.filter(roles__category=Role.Category.POI)
                .distinct().order_by('last_name', 'first_name')
        ]
        response.data['selected_presiding_officer_id'] = self._selected_id(params, 'presiding_officer')

        response.data['counsel_options'] = [
            {'id': participant.id, 'label': str(participant)}
            for participant in Participant.objects.filter(roles__category=Role.Category.INQUEST_COUNSEL)
                .distinct().order_by('last_name', 'first_name')
        ]
        response.data['selected_counsel_id'] = self._selected_id(params, 'counsel')

        response.data['advanced_open'] = bool(
            response.data['selected_keyword_ids']
            or response.data['selected_jurisdiction_id']
            or response.data['multiple_deaths']
            or response.data['selected_cause_id']
            or response.data['selected_recipient_id']
            or response.data['selected_presiding_officer_id']
            or response.data['selected_counsel_id']
        )

        return response

    @staticmethod
    def _selected_id(params, name):
        value = params.get(name)
        return int(value) if value and value.isdigit() else None


class InquestDetailView(RetrieveAPIView):
    queryset = Inquest.objects.select_related('jurisdiction', 'presiding_officer').prefetch_related(
        'keywords', 'groups', 'recommendation_recipients', 'participants', 'participants__roles',
        'documents', 'deceased', 'deceased__cause',
    )
    serializer_class = InquestDetailSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'inquests/inquest_detail.html'


class InquestUpdateView(LoginRequiredMixin, UpdateView):
    model = Inquest
    form_class = InquestForm
    template_name = 'inquests/inquest_edit.html'

    def get_success_url(self):
        return reverse('inquest-detail', kwargs={'pk': self.object.pk})


class InquestDeleteView(LoginRequiredMixin, DeleteView):
    model = Inquest
    template_name = 'inquests/inquest_confirm_delete.html'
    success_url = reverse_lazy('inquest-list')


class DeceasedDetailView(RetrieveAPIView):
    queryset = Deceased.objects.select_related('cause', 'inquest')
    serializer_class = DeceasedSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'deceased/deceased_detail.html'
