from django.urls import path
from .api import *

urlpatterns = [
    path('api/planning/lookup/', lookup_planning_by_code, name='lookup_planning'),
    path('api/planning/submit/', submit_planning_data, name='submit_planning_data'),
    path('api/planning/get/', getPlanningsView.as_view(), name='get_plannings'),
    path('api/login/', login_api, name='login_api'),
    path('api/files/<int:file_id>/approve/', ApproveFileView.as_view(), name='approve_file'),
    path('api/files/<int:file_id>/refuse/', RefuseFileView.as_view(), name='refuse_file'),
    path('api/planning/<int:planning_id>/approve/', ApprovePlanningView.as_view(), name='approve_planning'),
    path('api/planning/<int:planning_id>/refuse/', RefusePlanningView.as_view(), name='refuse_planning'),
    path('api/devices/register/', register_device),
    path('api/devices/unregister/', unregister_device),
]
