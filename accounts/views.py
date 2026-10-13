from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import MyUserInfo

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

# =========================
# 新規ユーザー登録（signup）
# =========================
def user_register_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('id') or ''
        password = request.POST.get('password') or ''
        if not user_id or not password:
            return render(request, 'accounts/signup.html', {
                'message': 'IDとパスワードを入力してください'
            })
        if len(user_id) < 5 or len(user_id) > 15:
            return render(request, 'accounts/signup.html', {
                'message': 'IDは5文字以上15文字以下で入力してください'
            })
        if len(password) < 5 or len(password) > 15:
            return render(request, 'accounts/signup.html', {
                'message': 'パスワードは5文字以上15文字以下で入力してください'
            })
        if User.objects.filter(username=user_id).exists():
            return render(request, 'accounts/signup.html', {
                'message': 'このユーザーIDはすでに登録されています'
            })
        User.objects.create_user(username=user_id, password=password)
        return redirect('login')
    return render(request, 'accounts/signup.html')

# =========================
# ログイン
# =========================
def login_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('id') or ''
        password = request.POST.get('password') or ''
        message = 'ユーザIDまたはパスワードが正しくありません'
        try:
            user_obj = User.objects.get(username=user_id)
        except User.DoesNotExist:
            return render(request, 'accounts/login.html', {
                'message': message
            })
        if not user_obj.check_password(password):
            return render(request, 'accounts/login.html', {
                'message': message
            })
        login(request, user_obj)
        return redirect('menu')
    return render(request, 'accounts/login.html')

# =========================
# メニュー
# =========================
@login_required
def menu_view(request):
    user_info = MyUserInfo.objects.filter(user=request.user).first()
    return render(request, 'accounts/menu.html', {
        'user_info': user_info,
    })

# =========================
# マイページ登録
# =========================
@login_required
def user_info_register_view(request):
    if request.method == 'POST':
        if MyUserInfo.objects.filter(user=request.user).exists():
            return render(request, 'accounts/user_info_register.html', {
                'message': 'すでにユーザー情報が登録されています',
                'mbti_choices': MBTI_CHOICES,
                'department_choices': DEPARTMENT_CHOICES,
            })
        photo = request.FILES.get('photo')
        MyUserInfo.objects.create(
            user=request.user,
            photo=photo,
            name=request.POST.get('name') or '',
            mbti=request.POST.get('mbti') or '',
            hobby=request.POST.get('hobby') or '',
            skill=request.POST.get('skill') or '',
            department=request.POST.get('department') or '',
            introduction=request.POST.get('introduction') or '',
        )
        return redirect('menu')
    return render(request, 'accounts/user_info_register.html', {
        'mbti_choices': MBTI_CHOICES,
        'department_choices': DEPARTMENT_CHOICES,
    })

# =========================
# マイページ編集
# =========================
@login_required
def user_info_edit_view(request):
    user_info = MyUserInfo.objects.filter(user=request.user).first()
    if not user_info:
        return redirect('user_info_register')
    if request.method == 'POST':
        user_info.name = request.POST.get('name') or ''
        user_info.mbti = request.POST.get('mbti') or ''
        user_info.hobby = request.POST.get('hobby') or ''
        user_info.skill = request.POST.get('skill') or ''
        user_info.department = request.POST.get('department') or ''
        user_info.introduction = request.POST.get('introduction') or ''
        if request.FILES.get('photo'):
            user_info.photo = request.FILES.get('photo')
        user_info.save()
        return redirect('menu')
    return render(request, 'accounts/user_info_edit.html', {
        'user_info': user_info,
        'mbti_choices': MBTI_CHOICES,
        'department_choices': DEPARTMENT_CHOICES,
    })

# =========================
# ユーザー削除
# =========================
@login_required
def user_delete_view(request):
    if request.method == 'POST':
        user = request.user
        MyUserInfo.objects.filter(user=user).delete()
        logout(request)
        user.delete()
        return redirect('login')
    return render(request, 'accounts/user_delete.html')

# =========================
# ログアウト
# =========================
@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return render(request, 'accounts/logout.html')
