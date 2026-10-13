from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from profiles.models import Profile
from .models import Team

@login_required
def team_list_view(request):
    search = request.GET.get('search', '')
    if request.user.is_authenticated:
        teams = Team.objects.filter(created_by=request.user).order_by('id')
    else:
        teams = Team.objects.none()

    if search:
        teams = teams.filter(name__icontains=search)

    return render(request, 'team/team_list.html', {
        'teams': teams,
        'search': search,
    })

@login_required
def team_create_view(request):
    profiles = Profile.objects.filter(created_by=request.user).order_by('name')

    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        leader_name = (request.POST.get('leader_name') or '').strip()
        memo = (request.POST.get('memo') or '').strip()
        member_ids = request.POST.getlist('members')
        self_included = request.POST.get('include-self-member') == '1'

        if not name:
            return render(request, 'team/team_create.html', {
                'profiles': profiles,
                'message': 'チーム名を入力してください',
            })

        team = Team.objects.create(
            created_by=request.user,
            name=name,
            leader_name=leader_name,
            memo=memo,
            self_included=self_included,
        )

        team.members.set(
            Profile.objects.filter(
                id__in=member_ids,
                created_by=request.user
            )
        )

        return redirect('team:team_list')

    return render(request, 'team/team_create.html', {
        'profiles': profiles,
    })

@login_required
def team_edit_view(request, pk):
    team = get_object_or_404(Team, pk=pk, created_by=request.user)
    profiles = Profile.objects.filter(created_by=request.user).order_by('name')

    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        leader_name = (request.POST.get('leader_name') or '').strip()
        memo = (request.POST.get('memo') or '').strip()
        member_ids = request.POST.getlist('members')
        self_included = request.POST.get('include-self-member') == '1'

        if not name:
            return render(request, 'team/team_edit.html', {
                'team': team,
                'profiles': profiles,
                'message': 'チーム名を入力してください',
            })

        team.name = name
        team.leader_name = leader_name
        team.memo = memo
        team.self_included = self_included
        team.save()

        selected_members = Profile.objects.filter(
            id__in=member_ids,
            created_by=request.user
        )
        team.members.set(selected_members)

        return redirect('team:team_list')

    return render(request, 'team/team_edit.html', {
        'team': team,
        'profiles': profiles,
    })

@login_required
def team_delete_view(request, pk):
    team = get_object_or_404(Team, pk=pk, created_by=request.user)
    if request.method == 'POST':
        team.delete()
    return redirect('team:team_list')
