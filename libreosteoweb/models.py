from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS
from datetime import date, datetime
from .api.filter import get_name_filters


# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class RegularDoctor(models.Model):
        """
        This class implements bean object to represent
        regular doctor for a patient

        It describes fields into this object which are mapped into DB
        """
        family_name = models.CharField(_('Family name'), max_length=200)
        first_name = models.CharField(_('Firstname'), max_length=200)
        phone = models.CharField(_('Phone'), max_length=100, blank=True,null=True)
        city = models.CharField(_('City'), max_length=200, blank=True)

        def __unicode__(self):
                return "%s %s" % (self.family_name, self.first_name)


class Patient(models.Model):
        """
        This class implements bean object to represent
        patient.
        """
        family_name = models.CharField(_('Family name'), max_length=200 )
        original_name = models.CharField(_('Original name'), max_length=200, blank=True)
        first_name = models.CharField(_('Firstname'), max_length=200, blank=True )
        birth_date = models.DateField(_('Birth date'))
        address_street = models.CharField(_('Street'), max_length=500, blank=True)
        address_complement = models.CharField(_('Address complement'), max_length=500, blank=True)
        address_zipcode = models.CharField(_('Zipcode'), max_length=200, blank=True)
        address_city = models.CharField(_('City'), max_length=200, blank=True)
        phone = models.CharField(_('Phone'), max_length=200, blank=True)
        mobile_phone = models.CharField(_('Mobile phone'), max_length=200, blank=True)
        job = models.CharField(_('Job'), max_length=200, blank=True, default="")
        hobbies = models.TextField(_('Hobbies'), blank=True, default="")
        #family_situation = Column(Integer)
        doctor = models.ForeignKey(RegularDoctor, verbose_name=_('Regular doctor'), blank=True, null=True)
        smoker = models.BooleanField(_('Smoker'), default=False)
        important_info = models.TextField(_('Important note'), blank=True)
        surgical_history = models.TextField(_('Surgical history'), blank=True)
        medical_history = models.TextField(_('Medical history'), blank=True)
        family_history = models.TextField(_('Family history'), blank=True)
        trauma_history = models.TextField(_('Trauma history'), blank=True)
        medical_reports = models.TextField(_('Medical reports'), blank=True)
        creation_date = models.DateField(_('Creation date'), blank=True, null=True, editable=False)
        sex = models.CharField(_('Sex'), max_length=1, choices=(('M', _('Male')), ('F', _('Female'))), blank=True, null=True)

        #Not mapped field, only for traceability purpose
        current_user_operation = None

        def __unicode__(self):
                return "%s %s by %s" % (self.family_name, self.first_name, self.current_user_operation)

        def clean(self):
            if self.creation_date is None:
                self.creation_date = date.today()
            self.family_name = get_name_filters().filter(self.family_name)
            self.original_name = get_name_filters().filter(self.original_name)
            self.first_name = get_name_filters().filter(self.first_name)

        def set_user_operation(self, user):
            """ Use this setting method to define the user
            which performs the operation (create, update).
            Not mapped in DB only for the runtime"""
            self.current_user_operation = user


        TYPE_NEW_PATIENT = 1
        TYPE_UPDATE_PATIENT = 2


class Children(models.Model):
        """
        This class implements bean object to represent
        children of a patient.
        """
        family_name = models.CharField(_('Family name'), max_length=200, blank=True)
        first_name = models.CharField(_('Firstname'), max_length=200)
        birthday_date = models.DateField(_('Birth date'))
        parent = models.ForeignKey(Patient, verbose_name=_('Parent'))

        def __unicode__(self):
                return "%s %s" % (self.family_name, self.first_name)

class Examination(models.Model):
    """
    This class implements bean object to represent
    examination on a patient
    """
    reason = models.TextField(_('Reason'), blank=True)
    reason_description = models.TextField(_('Reason description/Context'), blank=True)
    orl = models.TextField(_('ORL Sphere'), blank=True)
    visceral = models.TextField(_('Visceral Sphere'), blank=True)
    pulmo = models.TextField(_('Cardio-Pulmo Sphere'), blank=True)
    uro_gyneco = models.TextField(_('Uro-gyneco Sphere'), blank=True)
    periphery = models.TextField(_('Periphery Sphere'), blank=True)
    general_state = models.TextField(_('General state'), blank=True)
    medical_examination = models.TextField(_('Medical examination'), blank=True)
    diagnosis = models.TextField(_('Diagnosis'), blank=True)
    treatments = models.TextField(_('Treatments'), blank=True)
    conclusion = models.TextField(_('Conclusion'), blank=True)
    date = models.DateTimeField(_('Date'))
    # Status : 0 -> in progress
    # Status : 1 -> invoiced not paid
    # Status : 2 -> invoiced and paid
    # Status : 3 -> not invoiced
    status = models.SmallIntegerField(_('Status'))
    status_reason = models.TextField(_('Status reason'), blank=True, null=True)
    # Type : 1 -> normal examination
    # Type : 2 -> continuation of the examination
    # Type : 3 -> return of a previous examination
    # Type : 4 -> emergency examination
    type = models.SmallIntegerField(_('Type'))
    invoice = models.OneToOneField('Invoice', verbose_name=_('Invoice'), blank=True, null=True)
    patient = models.ForeignKey(Patient, verbose_name=_('Patient'))
    therapeut = models.ForeignKey(User, verbose_name=_('Therapeut'), blank=True,null=True)

    EXAMINATION_IN_PROGRESS = 0
    EXAMINATION_WAITING_FOR_PAIEMENT = 1
    EXAMINATION_INVOICED_PAID = 2
    EXAMINATION_NOT_INVOICED = 3

    # i18n
    TYPE_NORMAL_EXAMINATION_I18N = _('Normal examination')
    TYPE_CONTINUING_EXAMINATION_I18N = _('Continuing examination')
    TYPE_RETURN_I18N = _('Return')
    TYPE_EMERGENCY_I18N = _('Emergency')

    def __unicode__(self):
        return "%s %s" % (self.patient, self.date)

