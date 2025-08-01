from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination (PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = 6
