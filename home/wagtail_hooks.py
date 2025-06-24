from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup






from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.urls import reverse

# @hooks.register('register_admin_menu_item')
# def register_users_menu_item():
#     return MenuItem(
#         'Users',                     # Menu label
#         reverse('wagtailusers_users:index'),  # Named URL for Wagtail users index
#         icon_name='user',            # Icon (use any Wagtail icon name)
#         order=1000                   # Order in the menu (adjust as needed)
#     )




@hooks.register('construct_main_menu')
def hide_explorer_menu_item_from_frank(request, menu_items):
    new_menu_items = []
    for item in menu_items:
        if not item.name in ['reports','help','explorer','documents','images']:
            new_menu_items.append(item)
    menu_items[:] = new_menu_items



@hooks.register('construct_settings_menu')
def hide_settings_items(request, menu_items):

    new_menu_items = []
    for item in menu_items:
        if not item.name in ['redirects','sites','collections','workflows','workflow-tasks']:
            new_menu_items.append(item)
    menu_items[:] = new_menu_items




