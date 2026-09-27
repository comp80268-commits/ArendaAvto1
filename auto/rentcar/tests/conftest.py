import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username="testuser", password="testpass123")

@pytest.fixture
def admin_user(db):
    User = get_user_model()
    return User.objects.create_superuser(username="admin", password="adminpass123")

@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture(autouse=True)
def _use_tmp_media_root(settings, tmp_path):
    """
    Автоматически подменяет MEDIA_ROOT на временную папку для КАЖДОГО теста.
    После завершения теста pytest сам удаляет tmp_path и всё, что в неё
    записали (загруженные тестовые изображения и т.п.), поэтому реальная
    папка media/ больше не засоряется тестовыми файлами.
    """
    settings.MEDIA_ROOT = tmp_path