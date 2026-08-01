from django.db.models import Q


def _windowed_page_numbers(current, total, window=2):
    """Page numbers to display for jumping between pages: first, last, and
    a window around the current page, with `None` standing in for an
    ellipsis gap between non-adjacent numbers."""
    kept = [
        n for n in range(1, total + 1)
        if n == 1 or n == total or current - window <= n <= current + window
    ]
    numbers = []
    previous = None
    for n in kept:
        if previous is not None and n - previous > 1:
            numbers.append(None)
        numbers.append(n)
        previous = n
    return numbers


class KeywordSearchMixin:
    """Adds free-text search (`q`), keyword multi-select filtering
    (`keywords`), and column sorting (`sort`/`dir`) to a DRF ListAPIView, and
    injects the keyword options, current selection, and sort-toggle links
    into the paginated response for template rendering.

    Subclasses set `search_fields`, `keyword_model`, `active_tab`, and
    `sort_fields` (a dict mapping a `sort` query param value to the
    queryset field(s), e.g. `{'jurisdiction': 'jurisdiction__name'}`).
    """

    search_fields = ()
    keyword_model = None
    active_tab = None
    sort_fields = {}

    def get_queryset(self):
        queryset = super().get_queryset()

        # Chaining one `.filter()` call per word (rather than matching the
        # whole query as a single substring) requires each word to be found
        # -- possibly in different fields -- so "Smith John" matches a
        # record with first_name=John, last_name=Smith just as well as
        # "John Smith" does.
        query = self.request.query_params.get('q', '').strip()
        words = query.split()
        if words and self.search_fields:
            for word in words:
                condition = Q()
                for field in self.search_fields:
                    condition |= Q(**{f'{field}__icontains': word})
                queryset = queryset.filter(condition)
            queryset = queryset.distinct()

        # Chaining one `.filter()` call per keyword (rather than a single
        # `keywords__id__in=keyword_ids` call) requires each selected
        # keyword to be present -- via a separate join per call -- giving
        # AND semantics instead of OR.
        keyword_ids = self.request.query_params.getlist('keywords')
        for keyword_id in keyword_ids:
            queryset = queryset.filter(keywords__id=keyword_id)
        if keyword_ids:
            queryset = queryset.distinct()

        sort_key = self.request.query_params.get('sort')
        if sort_key in self.sort_fields:
            fields = self.sort_fields[sort_key]
            if isinstance(fields, str):
                fields = [fields]
            if self.request.query_params.get('dir') == 'desc':
                fields = [f'-{field}' for field in fields]
            queryset = queryset.order_by(*fields)

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

        current_sort = request.query_params.get('sort', '')
        current_dir = request.query_params.get('dir', 'asc')
        sort_links = {}
        for key in self.sort_fields:
            next_dir = 'desc' if current_sort == key and current_dir == 'asc' else 'asc'
            params = request.query_params.copy()
            params['sort'] = key
            params['dir'] = next_dir
            params.pop('page', None)
            sort_links[key] = f'{request.path}?{params.urlencode()}'
        response.data['sort_links'] = sort_links
        response.data['sort'] = current_sort
        response.data['sort_dir'] = current_dir

        page = getattr(self.paginator, 'page', None)
        current_page = page.number if page is not None else 1
        total_pages = page.paginator.num_pages if page is not None else 1

        page_params = request.query_params.copy()
        page_links = []
        for page_number in _windowed_page_numbers(current_page, total_pages):
            if page_number is None:
                page_links.append({'number': None, 'url': None, 'is_current': False})
                continue
            page_params['page'] = page_number
            page_links.append({
                'number': page_number,
                'url': f'{request.path}?{page_params.urlencode()}',
                'is_current': page_number == current_page,
            })
        response.data['page_links'] = page_links
        response.data['current_page'] = current_page
        response.data['total_pages'] = total_pages

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
