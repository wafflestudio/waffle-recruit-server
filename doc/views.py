from django.shortcuts import redirect
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
class DocViewSet(GenericViewSet):
    @action(
        detail = False,
        methods=["GET"],
    )
    def api(self, request):
        return redirect("https://daeyong-personal.notion.site/waffle-recruit-server-api-72a4660a794e46c8a2d33012b0d933ae")
    def architecture(self,request):
        # 아키텍쳐도 시간 나면 그려보기
        return redirect("https://daeyong-personal.notion.site/waffle-recruit-server-api-72a4660a794e46c8a2d33012b0d933ae")