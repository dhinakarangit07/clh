# from wagtail import hooks
# from wagtail.admin.menu import MenuItem
# from django.urls import path, reverse
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required, permission_required

# @login_required
# @permission_required('wagtailadmin.access_admin')
# def dashboard_view(request):
#     return render(request, 'summery.html', {'title': 'Admin Dashboard'})

# @login_required
# @permission_required('wagtailadmin.access_admin')
# def admin_redirect(request):
#     return redirect(reverse('dashboard'))

# @hooks.register('register_admin_urls')
# def register_admin_urls():
#     return [
#         path('dashboard/', dashboard_view, name='dashboard'),
#         path('', admin_redirect, name='admin_redirect'),
#     ]

# @hooks.register('register_admin_menu_item')
# def register_dashboard_menu_item():
#     return MenuItem(
#         'Dashboard',
#         reverse('dashboard'),
#         icon_name='desktop',
#         order=100
#     )