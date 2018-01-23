from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Track, Theme, Proposal, Amendment
from django.db.models import Count
from review.forms import EditProposalForm, ProposalForm, DeleteProposalForm, AmendmentForm, EditAmendmentForm, DeleteAmendmentForm

@login_required
def index(request):
    return render(request, 'review/index.html', { 
        'tracks' : Track.objects.all().order_by('display_order') })

@login_required
def track(request, pk):
    track = get_object_or_404(Track, pk = pk)
    return render(request, 'review/track.html', { 
        'track' : track, 
        'themes': track.themes.order_by('display_order') })
    
@login_required
def theme(request, pk):
    theme = get_object_or_404(Theme, pk = pk)
    user_proposal = theme.proposals.filter(created_by = request.user).first()
    return render(request, 'review/theme.html', { 
        'theme' : theme, 
        'proposals': theme.proposals.annotate(nomination_count = Count('nominations')).order_by('-nomination_count', '-created_at'),
        'user_proposal': user_proposal })

@login_required
def proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk = pk)
    form = ProposalForm(instance = proposal)
    return render(request, 'review/proposal.html', { 
        'proposal' : proposal,
        'amendments' : proposal.amendments.order_by('-created_at'),
        'comments' : proposal.comments.order_by('-created_at'),
        'form': form })

@login_required
def new_proposal(request, pk):
    theme = get_object_or_404(Theme, pk = pk)
    
    # silent redirect back to theme as the user must have crafted/cached a URL to get here
    if not theme.track.allow_proposals:
        return redirect('review:theme', pk = theme.pk)

    if request.method == "POST":
        form = EditProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit = False)
            proposal.theme = theme
            proposal.created_by = request.user
            proposal.save()
            return redirect('review:theme', pk = theme.pk)
    else:
        form = EditProposalForm()
    return render(request, 'review/new_proposal.html', { 
        'theme' : theme,
        'form' : form })

@login_required
def edit_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk = pk)
    
    # silent redirect back to proposal as the user must have crafted/cached a URL to get here
    if not proposal.theme.track.allow_proposals:
        return redirect('review:proposal', pk = proposal.pk)

    if proposal.created_by == request.user and request.method == "POST":
        form = EditProposalForm(request.POST, instance = proposal)
        if form.is_valid():
            proposal = form.save()
            return redirect('review:proposal', pk = proposal.pk)
    else:
        form = EditProposalForm(instance = proposal)
    return render(request, 'review/edit_proposal.html', { 
        'proposal' : proposal,
        'form' : form })

@login_required
def delete_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk = pk)
    
    # silent redirect back to proposal as the user must have crafted/cached a URL to get here
    if not proposal.theme.track.allow_proposals:
        return redirect('review:proposal', pk = proposal.pk)

    if proposal.created_by == request.user and request.method == "POST":
        form = DeleteProposalForm(request.POST, instance = proposal)
        if form.is_valid():
            proposal.delete()
            return redirect('review:theme', pk = proposal.theme.pk)
    else:
        form = DeleteProposalForm(instance = proposal)
    return render(request, 'review/delete_proposal.html', { 
        'proposal' : proposal,
        'form' : form })

@login_required
def amendment(request, pk):
    amendment = get_object_or_404(Amendment, pk = pk)
    form = AmendmentForm(instance = amendment)
    return render(request, 'review/amendment.html', { 
        'amendment' : amendment,
        'form': form })

@login_required
def new_amendment(request, pk):
    proposal = get_object_or_404(Proposal, pk = pk)
    
    # silent redirect back to proposal as the user must have crafted/cached a URL to get here
    if not proposal.theme.track.allow_amendments:
        return redirect('review:proposal', pk = proposal.pk)

    if request.method == "POST":
        form = EditAmendmentForm(request.POST)
        if form.is_valid():
            amendment = form.save(commit = False)
            amendment.proposal = proposal
            amendment.created_by = request.user
            amendment.save()
            return redirect('review:proposal', pk = proposal.pk)
    else:
        form = EditAmendmentForm()
    return render(request, 'review/new_amendment.html', { 
        'proposal' : proposal,
        'form' : form })

@login_required
def edit_amendment(request, pk):
    amendment = get_object_or_404(Amendment, pk = pk)
    
    # silent redirect back to proposal as the user must have crafted/cached a URL to get here
    if not amendment.proposal.theme.track.allow_amendments:
        return redirect('review:amendment', pk = amendment.pk)

    if amendment.created_by == request.user and request.method == "POST":
        form = EditAmendmentForm(request.POST, instance = amendment)
        if form.is_valid():
            amendment = form.save()
            return redirect('review:amendment', pk = amendment.pk)
    else:
        form = EditAmendmentForm(instance = amendment)
    return render(request, 'review/edit_amendment.html', { 
        'amendment' : amendment,
        'form' : form })

@login_required
def delete_amendment(request, pk):
    amendment = get_object_or_404(Amendment, pk = pk)
    
    # silent redirect back to proposal as the user must have crafted/cached a URL to get here
    if not amendment.proposal.theme.track.allow_amendments:
        return redirect('review:amendment', pk = amendment.pk)

    if amendment.created_by == request.user and request.method == "POST":
        form = DeleteAmendmentForm(request.POST, instance = amendment)
        if form.is_valid():
            amendment.delete()
            return redirect('review:proposal', pk = amendment.proposal.pk)
    else:
        form = DeleteAmendmentForm(instance = amendment)
    return render(request, 'review/delete_amendment.html', { 
        'amendment' : amendment,
        'form' : form })

