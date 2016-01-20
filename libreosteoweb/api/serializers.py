from rest_framework import serializers, validators
from libreosteoweb.models import Patient, Examination, OfficeEvent, TherapeutSettings, OfficeSettings, ExaminationComment, RegularDoctor
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from datetime import date
from .validators import UniqueTogetherIgnoreCaseValidator


class WithPkMixin(object):
    def get_pk_field(self, model_field):
        return self.get_field(model_field)

def check_birth_date(value):
    if value > date.today():
        raise serializers.ValidationError({
            'birth_date' :
                _('Birth date is invalid')
        })

class PatientSerializer (serializers.ModelSerializer):
    current_user_operation = None
    birth_date = serializers.DateField(label=_('Birth date'), validators=[check_birth_date] )
    class Meta:
        model = Patient
        validators = [
            UniqueTogetherIgnoreCaseValidator(
                queryset=Patient.objects.all(),
                fields=('family_name', 'first_name', 'birth_date'),
                message = _('This patient already exists'),
            )
        ]

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta :
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


    #def restore_object(self, attrs, instance=None):
        # call set_password on user object. Without this
        # the password will be stored in plain text.
        #user = super(UserSerializer, self).restore_object(attrs, instance)
        #if(attrs['password']):
        #    user.set_password(attrs['password'])
        #return user

class RegularDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegularDoctor

class ExaminationExtractSerializer(WithPkMixin, serializers.ModelSerializer):
    therapeut = UserInfoSerializer()
    comments = serializers.SerializerMethodField('get_nb_comments')
    class Meta:
        model = Examination
        fields = ('id', 'reason', 'date', 'status', 'therapeut', 'type', 'comments')
        depth = 1

    def get_nb_comments(self, obj):
        return ExaminationComment.objects.filter(examination__exact=obj.id).count()         

class ExaminationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examination


class CheckSerializer(serializers.Serializer):
    bank = serializers.CharField(required=False, allow_null=True)
    payer = serializers.CharField(required=False, allow_null=True)
    number = serializers.CharField(required=False, allow_null=True)

class ExaminationInvoicingSerializer(serializers.Serializer):
    status = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_null=True)
    paiment_mode = serializers.CharField(required=False, allow_null=True)
    amount = serializers.FloatField(required=False, allow_null=True)
    check = CheckSerializer()

    def validate(self, attrs):
        """
        Check that the invoicing is consistent
        """
        if attrs['status'] == 'notinvoiced':
            if attrs['reason'] is None or len(attrs['reason'].strip()) == 0:
                raise serializers.ValidationError(_("Reason is mandatory when the examination is not invoiced"))
        if attrs['status'] == 'invoiced':
            if attrs['amount'] is None or attrs['amount'] <= 0:
                raise serializers.ValidationError(_("Amount is invalid"))
            if attrs['paiment_mode'] is None or len(attrs['paiment_mode'].strip()) == 0 or attrs['paiment_mode'] not in ['check', 'cash', 'notpaid']:
                raise serializers.ValidationError(_("Paiment mode is mandatory when the examination is invoiced"))
            if attrs['paiment_mode'] == 'check':
                if attrs['check'] is None :
                    raise serializers.ValidationError(_("Check information is missing"))
                #if attrs['check']['bank'] is None or len(attrs['check']['bank'].strip()) == 0:
                #    raise serializers.ValidationError(_("Bank information is missing about the check paiment"))
                #if attrs['check']['payer'] is None or len(attrs['check']['payer'].strip()) == 0:
                #    raise serializers.ValidationError(_("Payer information is missing about the check paiment"))
                #if attrs['check']['number'] is None or len(attrs['check']['number'].strip()) == 0:
                #    raise serializers.ValidationError(_("Number information is missing about the check paiment"))
        return attrs


class ExaminationCommentSerializer(WithPkMixin, serializers.ModelSerializer):
    user_info = UserInfoSerializer(source="user", required=False, read_only=True)
    class Meta:
        model = ExaminationComment

class OfficeEventSerializer(WithPkMixin, serializers.ModelSerializer):

    class Meta:
        model = OfficeEvent

    patient_name = serializers.SerializerMethodField()
    translated_comment = serializers.SerializerMethodField()
    therapeut_name = UserInfoSerializer(source = 'user')

    def get_patient_name(self, obj):
        if (obj.clazz == "Patient"):
            patient = Patient.objects.get(id = obj.reference)
            return "%s %s" % (patient.family_name, patient.first_name)
        if (obj.clazz == "Examination"):
            examination = Examination.objects.get(id=obj.reference)
            patient = examination.patient
            return "%s %s" % (patient.family_name, patient.first_name)
        return ""

    def get_translated_comment(self, obj):
        return _(obj.comment)


class TherapeutSettingsSerializer(WithPkMixin, serializers.ModelSerializer):
    class Meta:
        model = TherapeutSettings

class OfficeSettingsSerializer(WithPkMixin, serializers.ModelSerializer):
    class Meta:
        model = OfficeSettings



class UserOfficeSerializer(WithPkMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'is_staff', 'is_active')

class PasswordSerializer(serializers.Serializer):
     password = serializers.CharField(
        required=False
     )