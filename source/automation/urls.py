from django.urls import path
from . import api, views

urlpatterns = [
    path("automacao/", views.page_automation, name="pagina_automacao"),

    path("api/v1/automation/dashboard", api.automation_dashboard, name="automation_dashboard"),
    path("api/v1/automation/enable", api.enable_automation, name="enable_automation"),
    path("api/v1/automation/disable", api.disable_automation, name="disable_automation"),
    path("api/v1/automation/configuration", api.save_configuration, name="save_configuration"),
    path("api/v1/automation/api", api.save_api, name="save_api"),
]
