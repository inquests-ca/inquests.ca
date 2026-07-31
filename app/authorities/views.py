from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import TemplateHTMLRenderer

from common.views import ActiveTabMixin, KeywordSearchMixin
from .models import Authority, AuthorityKeyword
from .serializers import AuthorityDetailSerializer, AuthoritySerializer


class AuthorityPagination(PageNumberPagination):
    page_size = 10


class AuthorityListView(KeywordSearchMixin, ListAPIView):
    queryset = Authority.objects.select_related('jurisdiction').order_by('id')
    serializer_class = AuthoritySerializer
    pagination_class = AuthorityPagination
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'authorities/authority_list.html'

    search_fields = ('name', 'overview', 'summary')
    keyword_model = AuthorityKeyword
    active_tab = 'authorities'


class AuthorityDetailView(ActiveTabMixin, RetrieveAPIView):
    queryset = Authority.objects.select_related('jurisdiction').prefetch_related(
        'keywords', 'groups', 'citations', 'cited_by', 'document', 'document__level', 'document__jurisdiction',
    )
    serializer_class = AuthorityDetailSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'authorities/authority_detail.html'

    active_tab = 'authorities'
