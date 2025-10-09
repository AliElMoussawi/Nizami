from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet


class CreateViewSet(GenericViewSet):
    input_serializer_class = None
    output_serializer_class = None

    def get_input_serializer(self, *args, **kwargs):
        serializer_class = self.get_input_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_output_serializer(self, *args, **kwargs):
        serializer_class = self.get_output_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_input_serializer_class(self):
        return self.input_serializer_class

    def get_output_serializer_class(self):
        return self.output_serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_input_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        output_serializer = self.get_output_serializer(serializer.instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
