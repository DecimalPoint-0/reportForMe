"""
URL Router for API endpoints
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    UserConfigViewSet, ReportViewSet, CommitViewSet, GithubRepositoryViewSet
)

router = DefaultRouter()
router.register(r'users', UserConfigViewSet, basename='user-config')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'commits', CommitViewSet, basename='commit')
router.register(r'repositories', GithubRepositoryViewSet, basename='repository')

urlpatterns = [
    path('api/', include(router.urls)),
]
