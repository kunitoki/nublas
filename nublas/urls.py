from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView, RedirectView

from .conf import settings

from .ui.skins import get_skin_relative_path
from .ui.views.home import *
from .ui.views.auth import *
from .ui.views.association import *
from .ui.views.contact import *


#==============================================================================
urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url=settings.INDEX_URL), name='home'),
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^tags/$', TagsAutoCompleteView.as_view(), name='tags'),
)


#==============================================================================
urlpatterns += patterns('',
    # association editing
    url(r'^association/list/$', AssociationListView.as_view(), name='association_list'),
    url(r'^association/add/$', AssociationAddView.as_view(), name='association_add'),
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/details/$', AssociationDetailsView.as_view(), name='association_details'),
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/edit/$', AssociationEditView.as_view(), name='association_edit'),
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/delete/$', AssociationDeleteView.as_view(), name='association_delete'),

    # association contacts handling
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/contacts/$', AssociationContactListView.as_view(), name='association_contacts'),
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/contacts/action/$', AssociationContactListActionView.as_view(), name='association_contacts_action'),

    # association file handling
    #url(r'^association/(?P<association>[a-fA-F0-9]{32})/files/$', AssociationFilesView.as_view(), name='association_files'),
    #url(r'^association/(?P<association>[a-fA-F0-9]{32})/fileserve/$', AssociationFileServeView.as_view(), name='association_fileserve'),

    # association agenda handling
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/agenda/$', AssociationAgendaView.as_view(), name='association_agenda'),
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/agenda/latest/$', AssociationAgendaLatestView.as_view(), name='association_agenda_latest'),

    # association custom fields
    #url(r'^(?P<association>[a-fA-F0-9]{32})/custom/$', AssociationCustomView.as_view(), name='association_custom'),
    #url(r'^(?P<association>[a-fA-F0-9]{32})/custom/add/$', AssociationCustomAddView.as_view(), name='association_custom_add'),
    #url(r'^custom/(?P<object>[a-fA-F0-9]{32})/edit/$', AssociationCustomEditView.as_view(), name='association_custom_edit'),
    #url(r'^custom/(?P<object>[a-fA-F0-9]{32})/delete/$', AssociationCustomDeleteView.as_view(), name='association_custom_delete'),

    # association settings
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/settings/$', AssociationSettingsView.as_view(), name='association_settings'),

    # TODO - add specific settings
)


#==============================================================================
urlpatterns += patterns('',
    # globals
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/contact/add/$', ContactAddView.as_view(), name='contact_add'),
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/contact/autocomplete/$', ContactAutoCompleteView.as_view(), name='contact_search_autocomplete'),

    # details
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/details/$', ContactDetailsView.as_view(), name='contact_details'),
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/edit/$', ContactEditView.as_view(), name='contact_edit'),
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/delete/$', ContactDeleteView.as_view(), name='contact_delete'),
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/files/$', ContactFilesView.as_view(), name='contact_files'),
    #url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/fileserve/$', ContactFileServeView.as_view(), name='contact_fileserve'),

    # addresses
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/address/add/$', ContactAddressAddView.as_view(), name='contact_address_add'),
    url(r'^contact/address/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactAddressEditView.as_view(), name='contact_address_edit'),
    url(r'^contact/address/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactAddressDeleteView.as_view(), name='contact_address_delete'),

    # phones
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/phone/add/$', ContactPhoneAddView.as_view(), name='contact_phone_add'),
    url(r'^contact/phone/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactPhoneEditView.as_view(), name='contact_phone_edit'),
    url(r'^contact/phone/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactPhoneDeleteView.as_view(), name='contact_phone_delete'),

    # emails
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/email/add/$', ContactEmailAddView.as_view(), name='contact_email_add'),
    url(r'^contact/email/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactEmailEditView.as_view(), name='contact_email_edit'),
    url(r'^contact/email/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactEmailDeleteView.as_view(), name='contact_email_delete'),

    # websites
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/websites/add/$', ContactWebsiteAddView.as_view(), name='contact_website_add'),
    url(r'^contact/websites/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactWebsiteEditView.as_view(), name='contact_website_edit'),
    url(r'^contact/websites/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactWebsiteDeleteView.as_view(), name='contact_website_delete'),

    # groups
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/group/add/$', ContactGroupAddView.as_view(), name='contact_group_add'),
    url(r'^contact/group/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactGroupEditView.as_view(), name='contact_group_edit'),
    url(r'^contact/group/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactGroupDeleteView.as_view(), name='contact_group_delete'),

    # subscriptions
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/subscriptions/$', ContactSubscriptionView.as_view(), name='contact_subscriptions'),
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/subscription/add/$', ContactSubscriptionAddView.as_view(), name='contact_subscription_add'),
    url(r'^contact/subscription/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactSubscriptionEditView.as_view(), name='contact_subscription_edit'),
    url(r'^contact/subscription/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactSubscriptionDeleteView.as_view(), name='contact_subscription_delete'),

    # partecipations
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/partecipations/$', ContactPartecipationView.as_view(), name='contact_partecipations'),

    # relationships
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/relationships/$', ContactRelationshipView.as_view(), name='contact_relationships'),
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/relationship/add/$', ContactRelationshipAddView.as_view(), name='contact_relationship_add'),
    url(r'^contact/relationship/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactRelationshipEditView.as_view(), name='contact_relationship_edit'),
    url(r'^contact/relationship/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactRelationshipDeleteView.as_view(), name='contact_relationship_delete'),
)


#==============================================================================
# Only enable login based urls if requested
if settings.ENABLE_USER_LOGIN:
    urlpatterns += patterns('',
        # profile login
        url(r'^auth/login/$', LoginView.as_view(), name='auth_login'),
        url(r'^auth/logout/$', LogoutView.as_view(), name='auth_logout'),

        # user profile editing
        url(r'^auth/profile/$', ProfileView.as_view(), name='auth_profile'),

        # lost password and username
        url(r'^auth/lost_password/$', LostPasswordView.as_view(), name='auth_lost_password'),
        url(r'^auth/lost_password_change/(?P<lost_password_key>.*)/$', LostPasswordChangeView.as_view(), name='auth_lost_password_change'),
        url(r'^auth/lost_username/$', LostUsernameView.as_view(), name='auth_lost_username'),

        # su
        url(r'^su/(?P<username>.*)/$', SuperuserView, { 'redirect_url': settings.INDEX_URL }),
    )


#==============================================================================
# Only enable new registration if requested
if settings.ENABLE_USER_REGISTRATION:
    urlpatterns += patterns('',
        # user registration and activation
        url(r'^auth/register/$', RegisterView.as_view(), name='auth_register'),
        url(r'^auth/activate/(?P<activation_key>.*)/$', ActivateView.as_view(), name='auth_activate'),
    )


#==============================================================================
# Debug views
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^500/$', TemplateView.as_view(template_name=get_skin_relative_path('500.html'))),
        (r'^404/$', TemplateView.as_view(template_name=get_skin_relative_path('404.html'))),
        (r'^403/$', TemplateView.as_view(template_name=get_skin_relative_path('403.html'))),
    )
