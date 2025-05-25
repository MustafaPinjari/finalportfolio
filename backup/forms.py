from django import forms
from .models import BackupSchedule, BackupFile, RestorePoint

class BackupScheduleForm(forms.ModelForm):
    class Meta:
        model = BackupSchedule
        fields = ['name', 'frequency', 'day_of_week', 'day_of_month', 'time', 'retention_count', 'enabled']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'day_of_week': forms.Select(choices=[(i, day) for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])]),
            'day_of_month': forms.Select(choices=[(i, str(i)) for i in range(1, 32)]),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        frequency = cleaned_data.get('frequency')
        day_of_week = cleaned_data.get('day_of_week')
        day_of_month = cleaned_data.get('day_of_month')
        
        if frequency == 'weekly' and day_of_week is None:
            self.add_error('day_of_week', 'Day of week is required for weekly backups')
        
        if frequency == 'monthly' and day_of_month is None:
            self.add_error('day_of_month', 'Day of month is required for monthly backups')
        
        return cleaned_data

class ManualBackupForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, help_text='Name for this backup')
    note = forms.CharField(widget=forms.Textarea, required=False, help_text='Optional notes about this backup')
    include_media = forms.BooleanField(required=False, initial=True, help_text='Include media files in backup')
    include_static = forms.BooleanField(required=False, initial=False, help_text='Include static files in backup')

class RestoreForm(forms.ModelForm):
    class Meta:
        model = RestorePoint
        fields = ['name', 'backup_file', 'description']
        widgets = {
            'backup_file': forms.Select(attrs={'class': 'backup-file-select'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter backup files to only show completed ones
        self.fields['backup_file'].queryset = BackupFile.objects.filter(
            status='completed',
            is_deleted=False
        ).order_by('-created_at')

class ImportForm(forms.Form):
    backup_file = forms.FileField(help_text='Select a .zip or .sql backup file to import')
    name = forms.CharField(max_length=100, help_text='Name for this imported backup')
    note = forms.CharField(widget=forms.Textarea, required=False, help_text='Optional notes about this backup')
