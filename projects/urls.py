from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("register/", views.register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(
        template_name="projects/login.html",
        redirect_authenticated_user=True
    ), name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("projects/create/", views.create_project, name="create_project"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    path("projects/<int:project_id>/tasks/create/", views.create_task, name="create_task"),

    path("tasks/<int:task_id>/", views.task_detail, name="task_detail"),
    path("tasks/<int:task_id>/status/", views.update_task_status, name="update_task_status"),

    path("projects/<int:project_id>/members/add/", views.add_member, name="add_member"),
]
