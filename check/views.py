from rest_framework import permissions, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from check.models import Solver
from .serializers import SubmissionService, SkeletonService, ResultService

class SubmissionViewSet(GenericViewSet):
    @action(
        detail=True,
        methods=["POST"],
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=SubmissionService,
    )
    def submit(self, request, pk=None):
        serializer = self.get_serializer(data=request.data, context={**self.get_serializer_context(), 'prob_num': int(pk)})
        serializer.is_valid(raise_exception=True)
        return serializer.execute()

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=ResultService,
    )
    def result(self, request, pk=None):
        serializer = self.get_serializer(data=request.data, context={**self.get_serializer_context(), 'prob_num': int(pk)})
        serializer.is_valid(raise_exception=True)
        return serializer.execute()

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def prob_solvers(self, request, pk=None):
        solve_cnt = Solver.objects.filter(prob_num=int(pk)).count()
        return Response({'number': solve_cnt})

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=SkeletonService,
    )
    def skeleton(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.execute()

    