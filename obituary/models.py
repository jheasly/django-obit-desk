# -*- coding: utf-8 -*-

from django.core.mail import send_mail, send_mass_mail
from django.db import models
from django.contrib.humanize.templatetags.humanize import apnumber
from django.template.defaultfilters import date
from sorl.thumbnail import get_thumbnail, ImageField
from os import path
import datetime

# Create your models here.

DN_OBIT_EMAIL_RECIPIENTS = [
    'john.heasly@registerguard.com', 
    'lisa.crossley@registerguard.com', 
    'jheasly@earthlink.net',
]

class baseOtherServices(models.Model):
    '''
    Abstract base class for both Death Notice and Obituary.
    '''
    description = models.CharField(u'Description of other service', max_length=256)
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
        (2, 'months',),
        (3, 'days',),
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
        to_email = DN_OBIT_EMAIL_RECIPIENTS
        message_email = 'Go to the death notice admin page for further information.'
        
        if(self.id):
            datatuple = None
#             datatuple = (
#                 ('Change made by %s to %s %s death notice' % (self.funeral_home.funeralhomeprofile.full_name, self.first_name, self.last_name), message_email, from_email, to_email),
#             )
        else:
            # a new Death_notice
            message_subj = 'Death notice created by %s for %s %s' % (self.funeral_home.funeralhomeprofile.full_name, self.first_name, self.last_name)
            datatuple = (message_subj, message_email, from_email, to_email,), # <- This trailing comma's vital!
        
        if datatuple:
            send_mass_mail(datatuple)
        super(Death_notice, self).save()
    
    def last_name_no_suffix(self):
        suffixes = (' jr', ' sr', ' ii', ' iii')
        shortened_name = self.last_name
        for suffix in suffixes:
            if self.last_name.lower().count(suffix):
                offset = self.last_name.lower().find(suffix)
                shortened_name = self.last_name[:offset]
                break
        return shortened_name

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
#     description = models.CharField(max_length=256)
#     other_services_date_time = models.CharField(max_length=150, blank=True, help_text=u'YYYY-MM-DD format')
#     other_services_location = models.CharField(max_length=126, blank=True)

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
#         return 'obit_images/ob.%s.%s%s' % (instance.death_notice.last_name.lower(), instance.death_notice.first_name.lower(), orig_ext)
        return 'obits/%s/%s/ob.%s.%s%s' % (datetime.date.today().year, datetime.date.today().month, instance.death_notice.last_name.lower(), instance.death_notice.first_name.lower(), orig_ext)
    
    death_notice = models.OneToOneField(Death_notice, primary_key=True)
    cause_of_death = models.CharField(u'Died of ... ', max_length=75, blank=True, help_text=u'Leave blank if family chooses not to list cause of death.')
    no_service_planned = models.BooleanField(u'No service planned?', blank=True, help_text=u'Check if NO SERVICE IS PLANNED.')
    service_plans_indefinite = models.CharField(u'Service planned, no specifics yet', max_length=300, blank=True, help_text=u'If a Service is planned, but exact date, time, place are not known or it is private, use this field, i.e., "A service is planned in Oakridge." or "A service is planned for February." or "A private memorial service is planned." (If specifics are known, use Service section of Death Notice form.)')
    gender = models.CharField(choices=GENDERS, max_length=1)
    date_of_birth = models.DateField(help_text=u'YYYY-MM-DD format')
    place_of_birth = models.CharField(max_length=75, help_text=u'City, State')
    parents_names = models.CharField(u'Parents\' names', max_length=75, blank=True, help_text=u'Use this format: "[Father\'s first name] and [Mother\'s first name] [Mother\'s maiden name] [Married last name]" e.g.: Thomas and Bernice Davis Baker')
    education = models.TextField(blank=True, help_text=u'Use complete sentences.')
    military_service = models.TextField(blank=True, help_text=u'Use complete sentences.')
    career_work_experience = models.TextField(blank=True, help_text=u'Use complete sentences.')
    remembrances = models.CharField(u'Remembrances to ... ', max_length=255, blank=True)
    family_contact = models.CharField(max_length=126)
    family_contact_phone = models.CharField(max_length=12)
    mailing_address = models.TextField(blank=True, help_text=u'Please include a mailing address in the space below if you would like to receive up to 10 copies of this obituary.')
    number_of_copies = models.IntegerField(choices=COPIES, blank=True, null=True, help_text=u'Number of copies you would like.', default=10)
    photo = ImageField(upload_to=obit_file_name, blank=True)
    # Survivors
    life_domestic_partner = models.CharField(max_length=256, blank=True, help_text=u'Synonymous with spouse')
    length_of_relationship = models.CharField(max_length=12, blank=True)
    spouse = models.CharField(max_length=255, blank=True, help_text=u'Life/domestic partner')
    parents = models.CharField(max_length=255, blank=True, help_text=u'If living, i.e., \'mother,\' \'father\' or \'parents\' with hometown, if changed from place of birth, \'mother, now of Oneonta, N.Y.\'')
    grandparents = models.CharField(max_length=255, blank=True, help_text=u'If living')
    number_of_grandchildren = models.IntegerField(u'Number of grandchildren', blank=True, null=True)
    number_of_step_grandchildren = models.IntegerField(u'Number of step grandchildren', blank=True, null=True)
    number_of_great_grandchildren = models.CharField(u'Number of great-grandchildren', max_length=75, blank=True)
    number_of_step_great_grandchildren = models.CharField(u'Number of step great-grandchildren', max_length=75, blank=True)
    number_of_great_great_grandchildren = models.CharField(u'Number of great-great-grandchildren', max_length=75, blank=True)
    number_of_step_great_great_grandchildren = models.CharField(u'Number of step great-great-grandchildren', max_length=75, blank=True)
    preceded_in_death_by = models.TextField(u'Preceded in death by ... ', blank=True, help_text=u'Limited to spouses, children, grandchildren. Use complete sentences.')
    anything_else = models.TextField(u'Anything else we should know?', blank=True)
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
        to_email = DN_OBIT_EMAIL_RECIPIENTS
        message_email = 'Go to the obituary admin page for further information.'
        
        if(self.pk):
            datatuple = None
