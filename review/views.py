from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Track, Theme, Proposal, Amendment, Comment
from django.db.models import Count
from review.forms import EditProposalForm, ProposalForm, DeleteProposalForm, AmendmentForm, EditAmendmentForm, DeleteAmendmentForm, EditCommentForm, ModerationRequestForm, CommentForm

@login_required
def index(request):
    return render(request, 'review/index.html', { 
        'tracks' : Track.objects.all().order_by('display_order') })

@login_required
def track(request, pk):
    track = get_object_or_404(Track, pk = pk)
    return render(request, 'review/tracks/track.html', { 
        'track' : track, 
        'themes': track.themes.order_by('display_order') })
    
@login_required
def theme(request, pk):
    theme = get_object_or_404(Theme, pk = pk)
    user_proposal = theme.proposals.filter(created_by = request.user).first()
    return render(request, 'review/themes/theme.html', { 
        'theme' : theme, 
        'proposals': theme.proposals.annotate(nomination_count = Count('nominations')).order_by('-nomination_count', '-created_at', 'pk'),
        'user_proposal': user_proposal })

@login_required
def proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk = pk)
    moderation = request.user.moderation_requests.filter(proposal = proposal).first()
    
    # if valid post...
    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():        
            
            # nominate if allowed
            if 'nominate' in request.POST and proposal.theme.track.nominations_currently_allowed():
                for nomination in request.user.nominations.filter(proposal__theme = proposal.theme):
                    nomination.delete()
                proposal.nominations.create(proposal = proposal, nominated_by = request.user)
                
            # clear nomination if allowed
            if 'clear_nomination' in request.POST and proposal.theme.track.nominations_currently_allowed():
                nomination = proposal.nominations.filter(nominated_by = request.user, proposal = proposal).first()
                if nomination:
                    nomination.delete()
                    
            # cancel moderation if moderation request exists
            if 'cancel_moderation' in request.POST and moderation:
                moderation.delete()
                    
            return redirect('review:proposal', pk = proposal.pk)
    else:
        form = ProposalForm(instance = proposal)

    return render(request, 'review/proposals/proposal.html', { 
        'proposal' : proposal,
        'proposal_urls' : proposal.urls.order_by('pk'),
        'amendments' : proposal.amendments.order_by('-created_at'),
        'comments' : proposal.comments.order_by('-created_at'),
        'user_nominated': request.user.nominations.filter(proposal = proposal).exists(),
        'moderation': moderation,
        'form': form })

@login_required
def new_proposal(request, pk):
    theme = get_object_or_404(Theme, pk = pk)
    
    # redirect if submissions are not allowed or user already has a proposal in this theme
    if not theme.track.nominations_currently_allowed() or request.user.proposals.filter(theme = theme).exists():
        return redirect('review:theme', pk = theme.pk)

    # if valid post...
    if request.method == "POST":
        form = EditProposalForm(request.POST)
        if form.is_valid():
            
            # create proposal
            proposal = form.save(commit = False)
            proposal.theme = theme
            proposal.created_by = request.user
            proposal.save()
            
            return redirect('review:proposal_submitted', pk = theme.pk)
    else:
        form = EditProposalForm()
        
    return render(request, 'review/proposals/new_proposal.html', { 
        'theme' : theme,
        'form' : form })

@login_required
def proposal_submitted(request, pk):
    theme = get_object_or_404(Theme, pk = pk)
    return render(request, 'review/proposals/proposal_submitted.html', { 
        'theme' : theme })

@login_required
def edit_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk = pk)
    
    # redirect if moderated, submissions are not allowed or incorrect user
    if proposal.moderated() or not proposal.theme.track.submissions_currently_allowed() or request.user != proposal.created_by:
        return redirect('review:proposal', pk = proposal.pk)

    # if valid post...
    if request.method == "POST":
        form = EditProposalForm(request.POST, instance = proposal)
        if form.is_valid():
            
            # save the proposal
            proposal = form.save()
            
            return redirect('review:proposal', pk = proposal.pk)
    else:
        form = EditProposalForm(instance = proposal)
        
    return render(request, 'review/proposals/edit_proposal.html', { 
        'proposal' : proposal,
        'form' : form })

