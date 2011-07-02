from django.core.mail import send_mail, send_mass_mail
from django.db import models
from os import path

# Create your models here.
class FuneralHomeProfile(models.Model):
    STATES = (
        ('Alaska', 'Alaska',),
        ('Ariz.', 'Ariz.',),
        ('Calif.', 'Calif.',),
        ('Colo.', 'Colo.',),
        ('Conn.', 'Conn.',),
        ('Del.', 'Del.',),
        ('Fla.', 'Fla.',),
        ('Ga.', 'Ga.',),
        ('Hawaii', 'Hawaii',),
        ('Idaho', 'Idaho',),
        ('Ill.', 'Ill.',),
        ('Ind.', 'Ind.',),
        ('Kan.', 'Kan.',),
        ('Ky.', 'Ky.',),
        ('La.', 'La. ',),
        ('Mass.', 'Mass.',),
        ('Md.', 'Md.',),
        ('Mich.', 'Mich.',),
        ('Minn.', 'Minn.',),
        ('Miss.', 'Miss.',),
        ('Mo.', 'Mo.',),
        ('Mont.', 'Mont.',),
        ('Neb.', 'Neb.',),
        ('Nev.', 'Nev.',),
        ('N.C.', 'N.C.',),
        ('N.D.', 'N.D.',),
        ('N.H.', 'N.H.',),
        ('N.M.', 'N.M.',),
        ('N.J.', 'N.J.',),
        ('N.Y.', 'N.Y.',),
        ('Okla.', 'Okla.',),
        ('Pa.', 'Pa.',),
        ('R.I.', 'R.I.',),
        ('S.C.', 'S.C.',),
        ('S.D.', 'S.D.',),
        ('Texas', 'Texas',),
        ('Tenn.', 'Tenn.',),
        ('Utah', 'Utah',),
        ('Va.', 'Va.',),
        ('Vt.', 'Vt.',),
        ('Wash.', 'Wash.',),
        ('W.Va.', 'W.Va.',),
        ('Wis.', 'Wis.',),
        ('Wyo.', 'Wyo.',),
    )
    user = models.OneToOneField('auth.User')
    full_name = models.CharField(max_length=80)
    city = models.CharField(max_length=80, blank=True, help_text=u'Leave blank when city name is part of funeral home name, i.e., \'Oakridge Funeral Home Chapel of the Woods\'')
    state = models.CharField(max_length=6, choices=STATES, blank=True, help_text=u'Leave blank if located in Oregon')
    phone = models.CharField(max_length=12, blank=True)
    
    class Meta:
        ordering = ('full_name',)
    
    def __unicode__(self):
        if self.city:
            return '%s in %s' % (self.full_name, self.city)
        else:
            return '%s' % self.full_name

class Death_notice(models.Model):
    AGE_UNIT_CHOICES = (
        (1, 'years',),
        (2, 'days',),
    )
    funeral_home = models.ForeignKey('auth.User')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=95, blank=True, help_text='Middle name or initial.')
    nickname = models.CharField(max_length=90, blank=True, help_text='Just enter name, without double-quotes, i.e. Jack, not "Jack"')
    last_name = models.CharField(max_length=105)
    age = models.IntegerField()
    age_unit = models.IntegerField(default=1, choices=AGE_UNIT_CHOICES)
    city_of_residence = models.CharField(max_length=110)
    formerly_of = models.CharField(max_length=126, blank=True)
    death_date = models.DateField()
    death_notice_in_system = models.BooleanField()
    death_notice_has_run = models.BooleanField()
    death_notice_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Death notice'
        unique_together = ('first_name', 'last_name', 'age', 'death_date',)
    
    def __unicode__(self):
        return u'Death notice for %s %s' % (self.first_name, self.last_name)
    
    def save(self):
        from_email = 'rgnews.registerguard.@gmail.com'
        to_email = ['john.heasly@registerguard.com']
        message_email = 'Go to the death notice admin page for further information.'
        
        if(self.id):
            datatuple = (
                ('Change made by %s to %s %s death notice' % (self.funeral_home.funeralhomeprofile.full_name, self.first_name, self.last_name), message_email, from_email, to_email),
            )
        else:
            # a new Death_notice
            datatuple = (
                ('Death notice created by %s for %s %s' % (self.funeral_home.funeralhomeprofile.full_name, self.first_name, self.last_name), message_email, from_email, to_email),
            )
        send_mass_mail(datatuple)
        super(Death_notice, self).save()

class Service(models.Model):
    SERVICES = (
        ('visitation', 'visitation',),
        ('visitation followed by a funeral', 'visitation followed by a funeral',),
        ('celebration of life', 'celebration of life',),
        ('funeral', 'funeral',),
        ('funeral Mass', 'funeral Mass',),
        ('memorial service', 'memorial service',),
        ('military graveside funeral', 'military graveside funeral',),
    )
    
    death_notice = models.OneToOneField(Death_notice, blank=True)
    service = models.CharField(choices=SERVICES, max_length=65)
    service_date_time = models.DateTimeField()
    service_location = models.CharField(max_length=75)
    service_city = models.CharField(max_length=80, blank=True)
    
    def __unicode__(self):
        return self.service

