from rest_framework import viewsets
from .models import Project
from rest_framework.decorators import action
from .serializers import ProjectSerializer
from rest_framework.response import Response


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "")
        results = Project.objects.filter(name__icontains=query)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
