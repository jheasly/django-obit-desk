# -*- coding: utf-8 -*-

from django.core.mail import send_mail, send_mass_mail
from django.db import models
from django.template.defaultfilters import date
from os import path

# Create your models here.

class baseOtherServices(models.Model):
    '''
    Abstract base class for both Death Notice and Obituary.
    '''
    description = models.CharField(max_length=256)
    other_services_date_time = models.DateTimeField()
    other_services_location = models.CharField(max_length=126)
    
    class Meta:
        abstract = True
        verbose_name = 'Other services'
        verbose_name_plural = 'Other services'
    
    def __unicode__(self):
        return self.description

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
    middle_name = models.CharField(u'Middle name or initial', max_length=95, blank=True)
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
        ordering = ('-death_notice_created',)
    
    def __unicode__(self):
        return u'Death notice for %s %s' % (self.first_name, self.last_name)
    
    def save(self):
        from_email = 'rgnews.registerguard.@gmail.com'
        to_email = ['john.heasly@registerguard.com']
        message_email = 'Go to the death notice admin page for further information.'
        
        if(self.id):
            datatuple = None
#             datatuple = (
#                 ('Change made by %s to %s %s death notice' % (self.funeral_home.funeralhomeprofile.full_name, self.first_name, self.last_name), message_email, from_email, to_email),
#             )
        else:
            # a new Death_notice
            datatuple = (
                ('Death notice created by %s for %s %s' % (self.funeral_home.funeralhomeprofile.full_name, self.first_name, self.last_name), message_email, from_email, to_email),
            )
        send_mass_mail(datatuple)
        super(Death_notice, self).save()

class Service(models.Model):
    SERVICES = (
        ('A visitation', 'visitation',),
        ('A visitation followed by a funeral', 'visitation followed by a funeral',),
        ('A celebration of life', 'celebration of life',),
        ('The funeral', 'funeral',),
        ('The funeral Mass', 'funeral Mass',),
        ('A graveside service', 'graveside service',),
        ('A memorial service', 'memorial service',),
        ('A memorial service is planned', 'memorial service is planned',),
        ('A military graveside funeral', 'military graveside funeral',),
    )
    
    death_notice = models.OneToOneField(Death_notice, blank=True, null=True)
    service = models.CharField(choices=SERVICES, max_length=65)
    service_date_time = models.DateTimeField()
    service_location = models.CharField(max_length=75)
    service_city = models.CharField(max_length=80, blank=True)
    
    class Meta:
        ordering = ('-service_date_time',)
    
    def __unicode__(self):
        return self.service
    
    def full_description(self):
        if self.service_extra_info:
            return u'%s %s' % (self.service, self.service_extra_info)
        else:
            return u'%s' % (self.service)

class DeathNoticeOtherServices(baseOtherServices):
    death_notice = models.OneToOneField(Death_notice)

