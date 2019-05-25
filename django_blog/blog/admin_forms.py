from django import forms


class PostAdminForm(forms.ModelForm):
    desc = forms.CharField(widget=forms.Textarea(
        {'cols': '35', 'rows': '2'}), label='摘要', required=False)
