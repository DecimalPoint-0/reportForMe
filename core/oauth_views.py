"""
GitHub OAuth Integration Views
Handles user registration and login via GitHub OAuth
"""
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import redirect
from django.conf import settings
from allauth.socialaccount.models import SocialAccount
from core.models import UserConfig
from core.serializers import UserConfigSerializer
import requests
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def github_login(request):
    """
    Redirect to GitHub OAuth authorization
    Frontend should redirect to this endpoint to start OAuth flow
    """
    client_id = getattr(settings, 'GITHUB_OAUTH_CLIENT_ID', '')
    redirect_uri = f"{request.build_absolute_uri('/accounts/github/login/callback/')}"
    scope = 'user repo read:org'
    
    github_auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"allow_signup=true"
    )
    
    return Response({
        'auth_url': github_auth_url
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Get current authenticated user's config
    Endpoint: GET /api/users/me/
    """
    try:
        user_config = request.user.report_config
        serializer = UserConfigSerializer(user_config)
        return Response(serializer.data)
    except UserConfig.DoesNotExist:
        return Response(
            {'error': 'User config not found. Please complete registration.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_github_registration(request):
    """
    Complete GitHub registration - create/update UserConfig
    Called after successful GitHub OAuth login
    
    Expects POST data:
    {
        "email": "user@example.com",
        "report_time": "18:00",
        "timezone": "UTC"
    }
    """
    user = request.user
    
    try:
        # Get GitHub social account
        social_account = SocialAccount.objects.get(
            user=user,
            provider='github'
        )
        
        github_username = social_account.extra_data.get('login', '')
        github_email = social_account.extra_data.get('email', '')
        
        # Get or create UserConfig
        user_config, created = UserConfig.objects.get_or_create(
            user=user,
            defaults={
                'github_username': github_username,
                'email': request.data.get('email', github_email),
                'report_time': request.data.get('report_time', '18:00'),
                'timezone': request.data.get('timezone', 'UTC'),
            }
        )
        
        # Update if already exists
        if not created:
            user_config.email = request.data.get('email', user_config.email)
            user_config.report_time = request.data.get('report_time', user_config.report_time)
            user_config.timezone = request.data.get('timezone', user_config.timezone)
            user_config.save()
        
        serializer = UserConfigSerializer(user_config)
        return Response({
            'status': 'success',
            'message': 'Registration completed successfully',
            'user_config': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except SocialAccount.DoesNotExist:
        return Response(
            {'error': 'GitHub account not connected. Please try logging in again.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error completing registration: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_github_token(request):
    """
    Refresh/sync GitHub token for current user
    Called after login to ensure token is up to date
    """
    user = request.user
    
    try:
        social_account = SocialAccount.objects.get(
            user=user,
            provider='github'
        )
        
        # Token is stored in social_account.socialaccount_ptr.extra_data['access_token']
        # If expired, allauth should automatically refresh it
        token = social_account.socialaccount_ptr.extra_data.get('access_token')
        
        if not token:
            return Response(
                {'error': 'No GitHub access token found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'status': 'success',
            'message': 'GitHub token is synchronized',
            'token_exists': True
        })
        
    except SocialAccount.DoesNotExist:
        return Response(
            {'error': 'GitHub account not connected'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout current user
    """
    from django.contrib.auth import logout
    logout(request)
    return Response({
        'status': 'success',
        'message': 'Logged out successfully'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def oauth_callback_status(request):
    """
    Check OAuth callback status
    Used by frontend to verify if OAuth was successful
    """
    if request.user.is_authenticated:
        try:
            user_config = request.user.report_config
            return Response({
                'authenticated': True,
                'has_config': True,
                'username': request.user.username,
                'email': request.user.email
            })
        except UserConfig.DoesNotExist:
            return Response({
                'authenticated': True,
                'has_config': False,
                'username': request.user.username,
                'email': request.user.email,
                'message': 'Please complete registration'
            })
    else:
        
        return Response({
            'authenticated': False,
            'message': 'Not authenticated'
        })
