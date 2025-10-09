class ForceDatatablesFormatMixin:
    def initial(self, request, *args, **kwargs):
        if request.method == "POST" and 'format' not in request.POST:
            request.GET._mutable = True
            request.GET['format'] = 'datatables'
            request.GET._mutable = False

        super().initial(request, *args, **kwargs)
