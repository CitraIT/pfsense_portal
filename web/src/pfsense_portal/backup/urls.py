from django.urls import path
from .views import index, run_backup, download_backup


urlpatterns = [
    path('', index, name='backup_index'),
    path('policy/<int:policy_id>/run', run_backup, name='run_backup'),
    path('<int:backup_id>/download', download_backup, name='download_backup')
]