class ExaminationComment(models.Model):
    """This class represents a comment on examination
    """
    user = models.ForeignKey(User, verbose_name=_('User'), blank=True, null=True)
    comment = models.TextField(_('Comment'))
    date = models.DateTimeField(_('Date'), null=True, blank=True)
    examination = models.ForeignKey(Examination, verbose_name=_('Examination'))



class Invoice(models.Model):
    """
    This class implements bean object to represent
    invoice on an examination
    """
    date = models.DateTimeField(_('Date'))
    amount = models.FloatField(_('Amount'))
    currency = models.CharField(_('Currency'), max_length=10)
    paiment_mode = models.CharField(_('Paiment mode'), max_length=10)
    header = models.TextField(_('Header'),blank=True)
    therapeut_name = models.TextField(_('Therapeut name'))
    therapeut_first_name = models.TextField(_('Therapeut firstname'))
    quality = models.TextField(_('Quality'), blank=True)
    adeli = models.TextField(_('Adeli'))
    location = models.TextField(_('Location'))
    number = models.TextField(_('Number'))
    patient_family_name = models.CharField(_('Family name'), max_length=200 )
    patient_original_name = models.CharField(_('Original name'), max_length=200, blank=True)
    patient_first_name = models.CharField(_('Firstname'), max_length=200, blank=True )
    patient_address_street = models.CharField(_('Street'), max_length=500, blank=True)
    patient_address_complement = models.CharField(_('Address complement'), max_length=500, blank=True)
    patient_address_zipcode = models.CharField(_('Zipcode'), max_length=200, blank=True)
    patient_address_city = models.CharField(_('City'), max_length=200, blank=True)
    content_invoice = models.TextField(_('Content'), blank=True)
    footer = models.TextField(_('Footer'), blank=True)
    office_siret = models.TextField(_('Siret'), blank=True)
    office_address_street = models.CharField(_('Street'),max_length=500, blank=True, default='')
    office_address_complement = models.CharField(_('Address complement'),max_length=500, blank=True, default='')
    office_address_zipcode = models.CharField(_('Zipcode'), max_length=200, blank=True, default='')
    office_address_city = models.CharField(_('City'), max_length=200, blank=True, default='')
    office_phone = models.CharField(_('Phone'), max_length=200, blank=True, default='')

    def clean(self):
        if self.date is None:
            self.date = datetime.today()

class OfficeEvent(models.Model):
    """
    This class implements bean object to represent
    event on the office
    """
    date = models.DateTimeField(_('Date'), blank=True)
    clazz = models.TextField(_('Class'), blank=True)
    type = models.SmallIntegerField(_('Type'))
    comment = models.TextField(_('Comment'), blank=True)
    reference = models.IntegerField(_('Reference'), blank=True, null=False)
    user = models.ForeignKey(User, verbose_name=_('user'), blank=True,null=False)

    def clean(self):
        if self.date is None:
            self.date = datetime.today()

class OfficeSettings(models.Model):
    """
    This class implements model for the settings into the application
    """
    invoice_office_header = models.CharField(_('Invoice office header'), max_length=500, blank=True)
    office_address_street = models.CharField(_('Street'),max_length=500, blank=True)
    office_address_complement = models.CharField(_('Address complement'),max_length=500, blank=True)
    office_address_zipcode = models.CharField(_('Zipcode'), max_length=200, blank=True)
    office_address_city = models.CharField(_('City'), max_length=200, blank=True)
    office_phone = models.CharField(_('Phone'), max_length=200, blank=True)
    office_siret = models.CharField(_('Siret'), max_length=20)
    amount = models.FloatField(_('Amount'), blank=True, null=True, default=None)
    currency = models.CharField(_('Currency'), max_length=10)
    invoice_content = models.TextField(_('Invoice content'), blank=True)
    invoice_footer = models.TextField(_('Invoice footer'), blank=True)
    invoice_start_sequence = models.TextField(_('Invoice start sequence'), blank=True)    

    def save(self, *args, **kwargs):
        """
        Ensure that only one instance exists in the db
        """
        self.id = 1
        super(OfficeSettings, self).save()



class TherapeutSettings(models.Model):
    """
    This class implements model for extending the User model
    """
    adeli = models.TextField(_('Adeli'),blank=True)
    quality = models.TextField(_('Quality'), blank=True)
    user = models.OneToOneField(User, verbose_name=_('User'),   blank=True,null=True)