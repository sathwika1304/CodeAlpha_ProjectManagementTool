from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

from .models import Project, Task, Comment
from .forms import RegisterForm, ProjectForm, TaskForm, CommentForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect("dashboard")

    return render(request, "projects/register.html", {"form": form})


@login_required
def dashboard(request):
    projects = Project.objects.filter(members=request.user).distinct()
    owned_projects = Project.objects.filter(owner=request.user)

    return render(request, "projects/dashboard.html", {
        "projects": projects,
        "owned_projects": owned_projects,
        "total_projects": projects.count(),
        "total_tasks": Task.objects.filter(project__in=projects).count(),
        "completed_tasks": Task.objects.filter(
            project__in=projects, status="done"
        ).count(),
    })


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        form.save_m2m()
        project.members.add(request.user)
        messages.success(request, "Project created successfully!")
        return redirect("project_detail", project_id=project.id)

    return render(request, "projects/project_form.html", {
        "form": form,
        "title": "Create Project",
    })


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.filter(members=request.user).distinct(),
        id=project_id
    )

    tasks = project.tasks.select_related(
        "assigned_to", "created_by"
    ).prefetch_related("comments__author")

    return render(request, "projects/project_detail.html", {
    "project": project,
    "tasks": tasks,
    "task_statuses": Task.STATUS_CHOICES,
})


@login_required
def create_task(request, project_id):
    project = get_object_or_404(
        Project.objects.filter(members=request.user).distinct(),
        id=project_id
    )

    form = TaskForm(request.POST or None)
    form.fields["assigned_to"].queryset = project.members.all()

    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.created_by = request.user
        task.save()
        messages.success(request, "Task created successfully!")
        return redirect("project_detail", project_id=project.id)

    return render(request, "projects/task_form.html", {
        "form": form,
        "project": project,
        "title": "Create Task",
    })


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(
        Task.objects.filter(project__members=request.user).distinct(),
        id=task_id
    )

    form = CommentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        comment = form.save(commit=False)
        comment.task = task
        comment.author = request.user
        comment.save()
        messages.success(request, "Comment added!")
        return redirect("task_detail", task_id=task.id)

    comments = task.comments.select_related("author").order_by("created_at")

    return render(request, "projects/task_detail.html", {
        "task": task,
        "comments": comments,
        "form": form,
    })


@login_required
@require_POST
def update_task_status(request, task_id):
    task = get_object_or_404(
        Task.objects.filter(project__members=request.user).distinct(),
        id=task_id
    )

    status = request.POST.get("status")
    allowed_statuses = {"todo", "in_progress", "done"}

    if status in allowed_statuses:
        task.status = status
        task.save(update_fields=["status"])

    return redirect("project_detail", project_id=task.project_id)


@login_required
@require_POST
def add_member(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    username = request.POST.get("username", "").strip()

    try:
        member = User.objects.get(username=username)
        project.members.add(member)
        messages.success(request, f"{username} added to the project.")
    except User.DoesNotExist:
        messages.error(request, "User not found. Ask them to register first.")

    return redirect("project_detail", project_id=project.id)


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")

    return redirect("dashboard")