class Obituary(models.Model):
    STATUS = (
        ('live','Live',),
        ('drft','Draft',),
        ('hidn','Hidden',),
    )
    
    GENDERS =  (
        ('M', 'M',),
        ('F', 'F',),
    )
    
    COPIES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
    )
    
    def obit_file_name(instance, filename):
        (orig_name, orig_ext) = path.splitext(filename)
        return 'obit_images/ob.%s.%s%s' % (instance.death_notice.last_name.lower(), instance.death_notice.first_name.lower(), orig_ext)
    
    death_notice = models.OneToOneField(Death_notice, primary_key=True)
    cause_of_death = models.CharField(max_length=75, blank=True, help_text=u'Leave blank if family chooses not to list cause of death.')
    no_service_planned = models.BooleanField(u'No service planned?', blank=True, help_text=u'Check if NO SERVICE IS PLANNED.')
    service_plans_indefinite = models.CharField(u'Service planned, no specifics yet', max_length=300, blank=True, help_text=u'If a Service is planned, but exact date, time, place are not known or it is private, use this field, i.e., "A service is planned in Oakridge." or "A service is planned for February." or "A private memorial service is planned." (If specifcs are known, use Service section of Death Notice form.)')
    gender = models.CharField(choices=GENDERS, max_length=1)
    date_of_birth = models.DateField(help_text=u'YYYY-MM-DD format')
    place_of_birth = models.CharField(max_length=75, help_text=u'City, State')
    parents_names = models.CharField(max_length=75, blank=True)
    education = models.TextField(blank=True, help_text=u'Use complete sentences.')
    military_service = models.TextField(blank=True, help_text=u'Use complete sentences.')
    career_work_experience = models.TextField(blank=True, help_text=u'Use complete sentences.')
    life_domestic_partner = models.CharField(max_length=256, blank=True, help_text=u'Synonymous with spouse')
    length_of_relationship = models.CharField(max_length=12, blank=True)
    remembrances = models.CharField(u'Remembrances to:', max_length=255, blank=True)
    family_contact = models.CharField(max_length=126)
    family_contact_phone = models.CharField(max_length=12)
    mailing_address = models.TextField(blank=True, help_text=u'Please include a mailing address in the space below if you would like to receive up to 10 copies of this obituary.')
    number_of_copies = models.IntegerField(choices=COPIES, blank=True, null=True, help_text=u'Number of copies you would like.', default=10)
    photo = models.ImageField(upload_to=obit_file_name, blank=True)
    # Survivors
    parents = models.CharField(u'Surviving parents', max_length=255, blank=True, help_text=u'If living, i.e., \'mother,\' \'father\' or \'parents\' with hometown, if changed from place of birth, \'mother, now of Oneonta, N.Y.\'')
    grandparents = models.CharField(u'Surviving grandparents', max_length=255, blank=True, help_text=u'If living')
    number_of_grandchildren = models.IntegerField(u'Number of surviving grandchildren', blank=True, null=True)
    number_of_step_grandchildren = models.IntegerField(u'Number of surviving step grandchildren', blank=True, null=True)
    number_of_great_grandchildren = models.CharField(u'Number of surviving great-grandchildren', max_length=75, blank=True)
    number_of_step_great_grandchildren = models.CharField(u'Number of surviving step great-grandchildren', max_length=75, blank=True)
    number_of_great_great_grandchildren = models.CharField(u'Number of surviving great-great-grandchildren', max_length=75, blank=True)
    number_of_step_great_great_grandchildren = models.CharField(u'Number of surviving step great-great-grandchildren', max_length=75, blank=True)
    preceded_in_death_by = models.TextField(blank=True, help_text=u'Limited to spouses, children, grandchildren. Use complete sentences.')
    status = models.CharField(max_length=4, choices=STATUS, default='live')
    
    obituary_in_system = models.BooleanField(u'Obituary in DT system')
    obituary_has_run = models.BooleanField()
    obituary_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Obituary'
        verbose_name_plural = 'obituaries'
        ordering = ('-obituary_created',)
    
    def __unicode__(self):
        return u'Obituary for %s %s' % (self.death_notice.first_name, self.death_notice.last_name)
    
    def save(self):
        from_email = 'rgnews.registerguard.@gmail.com'
        to_email = ['john.heasly@registerguard.com', 'lisa.crossley@registerguard.com', 'jheasly@earthlink.net']
        message_email = 'Go to the obituary admin page for further information.'
        
        if(self.pk):
            datatuple = None