class Obituary(models.Model):
    GENDERS =  (
        ('M', 'M',),
        ('F', 'F',),
    )
    
    def obit_file_name(instance, filename):
        (orig_name, orig_ext) = path.splitext(filename)
        return 'obit_images/ob.%s.%s%s' % (instance.death_notice.last_name.lower(), instance.death_notice.first_name.lower(), orig_ext)
    
    death_notice = models.OneToOneField(Death_notice, primary_key=True)
    cause_of_death = models.CharField(max_length=75)
    service_planned = models.BooleanField(u'No service planned?', blank=True, help_text=u'Check if NO SERVICE IS PLANNED.')
    gender = models.CharField(choices=GENDERS, max_length=1)
    date_of_birth = models.DateField(help_text=u'YYYY-MM-DD format')
    place_of_birth = models.CharField(max_length=75)
    parents_names = models.CharField(max_length=75, blank=True)
    education = models.CharField(max_length=256, blank=True)
    military_service = models.TextField(blank=True, help_text=u'Use complete sentences.')
    career_work_experience = models.TextField(blank=True, help_text=u'Use complete sentences.')
    life_domestic_partner = models.CharField(max_length=256, blank=True, help_text=u'Synonymous with spouse')
    length_of_relationship = models.CharField(max_length=12, blank=True)
    memorial_contributions = models.CharField(max_length=256, blank=True)
    family_contact = models.CharField(max_length=126)
    family_contact_phone = models.CharField(max_length=12)
    photo = models.ImageField(upload_to=obit_file_name, blank=True)
    # Survivors
    parents = models.CharField(max_length=255, blank=True, help_text=u'If living')
    grandparents = models.CharField(max_length=255, blank=True, help_text=u'If living')
    number_of_grandchildren = models.IntegerField(blank=True, null=True)
    number_of_great_grandchildren = models.IntegerField(blank=True, null=True)
    number_of_great_great_grandchildren = models.IntegerField(blank=True, null=True)
    preceded_in_death_by = models.TextField(blank=True, help_text=u'Limited to spouses, children, grandchildren. Use complete sentences.')
    rememberances = models.CharField(u'Rememberances to:', max_length=255, blank=True)
    
    obituary_has_run = models.BooleanField()
    obituary_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Obituary'
        verbose_name_plural = 'obituaries'
    
    def __unicode__(self):
        return u'Obituary for %s %s' % (self.death_notice.first_name, self.death_notice.last_name)
    
    def save(self):
        from_email = 'rgnews.registerguard.@gmail.com'
        to_email = ['john.heasly@registerguard.com']
        message_email = 'Go to the obituary admin page for further information.'
        
        if(self.pk):
            datatuple = (
                ('Change made to %s %s obituary' % (self.death_notice.first_name, self.death_notice.last_name), message_email, from_email, to_email),
            )
        else:
            # a new Death_notice
            datatuple = (
                ('Obituary created for %s %s' % (self.death_notice.first_name, self.death_notice.last_name), message_email, from_email, to_email),
            )
        send_mass_mail(datatuple)
        super(Obituary, self).save()
    
    def photo_file_name(self):
        if self.photo:
            return path.basename(self.photo.name)

class Marriage(models.Model):
    obituary =  models.ForeignKey(Obituary)
    married = models.CharField(max_length=126, blank=True)
    marriage_date = models.DateField(blank=True, null=True, help_text=u'YYYY-MM-DD format')
    marriage_location = models.CharField(max_length=126, blank=True)
    spouse_death = models.CharField(max_length=128, blank=True, null=True, help_text=u'\'Previously\' or year, or complete date, if known')

class Visitation(models.Model):
    obituary = models.OneToOneField(Obituary)
    description = models.CharField(max_length=256)
    visitation_date_time = models.DateTimeField()
    visitation_location = models.CharField(max_length=126)
    
    class Meta:
        verbose_name = 'Visitation'
    
    def __unicode__(self):
        return self.description

class BEI(models.Model):
    BEI= (
        ('burial', 'burial',),
        ('entombment', 'entombment',),
        ('inurnment', 'inurnment',),
    )
    
    obituary = models.OneToOneField(Obituary)
    bei = models.CharField(u'burial, entombment or inurnment', choices=BEI, max_length=10)
    bei_date_time = models.DateTimeField(u'burial, entombment or inurnment date and time', blank=True, null=True)
    bei_location = models.CharField(u'burial, entombment or inurnment location', max_length=126)
    
    class Meta:
        verbose_name = 'Burial, entombment or inurnment'
    
    def __unicode__(self):
        return self.bei

class Other_services(models.Model):
    obituary = models.OneToOneField(Obituary)
    description = models.CharField(max_length=256)
    other_services_date_time = models.DateTimeField()
    other_services_location = models.CharField(max_length=126)
    
    class Meta:
         verbose_name = 'Other services'
    
    def __unicode__(self):
        return self.description

class Children(models.Model):
    CHILD_GENDER = (
        ('daughter', 'daughter',),
        ('son',      'son',),
        ('stepdaughter', 'stepdaughter',),
        ('stepson', 'stepson',),
    )
    
    obituary = models.ForeignKey(Obituary)
    gender = models.CharField(choices=CHILD_GENDER, max_length=12, blank=True, null=True)
    name = models.CharField(max_length=126)
    residence = models.CharField(max_length=126, blank=True)
    
    class Meta:
        verbose_name = 'Surviving children'
        verbose_name_plural = 'Surviving children'
    
    def __unicode__(self):
        return '%s %s' % (self.gender ,self.name)

class Siblings(models.Model):
    SIBLING_GENDER = (
        ('brother', 'brother',),
        ('sister', 'sister',),
    )
    
    obituary = models.ForeignKey(Obituary)
    gender = models.CharField(choices=SIBLING_GENDER, max_length=8, blank=True, null=True)
    name = models.CharField(max_length=126)
    residence = models.CharField(max_length=126, blank=True)
    
    class Meta:
        verbose_name = 'Surviving siblings'
        verbose_name_plural = 'Surviving siblings'
    
    def __unicode__(self):
        return '%s %s' % (self.gender, self.name )
