from django import forms
from modoboa.admin.models import Domain
from modoboa.lib import _check_password
from django.contrib.auth.models import check_password
from django.utils.translation import ugettext as _
from modoboa.lib import split_mailbox

class BadDestination(Exception):
    pass

class ChangePasswordForm(forms.Form):
    oldpassword = forms.CharField(label=_("Old password"), 
                                  widget=forms.PasswordInput)
    newpassword = forms.CharField(label=_("New password"), 
                                  widget=forms.PasswordInput)
    confirmation = forms.CharField(label=_("Confirmation"), 
                                   widget=forms.PasswordInput)

    def __init__(self, target, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.target = target

    def clean_oldpassword(self):
        if not isinstance(self.target, Mailbox):
            func = check_password
        else:
            func = _check_password
        if not func(self.cleaned_data["oldpassword"], 
                    self.target.password):
            raise forms.ValidationError(_("Old password mismatchs"))
        return self.cleaned_data["oldpassword"]

    def clean_confirmation(self):
        if self.cleaned_data["newpassword"] != self.cleaned_data["confirmation"]:
            raise forms.ValidationError(_("Passwords mismatch"))
        return self.cleaned_data["confirmation"]

class ForwardForm(forms.Form):
    dest = forms.CharField(label=_("Destination(s)"), widget=forms.Textarea)

    def parse_dest(self):
        self.dests = []
        for d in self.cleaned_data["dest"].strip().split(","):
            local_part, domname = split_mailbox(d)
            if not local_part or not domname or not len(domname):
                raise BadDestination("Invalid mailbox syntax for %s" % d)
            try:
                mb = Domain.objects.get(name=domname)
            except Mailbox.DoesNotExist:
                self.dests += [d]
            else:
                raise BadDestination(_("You can't define a forward to a local destination. Please ask your administrator to create an alias instead."))
        
