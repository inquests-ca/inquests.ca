from django.db.models import Count
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import TemplateHTMLRenderer

from common.models import Jurisdiction
from common.views import ActiveTabMixin, KeywordSearchMixin
from .models import CauseOfDeath, Inquest, InquestKeyword, Participant, Party, Role
from .serializers import InquestDetailSerializer, InquestSerializer


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

        jurisdiction_ids = params.getlist('jurisdiction')
        if jurisdiction_ids:
            queryset = queryset.filter(jurisdiction__id__in=jurisdiction_ids)

        multiple_deaths = params.get('multiple_deaths')
        if multiple_deaths in ('yes', 'no'):
            queryset = queryset.annotate(_deceased_count=Count('deceased', distinct=True))
            if multiple_deaths == 'yes':
                queryset = queryset.filter(_deceased_count__gt=1)
            else:
                queryset = queryset.filter(_deceased_count__lte=1)

        cause_ids = params.getlist('cause')
        if cause_ids:
            queryset = queryset.filter(deceased__cause__id__in=cause_ids).distinct()

        recipient_ids = params.getlist('recipient')
        if recipient_ids:
            queryset = queryset.filter(recommendation_recipients__id__in=recipient_ids).distinct()

        presiding_officer_ids = params.getlist('presiding_officer')
        if presiding_officer_ids:
            queryset = queryset.filter(presiding_officer__id__in=presiding_officer_ids)

        counsel_ids = params.getlist('counsel')
        if counsel_ids:
            queryset = queryset.filter(participants__id__in=counsel_ids).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        params = request.query_params

        response.data['jurisdictions'] = [
            {'id': jurisdiction.id, 'label': jurisdiction.name}
            for jurisdiction in Jurisdiction.objects.filter(does_conduct_inquests=True).order_by('name')
        ]
        response.data['selected_jurisdiction_ids'] = self._selected_ids(params, 'jurisdiction')

        response.data['multiple_deaths'] = params.get('multiple_deaths', '')

        response.data['causes'] = [
            {'id': cause.id, 'label': cause.name}
            for cause in CauseOfDeath.objects.order_by('name')
        ]
        response.data['selected_cause_ids'] = self._selected_ids(params, 'cause')

        response.data['recipients'] = [
            {'id': party.id, 'label': str(party)}
            for party in Party.objects.select_related('party_type').order_by('party_type__name', 'name')
        ]
        response.data['selected_recipient_ids'] = self._selected_ids(params, 'recipient')

        response.data['presiding_officers'] = [
            {'id': participant.id, 'label': str(participant)}
            for participant in Participant.objects.filter(roles__category=Role.Category.POI)
                .distinct().order_by('last_name', 'first_name')
        ]
        response.data['selected_presiding_officer_ids'] = self._selected_ids(params, 'presiding_officer')

        response.data['counsel_options'] = [
            {'id': participant.id, 'label': str(participant)}
            for participant in Participant.objects.filter(roles__category=Role.Category.INQUEST_COUNSEL)
                .distinct().order_by('last_name', 'first_name')
        ]
        response.data['selected_counsel_ids'] = self._selected_ids(params, 'counsel')

        response.data['advanced_open'] = bool(
            response.data['selected_keyword_ids']
            or response.data['selected_jurisdiction_ids']
            or response.data['multiple_deaths']
            or response.data['selected_cause_ids']
            or response.data['selected_recipient_ids']
            or response.data['selected_presiding_officer_ids']
            or response.data['selected_counsel_ids']
        )

        return response

    @staticmethod
    def _selected_ids(params, name):
        return [int(value) for value in params.getlist(name) if value.isdigit()]


class InquestDetailView(ActiveTabMixin, RetrieveAPIView):
    queryset = Inquest.objects.select_related('jurisdiction', 'presiding_officer').prefetch_related(
        'keywords', 'groups', 'recommendation_recipients', 'participants', 'participants__roles',
        'documents', 'deceased', 'deceased__cause',
    )
    serializer_class = InquestDetailSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'inquests/inquest_detail.html'

    active_tab = 'inquests'