@login_required
def delete_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk = pk)
    
    # redirect if submissions are not allowed or incorrect user
    if not proposal.theme.track.submissions_currently_allowed() or request.user != proposal.created_by:
        return redirect('review:proposal', pk = proposal.pk)

    # if valid post...
    if request.method == "POST":
        form = DeleteProposalForm(request.POST, instance = proposal)
        if form.is_valid():
            
            # delete the proposal
            proposal.delete()
            
            return redirect('review:theme', pk = proposal.theme.pk)
    else:
        form = DeleteProposalForm(instance = proposal)
        
    return render(request, 'review/proposals/delete_proposal.html', { 
        'proposal' : proposal,
        'form' : form })

@login_required
def moderate_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk = pk)
        
    # redirect if user created the proposal or has already moderated it
    if request.user == proposal.created_by or request.user.moderation_requests.filter(proposal = proposal).first():
        return redirect('review:proposal', pk = proposal.pk)

    # if valid post...
    if request.method == "POST":
        form = ModerationRequestForm('proposal', request.POST)
        if form.is_valid():
            
            # save the moderation request
            moderation_request = form.save(commit = False)
            moderation_request.proposal = proposal
            moderation_request.requested_by = request.user
            moderation_request.save()
            
            # notify that moderation is required
            moderation_request.notify_staff(request)
            
            return redirect("review:proposal", pk = pk)
    else:
        form = ModerationRequestForm('proposal')
    
    return render(request, 'review/proposals/moderate_proposal.html', {
        'proposal': proposal,
        'form' : form })
    
@login_required
def amendment(request, pk):
    amendment = get_object_or_404(Amendment, pk = pk)
    moderation = request.user.moderation_requests.filter(amendment = amendment).first()
     
    # if valid post...
    if request.method == 'POST':
        form = AmendmentForm(request.POST)
        if form.is_valid():        
                                        
            # cancel moderation if moderation request exists
            if moderation:
                moderation.delete()
                    
            return redirect('review:amendment', pk = amendment.pk)        
    else:
        form = AmendmentForm(instance = amendment) 
    
    return render(request, 'review/amendments/amendment.html', { 
        'amendment' : amendment,
        'moderation': moderation,
        'form': form })

@login_required
def new_amendment(request, pk):
    proposal = get_object_or_404(Proposal, pk = pk)
    
    # redirect if submissions are not allowed
    if not proposal.theme.track.nominations_currently_allowed():
        return redirect('review:proposal', pk = proposal.pk)

    # if valid post...
    if request.method == "POST":
        form = EditAmendmentForm(request.POST)
        if form.is_valid():
            
            # save the amendment
            amendment = form.save(commit = False)
            amendment.proposal = proposal
            amendment.created_by = request.user
            amendment.save()
            
            return redirect('review:proposal', pk = proposal.pk)
    else:
        form = EditAmendmentForm()
        
    return render(request, 'review/amendments/new_amendment.html', { 
        'proposal' : proposal,
        'form' : form })

@login_required
def edit_amendment(request, pk):
    amendment = get_object_or_404(Amendment, pk = pk)
    
    # redirect if moderated, submissions are not allowed or incorrect user
    if amendment.moderated() or not amendment.proposal.theme.track.submissions_currently_allowed() or request.user != amendment.created_by:
        return redirect('review:amendment', pk = amendment.pk)

    # if valid post...
    if request.method == "POST":
        form = EditAmendmentForm(request.POST, instance = amendment)
        if form.is_valid():
            
            # save the amendment
            amendment = form.save()
            
            return redirect('review:amendment', pk = amendment.pk)
    else:
        form = EditAmendmentForm(instance = amendment)
        
    return render(request, 'review/amendments/edit_amendment.html', { 
        'amendment' : amendment,
        'form' : form })

