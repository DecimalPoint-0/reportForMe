"""
URL Router for API endpoints
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    UserConfigViewSet, ReportViewSet, CommitViewSet, GithubRepositoryViewSet
)
from core.oauth_views import (
    github_login,
    get_current_user,
    complete_github_registration,
    sync_github_token,
    logout_user,
    oauth_callback_status,
)

router = DefaultRouter()
router.register(r'users', UserConfigViewSet, basename='user-config')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'commits', CommitViewSet, basename='commit')
router.register(r'repositories', GithubRepositoryViewSet, basename='repository')

urlpatterns = [
    path('api/', include(router.urls)),
    # OAuth endpoints
    path('api/auth/github/login/', github_login, name='github-login'),
    path('api/auth/github/callback/', oauth_callback_status, name='oauth-callback-status'),
    path('api/users/me/', get_current_user, name='current-user'),
    path('api/auth/complete-registration/', complete_github_registration, name='complete-registration'),
    path('api/auth/sync-token/', sync_github_token, name='sync-token'),
    path('api/auth/logout/', logout_user, name='logout'),
]
