from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import TemplateHTMLRenderer

from common.models import Jurisdiction
from common.views import ActiveTabMixin, KeywordSearchMixin
from .models import Authority, AuthorityKeyword, AuthorityLevel
from .serializers import AuthorityDetailSerializer, AuthoritySerializer


class AuthorityPagination(PageNumberPagination):
    page_size = 10


class AuthorityListView(KeywordSearchMixin, ListAPIView):
    queryset = Authority.objects.select_related('jurisdiction').order_by('id')
    serializer_class = AuthoritySerializer
    pagination_class = AuthorityPagination
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'authorities/authority_list.html'

    search_fields = (
        'name',
        'overview',
        'summary',
        'notes',
        'quotes',
        'key_case_reason',
        'keywords__name',
        'keywords__category',
    )
    keyword_model = AuthorityKeyword
    active_tab = 'authorities'
    sort_fields = {
        'name': 'name',
        'jurisdiction': 'jurisdiction__name',
        'judicial_review': 'is_judicial_review',
        'key_case': 'key_case_reason',
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        jurisdiction_ids = params.getlist('jurisdiction')
        if jurisdiction_ids:
            queryset = queryset.filter(jurisdiction__id__in=jurisdiction_ids)

        level_ids = params.getlist('level')
        if level_ids:
            queryset = queryset.filter(document__level__id__in=level_ids).distinct()

        judicial_review = params.get('judicial_review')
        if judicial_review in ('yes', 'no'):
            queryset = queryset.filter(is_judicial_review=(judicial_review == 'yes'))

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        params = request.query_params

        response.data['jurisdictions'] = [
            {'id': jurisdiction.id, 'label': jurisdiction.name}
            for jurisdiction in Jurisdiction.objects.filter(authorities__isnull=False).distinct().order_by('name')
        ]
        response.data['selected_jurisdiction_ids'] = self._selected_ids(params, 'jurisdiction')

        response.data['levels'] = [
            {'id': level.id, 'label': level.name}
            for level in AuthorityLevel.objects.order_by('-rank')
        ]
        response.data['selected_level_ids'] = self._selected_ids(params, 'level')

        response.data['judicial_review'] = params.get('judicial_review', '')

        response.data['advanced_open'] = bool(
            response.data['selected_keyword_ids']
            or response.data['selected_jurisdiction_ids']
            or response.data['selected_level_ids']
            or response.data['judicial_review']
        )

        return response

    @staticmethod
    def _selected_ids(params, name):
        return [int(value) for value in params.getlist(name) if value.isdigit()]


class AuthorityDetailView(ActiveTabMixin, RetrieveAPIView):
    queryset = Authority.objects.select_related('jurisdiction').prefetch_related(
        'keywords', 'groups',
        'citations', 'citations__document', 'citations__document__level',
        'cited_by', 'cited_by__document', 'cited_by__document__level',
        'document', 'document__level', 'document__jurisdiction',
    )
    serializer_class = AuthorityDetailSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'authorities/authority_detail.html'

    active_tab = 'authorities'
