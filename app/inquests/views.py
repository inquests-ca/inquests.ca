from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import TemplateHTMLRenderer

from common.views import ActiveTabMixin, KeywordSearchMixin
from .models import Inquest, InquestKeyword
from .serializers import InquestDetailSerializer, InquestSerializer


class InquestPagination(PageNumberPagination):
    page_size = 10


class InquestListView(KeywordSearchMixin, ListAPIView):
    queryset = Inquest.objects.select_related('jurisdiction', 'presiding_officer').order_by('id')
    serializer_class = InquestSerializer
    pagination_class = InquestPagination
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'inquests/inquest_list.html'

    search_fields = ('name', 'overview', 'summary')
    keyword_model = InquestKeyword
    active_tab = 'inquests'


class InquestDetailView(ActiveTabMixin, RetrieveAPIView):
    queryset = Inquest.objects.select_related('jurisdiction', 'presiding_officer').prefetch_related(
        'keywords', 'groups', 'recommendation_recipients', 'documents', 'deceased', 'deceased__cause',
    )
    serializer_class = InquestDetailSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'inquests/inquest_detail.html'

    active_tab = 'inquests'
