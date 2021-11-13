from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Firewall
from .forms import FirewallForm


#
#
#
@login_required
def index(request):
    firewalls = Firewall.objects.all()
    return render(request, 'firewall/firewall.html', context={'firewalls': firewalls})



#
#
#
@login_required
def add_firewall(request):
    submitted = False
    if request.method == "POST":
        form = FirewallForm(request.POST)
        if form.is_valid():
            firewall = form.save()
            return HttpResponseRedirect(f'/firewall/')
    else:
        form = FirewallForm()
        if 'submitted' in request.GET:
            submitted = True
    
    return render(request, 'firewall/add.html', context={'form':form, 'submitted':submitted})



#
#
#
@login_required
def edit_firewall(request, firewall_id):
    if request.method == "GET":
        firewall = Firewall.objects.get(id=firewall_id)
        form = FirewallForm(instance=firewall)
        return render(request, "firewall/edit.html", {'form': form, 'firewall': firewall})
    elif request.method == "POST":
        firewall = Firewall.objects.get(id=firewall_id)
        form = FirewallForm(request.POST, instance=firewall)
        submitted = False
        if form.is_valid():
            form.save()
            submitted = True
            return render(request, "firewall/edit.html", {'form': form, 'submitted': submitted, 'firewall': firewall })
        else:
            return render(request, "firewall/edit.html", {'form': form})



#
#
#
@login_required
def delete_firewall(request, firewall_id):
    firewall = Firewall.objects.get(id=firewall_id)
    firewall.delete()
    return render(request, "firewall/delete.html", {'firewall': firewall, 'submitted': True})






