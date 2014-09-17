import re
import string
from django import forms
from django.db.models import Q


#==============================================================================
class SearchForm(forms.Form):
    search = forms.CharField(required=False)
    letter = forms.CharField(required=False)


#==============================================================================
def search_contacts(request, contacts, association):
    valid = False
    letter = 'ALL'
    searchtext = ''
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            searchtext = form.cleaned_data['search']
            letter = form.cleaned_data['letter']

            #filter letters if any
            if letter == "ALL":
                pass
            elif letter == "0-9":
                allowed_chars = string.digits
                query = None
                for c in allowed_chars:
                    if not query:
                        query = Q(last_name__startswith=c)
                    else:
                        query |= Q(last_name__startswith=c)
                contacts = contacts.filter(query)
            elif letter == "...":
                not_allowed_chars = string.letters + string.digits
                query = None
                for c in not_allowed_chars:
                    if not query:
                        query = Q(last_name__istartswith=c)
                    else:
                        query |= Q(last_name__istartswith=c)
                contacts = contacts.exclude(query)
            else:
                contacts = contacts.filter(Q(last_name__istartswith=letter))

            # search tokens
            for token in re.findall('\w+', searchtext):
                search_query = Q(first_name__icontains=token)
                search_query |= Q(middle_name__icontains=token)
                search_query |= Q(last_name__icontains=token)
                search_query |= Q(emails__address__icontains=token)
                search_query |= Q(phones__number__icontains=token)
                search_query |= Q(addresses__address__icontains=token)

                # search in uuids
                search_query |= Q(_uuid=token)

                # search in tags
                search_query |= Q(tags__name=token)

                # search in custom fields
                #search_query |= CustomQ(Contact, association, token)

                # TODO - add other applications but only if purchased
                #search_query |= Q(dogs__name__icontains=token)

                contacts = contacts.filter(search_query)

            valid = True

    return valid, searchtext, letter, contacts


#==============================================================================
def search_events(request, events, association):
    valid = False
    searchtext = ''
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            searchtext = form.cleaned_data['search']

            # search tokens
            for token in re.findall('\w+', searchtext):
                search_query = Q(title__icontains=token)
                search_query |= Q(details__icontains=token)
                search_query |= Q(author__first_name__icontains=token)
                search_query |= Q(author__last_name__icontains=token)
                search_query |= Q(author__email__icontains=token)
                search_query |= Q(contacts__first_name__icontains=token)
                search_query |= Q(contacts__last_name__icontains=token)
                search_query |= Q(contacts__emails__address__icontains=token)
                search_query |= Q(contacts__phones__number__icontains=token)
                search_query |= Q(contacts__addresses__address__icontains=token)

                # search in uuids
                search_query |= Q(_uuid=token)

                # search in tags
                search_query |= Q(tags__name=token)

                # search in custom fields
                #search_query |= CustomQ(Event, association, token)

                events = events.filter(search_query)

            valid = True

    return valid, searchtext, events
