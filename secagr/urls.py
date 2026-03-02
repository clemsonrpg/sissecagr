from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


# Routers provide an easy way of automatically determining the URL conf.


urlpatterns = [
    path('', include("apps.core.urls", namespace='core')),
    path('pessoas/', include('apps.pessoas.urls', namespace='pessoas')),
    path('admin/', admin.site.urls),
    path('servicos/', include('apps.servicos.urls', namespace='servicos')),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)