from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from django.db.models.deletion import CASCADE
from random import choices

# Create your models here.

#when saving the upload path with the name starts here
def resume_dir(instance, filename):
#     dir_name = instance.email 
    return 'mail_attachments/%s' % (filename)
#when saving the upload path with the name ends here

class CandidateDetails(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True,verbose_name=_("Name"))
    email = models.CharField(max_length=50, blank=True, null=True,verbose_name=_("Email"))
    mobile_no = models.CharField(max_length=15, blank=True, null=True,verbose_name=_("Mobile No."))
    from_email = models.CharField(max_length=50, blank=True, null=True,verbose_name=_("From Email"))
    to_email = models.CharField(max_length=50, blank=True, null=True,verbose_name=_("To Email"))
    email_subject = models.TextField(blank=True, null=True,verbose_name=_("Subject"))
    resume = models.FileField(upload_to=resume_dir, blank=True, null=True,verbose_name=_("Resume"))
    created_date = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "Candidate Details"
        verbose_name_plural = "Candidate Details"
        db_table = 'mr_condidates_details'
        

