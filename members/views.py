from django.http.response import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponseBadRequest
from members.models import Member
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin import site
from members.forms import SendMemberActivationEmailsForm
from django.contrib import messages
from django.urls import reverse
from mxv.settings import JOIN_URL, CREATE_INACTIVE_MEMBER_SECRET
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import render
from mxv.models import EmailSettings

# signals that a conflict occurred
class HttpResponseConflict(HttpResponse):
    status_code = 409

# creates an inactive member for the email and name (POST with email, name and secret)
@csrf_exempt
def create_inactive_member(request):
        # if it's a post and the secret is correct...
        if request.method == 'POST' and request.POST['secret'] == CREATE_INACTIVE_MEMBER_SECRET:
            
            # if the member doesn't already exist...
            if not Member.objects.filter(email = request.POST['email']).exists():

                # create the member
                member = Member.objects.create_member(email = request.POST['email'], name = request.POST['name'])
                
                # send the activation email
                activation_email = EmailSettings.get_solo().activation_email
                if activation_email:
                    try:
                        activation_email.send_to(request, [member.email])
                    except Exception as e:
                        return HttpResponseBadRequest(content = repr(e) + ' (email address is probably invalid)')
                
                return HttpResponse(content = 'Created inactive member for ' + request.POST['email'])
            else:
                # signal that the member already exists
                return HttpResponseConflict(content = 'Member with email %s already exists' % request.POST['email'])
        else:
            return HttpResponseForbidden()

# sends the member activation email
@staff_member_required
def send_member_activation_emails(request):
    
    # include the django admin context for the member links
    context = site.each_context(request)

    # populate the form with the email settings in case this is a GET
    email_settings = EmailSettings.get_solo()
    form = SendMemberActivationEmailsForm(instance = email_settings)
    
    # if a valid post...
    if request.method == 'POST':
        form = SendMemberActivationEmailsForm(request.POST)
        if form.is_valid():           
            try:
                
                # update the email settings
                if not ('cancel' in request.POST):
                    email_settings.test_email_address = form.cleaned_data['test_email_address']
                    email_settings.send_count = form.cleaned_data['send_count']
                    email_settings.is_active = form.cleaned_data['is_active']
                    email_settings.activation_email = form.cleaned_data['activation_email']
                    email_settings.save()

                # if there is an activation email set...
                if email_settings.activation_email:
                    
                    # send the activation email to the test address
                    if 'send_test' in request.POST:
                        sent = email_settings.activation_email.send_test(request)
                        messages.info(request, "%d member%s emailed" % (sent, 's' if sent != 1 else ''))
                        
                    # send the activation email to uninvited members
                    if 'send_to_count_uninvited' in request.POST:
                        sent = email_settings.activation_email.send_to_count_uninvited(request)
                        messages.info(request, "%d member%s emailed" % (sent, 's' if sent != 1 else ''))
                        
                    # send the activation email to targeted members
                    if 'send_to_count_targeted' in request.POST:
                        sent = email_settings.activation_email.send_to_count_targeted(request)
                        messages.info(request, "%d member%s emailed" % (sent, 's' if sent != 1 else ''))
                        
                    # send the activation email to inactive members
                    if 'send' in request.POST:
                        sent = email_settings.activation_email.send_to_inactive_members(request)
                        messages.info(request, "%d member%s emailed" % (sent, 's' if sent != 1 else ''))
                    
            except Exception as e:
                messages.error(request, repr(e))
        
        # redirect
        return HttpResponseRedirect(reverse('membersadmin:send_member_activation_emails'))
                        
    # add the form to the context
    context['form'] = form
    
    # render the page
    return render(request, 'admin/send_member_activation_emails.html', context)

# activates the member
def activate(request, activation_key):
    
    # get the member with the activation key
    member = Member.objects.filter(activation_key = activation_key).first()
    
    # redirect activation attempts for an unknown member to the join page
    if not member:
        return HttpResponseRedirect(JOIN_URL)
    
    # redirect activation attempts for an active member to the login page
    if member.is_active:
        return HttpResponseRedirect(reverse('login'))

    # if valid post...
    if request.method == 'POST':
        form = SetPasswordForm(member, request.POST)
        if form.is_valid():
            
            # make the member active and save the user's password
            member.is_active = True
            member = form.save()
            
            # log the member in
            update_session_auth_hash(request, member)
            authenticate(request)
            login(request, member)
            messages.success(request, 'Your password was successfully set!')
            return HttpResponseRedirect('/')
        else:
            #show errors
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SetPasswordForm(member)

    return render(request, 'members/activate.html', { 
        'member' : member,
        'form': form })

