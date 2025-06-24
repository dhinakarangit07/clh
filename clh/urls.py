from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views



urlpatterns = [
    path("django-admin/", admin.site.urls),
    
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    

    #custom urls
    path("", include("login.urls")),
    path("", include("client.urls")),
    path("", include("case.urls")),
    path("", include("reminder.urls")),
    path("", include("calander.urls")),
    path("", include('user_profile.urls')), 
    path("", include('cadmin.urls')), 
    path("", include('advocate.urls')), 
    path("", include('invoice.urls')), 
    path("", include('court.urls')), 
    path("", include('forum.urls')), 
    path("", include('student.urls')),
    path("", include('senior_advocate.urls')),  
    path("", include('task.urls')),  
    path("", include('handbag.urls')),  
    path("", include('cowork.urls')),  
    #####


    path("", include(wagtailadmin_urls)),

]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



# urlpatterns = urlpatterns + [
#     # For anything not caught by a more specific rule above, hand over to
#     # Wagtail's page serving mechanism. This should be the last pattern in
#     # the list:
#     path("", include(wagtail_urls)),
#     # Alternatively, if you want Wagtail pages to be served from a subpath
#     # of your site, rather than the site root:
#     #    path("pages/", include(wagtail_urls)),
# ]
