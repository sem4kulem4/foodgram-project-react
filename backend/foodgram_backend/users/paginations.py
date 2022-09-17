from rest_framework.pagination import LimitOffsetPagination


class PagePagination(LimitOffsetPagination):
    """Переопределенная пажинация для страницы с пользователями."""
    offset_query_param = 'page'

    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        if self.limit is None and self.offset == 0:
            return None
        if self.limit is None and self.offset != 0:
            self.limit = 1
        self.count = self.get_count(queryset)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset:self.offset + self.limit])