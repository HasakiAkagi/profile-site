from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Profile


MBTI_CHOICES = [
    "ENFJ", "ENFP", "INFJ", "INFP",
    "ENTJ", "ENTP", "INTJ", "INTP",
    "ESTP", "ESFP", "ISTP", "ISFP",
    "ESTJ", "ESFJ", "ISTJ", "ISFJ",
]

DEPARTMENT_CHOICES = [
    "SVCP-DP",
    "SVCP-AD",
    "SVCP-SVI",
]

RELATIONSHIP_CHOICES = [
    "同期",
    "先輩",
    "後輩",
]

def get_mbti_group(mbti):
    mbti = (mbti or '').upper()
    if mbti in {'ESTP', 'ESFP', 'ISTP', 'ISFP'}:
        return 'yellow'
    if mbti in {'ENFJ', 'ENFP', 'INFJ', 'INFP'}:
        return 'green'
    if mbti in {'ENTJ', 'ENTP', 'INTJ', 'INTP'}:
        return 'purple'
    if mbti in {'ESFJ', 'ESTJ', 'ISFJ', 'ISTJ'}:
        return 'blue'
    return None

# 一覧
@login_required
def profile_list_view(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.filter(created_by=request.user)
    else:
        profiles = Profile.objects.none()

    search = request.GET.get('search', '')
    if search:
        profiles = profiles.filter(name__icontains=search)

    message = 'プロフィールが登録されていません' if not profiles.exists() else None
    return render(request, 'profiles/list.html', {
        'profiles': profiles,
        'search': search,
        'message': message,
    })

# 登録
@login_required
def profile_register_view(request):
    if request.method == 'POST':
        photo = request.FILES.get('photo')
        name = (request.POST.get('name') or '').strip()
        mbti = (request.POST.get('mbti') or '').strip()
        hobby = (request.POST.get('hobby') or '').strip()
        skill = (request.POST.get('skill') or '').strip()
        department = (request.POST.get('department') or '').strip()
        relationship = (request.POST.get('relationship') or '').strip()
        talk = (request.POST.get('talk') or '').strip()

        if not photo or not name or not mbti or not hobby or not skill or not department or not relationship or not talk:
            return render(request, 'profiles/register.html', {
                'message': '未入力の項目があります。入力してください。',
                'mbti_choices': MBTI_CHOICES,
                'department_choices': DEPARTMENT_CHOICES,
                'relationship_choices': RELATIONSHIP_CHOICES,
            })

        Profile.objects.create(
            created_by=request.user,
            name=name,
            mbti=mbti,
            hobby=hobby,
            skill=skill,
            department=department,
            relationship=relationship,
            talk=talk,
            photo=photo,
        )
        return redirect('profiles:profile_list')

    return render(request, 'profiles/register.html', {
        'mbti_choices': MBTI_CHOICES,
        'department_choices': DEPARTMENT_CHOICES,
        'relationship_choices': RELATIONSHIP_CHOICES,
    })

# 編集
@login_required
def profile_edit_view(request, pk):
    profile = get_object_or_404(Profile, pk=pk, created_by=request.user)

    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        mbti = (request.POST.get('mbti') or '').strip()
        hobby = (request.POST.get('hobby') or '').strip()
        skill = (request.POST.get('skill') or '').strip()
        department = (request.POST.get('department') or '').strip()
        relationship = (request.POST.get('relationship') or '').strip()
        talk = (request.POST.get('talk') or '').strip()

        if not name or not mbti or not hobby or not skill or not department or not relationship or not talk:
            return render(request, 'profiles/edit.html', {
                'profile': profile,
                'message': '未入力の項目があります。入力してください。',
                'mbti_choices': MBTI_CHOICES,
                'department_choices': DEPARTMENT_CHOICES,
                'relationship_choices': RELATIONSHIP_CHOICES,
            })

        profile.name = name
        profile.mbti = mbti
        profile.hobby = hobby
        profile.skill = skill
        profile.department = department
        profile.relationship = relationship
        profile.talk = talk

        if request.FILES.get('photo'):
            profile.photo = request.FILES.get('photo')

        profile.save()
        return redirect('profiles:profile_list')

    return render(request, 'profiles/edit.html', {
        'profile': profile,
        'mbti_choices': MBTI_CHOICES,
        'department_choices': DEPARTMENT_CHOICES,
        'relationship_choices': RELATIONSHIP_CHOICES,
    })

# 削除
def profile_delete_view(request, pk):
    profile = get_object_or_404(Profile, pk=pk, created_by=request.user)
    if request.method == 'POST':
        profile.delete()
    return redirect('profiles:profile_list')

# MBTI集計
def mbti_view(request):
    department = request.GET.get('department', '')
    relationship = request.GET.get('relationship', '')
    searched = False

    if request.user.is_authenticated:
        profiles = Profile.objects.filter(created_by=request.user)
    else:
        profiles = Profile.objects.none()

    if department:
        profiles = profiles.filter(department=department)
        searched = True

    if relationship:
        profiles = profiles.filter(relationship=relationship)
        searched = True

    blue_profiles = []
    green_profiles = []
    yellow_profiles = []
    purple_profiles = []

    for profile in profiles:
        group = get_mbti_group(profile.mbti)
        if group == 'blue':
            blue_profiles.append(profile)
        elif group == 'green':
            green_profiles.append(profile)
        elif group == 'yellow':
            yellow_profiles.append(profile)
        elif group == 'purple':
            purple_profiles.append(profile)

    blue_count = len(blue_profiles)
    green_count = len(green_profiles)
    yellow_count = len(yellow_profiles)
    purple_count = len(purple_profiles)
    total_count = blue_count + green_count + yellow_count + purple_count

    def calc_percent(count):
        return round((count / total_count) * 100, 1) if total_count > 0 else 0

    context = {
        'department': department,
        'relationship': relationship,
        'searched': searched,
        'blue_profiles': blue_profiles,
        'green_profiles': green_profiles,
        'yellow_profiles': yellow_profiles,
        'purple_profiles': purple_profiles,
        'blue_count': blue_count,
        'green_count': green_count,
        'yellow_count': yellow_count,
        'purple_count': purple_count,
        'blue_percent': calc_percent(blue_count),
        'green_percent': calc_percent(green_count),
        'yellow_percent': calc_percent(yellow_count),
        'purple_percent': calc_percent(purple_count),
        'message': 'プロフィール情報が登録されていません' if not profiles.exists() else None,
        'department_choices': DEPARTMENT_CHOICES,
        'relationship_choices': RELATIONSHIP_CHOICES,
    }
    return render(request, 'profiles/mbti.html', context)
