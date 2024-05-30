from django import forms


class PurchasePointsForm(forms.Form):
    points = forms.ChoiceField(choices=[(x, f'{x} points') for x in [100, 200, 500, 1000, 2000, 5000, 10000, 20000,
                                                                     50000, 100000]], label='Number of points')


class WithdrawPointsForm(forms.Form):
    points = forms.IntegerField(min_value=1, label='Number of points')
