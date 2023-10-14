from math import ceil

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'items': data,

            'pagination': {
                'count': self.page.paginator.count,
                'shown': self.__get_shown(),
                'number': self.page.number,
                'num_pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous()
            }
        })

    def __get_shown(self):
        count = self.page.paginator.count
        shown = self.page_size * self.page.number

        return count if shown > count else shown