#             datatuple = (
#                 ('Change made to %s %s obituary' % (self.death_notice.first_name, self.death_notice.last_name), message_email, from_email, to_email),
#             )
        else:
            # a new Death_notice
            datatuple = (
                ('Obituary created for %s %s' % (self.death_notice.first_name, self.death_notice.last_name), message_email, from_email, to_email),
            )
        if datatuple:
            send_mass_mail(datatuple)
        super(Obituary, self).save()
    
    ##
    ## MODEL ATTRIBUTES FOR THE OBITUARY ADMIN
    ##
    def photo_file_name(self):
        if self.photo:
            return path.basename(self.photo.name)
    
    def service_date(self):
        try:
            self.death_notice.service
            if self.death_notice.service.service_date_time:
                return u'%s' % date(self.death_notice.service.service_date_time, "P l, N j,")
        except Service.DoesNotExist:
            return u'No service scheduled.'
    
    ##
    ## MODE ATTRIBUTES FOR OBITUARY TEMPLATING
    ##
    def pronoun(self):
        if self.gender == 'F':
            return u'She'
        else:
            return u'He'
    
    def intro(self):
        '''
        Navigates all the permutations of the first paragraph.
        '''
        ##
        ## DATELINE
        ##
        local_cities = (
            'Eugene',
            'Springfield',
        )
        if self.death_notice.city_of_residence not in local_cities:
            dateline =  u'%s — ' % self.death_notice.city_of_residence.upper()
        else:
            dateline = u''
        
        ##
        ## CITY
        ##
        if self.death_notice.formerly_of:
            city = u'%s, formerly of %s' % (self.death_notice.city_of_residence.strip(), self.death_notice.formerly_of.strip())
        else:
            city = self.death_notice.city_of_residence.strip()
        
        ##
        ## NAME
        ##
        if self.death_notice.nickname:
            nickname = '"%s"' % self.death_notice.nickname
        else:
            nickname = self.death_notice.nickname
        name_list = ([self.death_notice.first_name, 
            self.death_notice.middle_name, 
            nickname, 
            self.death_notice.last_name])
        
        # get rid of empty elements
        vetted_list = filter(lambda x : x, name_list)
        full_name = ' '.join(vetted_list)
        
        ##
        ## NO_SERVICE_PLANNED // SERVICE PLANS INDEFINITE
        ##
        if self.no_service_planned:
            no_service_indefinite = u' No service is planned.'
        else:
            if self.service_plans_indefinite:
                no_service_indefinite = u' %s' % self.service_plans_indefinite
            else:
                no_service_indefinite = u''
        
        ##
        ## DEATH // AGE // CAUSE
        ##
        if self.cause_of_death:
            date_age_cause = u'died %s of %s. %s was %s.' % (
                date(self.death_notice.death_date, "N j"),
                self.cause_of_death.strip(),
                self.pronoun(),
                self.death_notice.age,
            )
        else:
            date_age_cause = u'died %s at age %s. The family chose not to list the cause of death.' % (
                date(self.death_notice.death_date, "N j"),
                self.death_notice.age,
            )
        
        ##
        ## SERVICE INTRO
        ##
        try:
            self.death_notice.service
            
            if self.death_notice.service.service:
                if self.death_notice.service.service.lower().count('mass'):
                    celebrated = u'celebrated'
                else:
                    celebrated = u'held'
                
                service = u'%s will be %s at %s at %s in %s, for %s of %s, %s' % (
                    self.death_notice.service.service.strip(), 
                    celebrated, 
                    date(self.death_notice.service.service_date_time, "P l, N j,"),
                    self.death_notice.service.service_location.strip(),
                    self.death_notice.service.service_city.strip(),
                    full_name, 
                    city,
                    u'who ' + date_age_cause,
                )
        except Service.DoesNotExist:
            service = u'%s of %s %s' % (
                full_name, 
                self.death_notice.city_of_residence,
                date_age_cause,
            )
            
        return dateline + service + no_service_indefinite
    
    ##
    ## MARRIAGE
    ##
    
    def marriage(self):
        if self.marriage_set.all():
            marriage_str = u'%s married %s' % (
                self.pronoun(), 
                ', '.join([', '.join((wedding.married, wedding.marriage_date, wedding.marriage_location, wedding.spouse_death)) for wedding in self.marriage_set.all()]),
            )
        else:
            marriage_str = u''
        return marriage_str
    
    ##
    ## SURVIVORS
    ##
    def surviving_siblings(self):
        brother_list = []
        sister_list = []
        if self.siblings_set.all():
            brother_set = self.siblings_set.filter(gender='brother')
            sister_set = self.siblings_set.filter(gender='sister')
            if brother_set:
                for brother in brother_set:
                    brother_list.append(u'%s of %s' % (brother.name, brother.residence))
                    brother_str = ', '.join(brother_list)
                brothers = u'%s brothers, %s' % (len(brother_set), brother_str)
            else:
                brothers = u''
            if sister_set:
                for sister in sister_set:
                    sister_list.append(u'%s of %s' % (sister.name, sister.residence))
                    sister_str = ', '.join(sister_list)
                sisters = u'%s sisters, %s' % (len(sister_set), sister_str)
            else:
                sisters = u''
            return u'%s; %s' % (brothers, sisters)
        else:
            return u''

class Marriage(models.Model):
    obituary =  models.ForeignKey(Obituary)
    married = models.CharField(max_length=126, blank=True, help_text=u'Enter spouse\'s name.')
    marriage_date = models.CharField(max_length=32, blank=True, help_text=u'YYYY-MM-DD format')
    marriage_location = models.CharField(max_length=126, blank=True)
    spouse_death = models.CharField(max_length=128, blank=True, null=True, help_text=u'\'Previously\' or year, or complete date of death, if known. If they divorced, fill in year and date, if known.')
    
    class Meta:
        ordering = ('marriage_date', 'id',)

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

class Other_services(baseOtherServices):
    obituary = models.OneToOneField(Obituary)

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
    name = models.CharField(max_length=126, help_text=u'First and last, no middle initial')
    residence = models.CharField(max_length=126, blank=True, help_text=u'City and state')
    
    class Meta:
        verbose_name = 'Surviving siblings'
        verbose_name_plural = 'Surviving siblings'
    
    def __unicode__(self):
        return '%s %s' % (self.gender, self.name )