@login_required
def delete_amendment(request, pk):
    amendment = get_object_or_404(Amendment, pk = pk)
    
    # redirect if submissions are not allowed or incorrect user
    if not amendment.proposal.theme.track.submissions_currently_allowed() or request.user != amendment.created_by:
        return redirect('review:amendment', pk = amendment.pk)

    # if valid post...
    if request.method == "POST":
        form = DeleteAmendmentForm(request.POST, instance = amendment)
        if form.is_valid():
            
            # delete the amendment
            amendment.delete()
            return redirect('review:proposal', pk = amendment.proposal.pk)
    else:
        form = DeleteAmendmentForm(instance = amendment)
        
    return render(request, 'review/amendments/delete_amendment.html', { 
        'amendment' : amendment,
        'form' : form })

@login_required
def moderate_amendment(request, pk):
    # get the amendment
    amendment = get_object_or_404(Amendment, pk = pk)
        
    # redirect if user created the amendment or has already moderated it
    if request.user == amendment.created_by or request.user.moderation_requests.filter(amendment = amendment).first():
        return redirect('review:amendment', pk = amendment.pk)

    # if this is a valid post...
    if request.method == "POST":
        form = ModerationRequestForm('amendment', request.POST)
        if form.is_valid():
            
            # save the moderation request
            moderation_request = form.save(commit = False)
            moderation_request.amendment = amendment
            moderation_request.requested_by = request.user
            moderation_request.save()
            
            # notify that moderation is required
            moderation_request.notify_staff(request)
            
            # return to the referring entity
            return redirect("review:amendment", pk = pk)
    else:
        form = ModerationRequestForm('amendment')
    
    return render(request, 'review/amendments/moderate_amendment.html', {
        'amendment': amendment,
        'form' : form })
    
@login_required
def comment(request, pk):    
    comment = get_object_or_404(Comment, pk = pk)
    moderation = request.user.moderation_requests.filter(comment = comment).first()
    
    # if valid post...
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():        
                                
            # cancel moderation if moderation request exists
            if moderation:
                moderation.delete()
                    
            return redirect('review:comment', pk = comment.pk)
    else:
        form = CommentForm(instance = comment)
    
    return render(request, 'review/comments/comment.html', { 
        'comment' : comment,
        'moderation': moderation,
        'form': form })

@login_required
def new_comment(request, pk):
    proposal = get_object_or_404(Proposal, pk = pk)
    
    # redirect if comments are not allowed
    if not proposal.theme.track.allow_comments:
        return redirect('review:proposal', pk = proposal.pk)

    # if valid post...
    if request.method == "POST":
        form = EditCommentForm(request.POST)
        if form.is_valid():
            
            # save the comment
            comment = form.save(commit = False)
            comment.proposal = proposal
            comment.created_by = request.user
            comment.save()
            return redirect('review:proposal', pk = proposal.pk)
    else:
        form = EditCommentForm()
    return render(request, 'review/comments/new_comment.html', { 
        'proposal' : proposal,
        'form' : form })

@login_required
def moderate_comment(request, pk):
    comment = get_object_or_404(Comment, pk = pk)
        
    # redirect if user created the comment or has already moderated it
    if request.user == comment.created_by or request.user.moderation_requests.filter(comment = comment).first():
        return redirect('review:comment', pk = comment.pk)

    # if this is a valid post...
    if request.method == "POST":
        form = ModerationRequestForm('comment', request.POST)
        if form.is_valid():
            
            # save the moderation request
            moderation_request = form.save(commit = False)
            moderation_request.comment = comment
            moderation_request.requested_by = request.user
            moderation_request.save()
            
            # notify that moderation is required
            moderation_request.notify_staff(request)
            
            # return to the referring entity
            return redirect("review:comment", pk = pk)
    else:
        form = ModerationRequestForm('comment')
    
    return render(request, 'review/comments/moderate_comment.html', {
        'comment': comment,
        'form' : form })
    
@login_required
def help(request):
    return render(request, 'review/support/help.html')

@login_required
def rules(request):
    return render(request, 'review/support/rules.html')

@login_required
def faq(request):
    return render(request, 'review/support/faq.html')

@login_required
def moderation(request):
    return render(request, 'review/support/moderation.html')

@login_required
def guide(request):
    return render(request, 'review/support/guide.html')

