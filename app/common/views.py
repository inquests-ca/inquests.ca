from django.db.models import Q


class KeywordSearchMixin:
    """Adds free-text search (`q`) and keyword multi-select filtering
    (`keywords`) to a DRF ListAPIView, and injects the keyword options and
    current selection into the paginated response for template rendering.

    Subclasses set `search_fields`, `keyword_model`, and `active_tab`.
    """

    search_fields = ()
    keyword_model = None
    active_tab = None

    def get_queryset(self):
        queryset = super().get_queryset()

        query = self.request.query_params.get('q', '').strip()
        if query and self.search_fields:
            condition = Q()
            for field in self.search_fields:
                condition |= Q(**{f'{field}__icontains': query})
            queryset = queryset.filter(condition)

        keyword_ids = self.request.query_params.getlist('keywords')
        if keyword_ids:
            queryset = queryset.filter(keywords__id__in=keyword_ids).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        response.data['keywords'] = [
            {'id': keyword.id, 'label': str(keyword)}
            for keyword in self.keyword_model.objects.order_by('category', 'name')
        ]
        response.data['selected_keyword_ids'] = [
            int(keyword_id) for keyword_id in request.query_params.getlist('keywords') if keyword_id.isdigit()
        ]
        response.data['query'] = request.query_params.get('q', '')
        response.data['active_tab'] = self.active_tab

        return response


class ActiveTabMixin:
    """Injects `active_tab` into a DRF RetrieveAPIView's response, so the
    detail page templates can highlight the right sidebar toggle option.
    """

    active_tab = None

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response.data['active_tab'] = self.active_tab
        return response