#             datatuple = (
#                 ('Change made to %s %s obituary' % (self.death_notice.first_name, self.death_notice.last_name), message_email, from_email, to_email),
#             )
        else:
            # a new Death_notice
            message_subj = 'Obituary created for %s %s' % (self.death_notice.first_name, self.death_notice.last_name)
            datatuple = (message_subj,  message_email, from_email, to_email,), # <- This trailing comma's vital!
        if datatuple:
            send_mass_mail(datatuple)
        super(Obituary, self).save()
    
    def admin_thumbnail(self):
        if self.photo:
            im = get_thumbnail(self.photo, '60')
            return u'<img src="%s" width="60" alt="%s %s" />' % (im.url, self.death_notice.first_name, self.death_notice.last_name)
        else:
            return u'(No photo)'
    admin_thumbnail.short_description = u'Thumbnail'
    admin_thumbnail.allow_tags = True
    
    ##
    ## MODEL ATTRIBUTES FOR THE OBITUARY ADMIN
    ##
    def display_photo_file_name(self):
        if self.photo:
            return self.photo.name
        else:
            return u'(No photo)'
    display_photo_file_name.short_description = u'File path'
    
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
            service = u'%s of %s, %s' % (
                full_name, 
                city,
                date_age_cause,
            )
            
        return dateline + service + no_service_indefinite
    
    ##
    ## MARRIAGE
    ##
    
    def date_or_what(self, wed_date_str):
        '''
        Takes a string; if it's in YYYY-MM-DD format, a date object is 
        returned, otherwise the the original string is returned.
        '''
        from datetime import datetime
        try:
            date_obj = datetime.strptime(wed_date_str, '%Y-%m-%d')
            return date_obj
        except (AttributeError, ValueError,):
            return wed_date_str
    
    def other_gender(self, the_one):
        if the_one == 'M':
            return u'she'
        else:
            return u'he'
    
    def marriage(self):
        if self.marriage_set.all():
            wedding_list = []
            for wedding in self.marriage_set.all():
                if self.date_or_what(wedding.marriage_date) and wedding.marriage_location:
                    
                    if isinstance(self.date_or_what(wedding.marriage_date), datetime.datetime):
                        wedding_date_str = date(self.date_or_what(wedding.marriage_date), "N j, Y")
                    else:
                        wedding_date_str = self.date_or_what(wedding.marriage_date)
                    
                    wedding_str = u'%s married %s on %s in %s' % (
                        self.pronoun(), 
                        wedding.married, 
                        wedding_date_str,
#                         date(self.date_or_what(wedding.marriage_date), "N j, Y"), 
                        wedding.marriage_location, 
                    )
                elif not self.date_or_what(wedding.marriage_date) and not wedding.marriage_location:
                    wedding_str = u'%s married %s' % (
                        self.pronoun(), 
                        wedding.married, 
                    )
                
                if wedding.spouse_death:
                    # See if the 'spouse_death" is a date (a death) or a string, something else ... 
                    if isinstance(self.date_or_what(wedding.spouse_death), datetime.datetime):
                        wedding_str += u'. %s died %s' % (
                            self.other_gender(self.gender).capitalize(), 
                            date(self.date_or_what(wedding.spouse_death), "N j, Y"), 
                        )
                    else:
                        wedding_str += u'. %s' % self.date_or_what(wedding.spouse_death)
                wedding_list.append(wedding_str)
            marriage_str = '. '.join(wedding_list)
            if marriage_str[-1] != '.':
                marriage_str += '.'
        else:
            marriage_str = u''
        return marriage_str
    
    ##
    ## SURVIVORS
    ##
    def surviving_sig_ot(self):
        if self.spouse or self.life_domestic_partner:
            if self.gender == 'M':
                sig_ot_str = u' his wife; '
            else:
                sig_ot_str = u' her husband; '
        else:
            sig_ot_str = u''
        
        return sig_ot_str
    
    def surviving_parents(self):
        if self.parents:
            if self.gender == 'M':
                surv_par_str = u'his %s; ' % self.parents
            else:
                surv_par_str = u'her %s; ' % self.parents
        else:
            surv_par_str = u''
        return surv_par_str
    
    def surviving_children(self):
        genders = ('son', 'daughter', 'stepson', 'stepdaughter')
        if self.children_set.all():
            gender_sub_list = []
            for gender in genders:
                child_list = []
                gender_set = self.children_set.filter(gender=gender)
                if gender_set:
                    # build gender-based list
                    for child in gender_set:
                        if child.residence:
                            child_list.append(u'%s of %s' % (child.name, child.residence))
                        else:
                            child_list.append(u'%s' % (child.name))
                    
                    if len(child_list) == 1:
                        child_str = ', '.join(child_list)
                    else:
                        # insert 'and" in front of last item
                        child_list[-1] = u'and ' + child_list[-1]
                        # merge last two items
                        child_list[-2:] = [ ' '.join(child_list[-2:]) ]
                        child_str = ', '.join(child_list)
                    
                    if len(gender_set) == 1:
                        child_str = u'a %s, %s' % (gender, child_str)
                    else:
                        child_str = u' %s %ss, %s' % (apnumber(len(gender_set)), gender, child_str)
                    gender_sub_list.append(child_str)
            child_display = '; '.join(gender_sub_list)
        else:
            child_display = u''
        return child_display
        
    def surviving_siblings(self):
        genders = ('brother', 'sister',)
        if self.children_set.all():
            gender_sub_list = []
            for gender in genders:
                child_list = []
                gender_set = self.siblings_set.filter(gender=gender)
                if gender_set:
                    # build gender-based list
                    for child in gender_set:
                        if child.residence:
                            child_list.append(u'%s of %s' % (child.name, child.residence))
                        else:
                            child_list.append(u'%s' % (child.name))
                    
                    if len(child_list) == 1:
                        child_str = ', '.join(child_list)
                    else:
                        # insert 'and" in front of last item
                        child_list[-1] = u'and ' + child_list[-1]
                        # merge last two items
                        child_list[-2:] = [ ' '.join(child_list[-2:]) ]
                        child_str = ', '.join(child_list)
                    
                    if len(gender_set) == 1:
                        child_str = u'; a %s, %s' % (gender, child_str)
                    else:
                        child_str = u'; %s %ss, %s' % (apnumber(len(gender_set)), gender, child_str)
                    gender_sub_list.append(child_str)
            child_display = '; '.join(gender_sub_list)
        else:
            child_display = u''
        return child_display
    
    def surviving_grands(self):
        grand_list = (
            [self.number_of_grandchildren,                  u'grandchildren',],
            [self.number_of_step_grandchildren,             u'step granchildren',],
            [self.number_of_great_grandchildren,            u'great-grandchildren',],
            [self.number_of_step_great_grandchildren,       u'step great-grandchildren',],
            [self.number_of_great_great_grandchildren,      u'great-great grandchildren',],
            [self.number_of_step_great_great_grandchildren, u'step great-great grandchildren',],
        )
        
        # Eliminate empty 'grands' and make correct grandchildren grandchild when there's only one.
        grand_display_list = []
        for grand in grand_list:
            if grand[0]:
                if grand[0] == u'1':
                    grand[0] = u'a'
                    grand[1] = grand[1][:-3]
                grand_display_list.append((apnumber(grand[0]), grand[1]))
        
        if grand_display_list:
            
            if len(grand_display_list) == 1:                # SINGLE-ITEM grand_display_list: [(u'eight', u'grandchildren')]
                grand_display = u'and %s %s' % grand_display_list[0]
            else:                                           # MULTI grand_display_list: [(14, u'grandchildren'), (14, u'great-grandchildren')]
                grand_display_list = ['%s %s' % grand_display for grand_display in grand_display_list]
                grand_display_list[-1] = u'and ' + grand_display_list[-1]
                grand_display = '; '.join( grand_display_list )
            grand_display = u'; ' + grand_display
        else:
            grand_display = u''
        return grand_display
    
    ##
    ## BURIAL, ENTOMBMENT, INURNMENT
    ##
    def bei_display(self):
        try:
            bei_str = u'<pstyle:BodyText\:BodyText\_No\_BL>%s will be at %s in %s.\n' % ( self.bei.bei.capitalize(), date(self.bei.bei_date_time,"P l, N j,"), self.bei.bei_location)
        except BEI.DoesNotExist:
            bei_str = u''
        return bei_str

class Marriage(models.Model):
    obituary =  models.ForeignKey(Obituary)
    married = models.CharField(max_length=126, blank=True, help_text=u'Enter spouse\'s name.')
    marriage_date = models.CharField(max_length=32, blank=True, help_text=u'If only the year is known, enter the year. If just month and year are known, enter month and year, i.e. \'September 1954\'')
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
        ordering = ('id',)
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
    name = models.CharField(max_length=126, blank=True, help_text=u'First and last, no middle initial')
    residence = models.CharField(max_length=126, blank=True, help_text=u'City and state')
    
    class Meta:
        ordering = ('id',)
        verbose_name = 'Surviving siblings'
        verbose_name_plural = 'Surviving siblings'
    
    def __unicode__(self):
        return '%s %s' % (self.gender, self.name )
