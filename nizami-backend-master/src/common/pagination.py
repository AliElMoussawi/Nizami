from rest_framework.pagination import PageNumberPagination, BasePagination
from rest_framework.response import Response


class PerPagePagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'current_page': self.page.number,
            'per_page': self.page.paginator.per_page,
            'last_page': self.page.paginator.num_pages,
            'data': data,
        })


class IDBasedPagination(BasePagination):
    def __init__(self):
        self.page_size = None
        self.queryset = None

    def paginate_queryset(self, queryset, request, view=None):
        self.page_size = int(request.query_params.get('per_page', 100))

        last_id = request.query_params.get('last_id')

        if last_id:
            queryset = queryset.filter(id__lt=last_id)

        self.queryset = queryset.order_by('-id')[:self.page_size]

        return list(self.queryset)

    def get_paginated_response(self, data):
        last_id = None

        if data and len(data) > 0:
            last_id = data[-1]['id']

        return Response({
            'data': data[::-1],
            'last_id': last_id,
        })
