from django.apps import AppConfig

from ..common.utils import load_aspose_license


class ChatsConfig(AppConfig):
    name = 'src.chats'

    def ready(self):
        load_aspose_license()
