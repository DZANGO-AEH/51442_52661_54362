from django import forms


class PurchasePointsForm(forms.Form):
    """
    Form for purchasing points.

    Fields:
        points (ChoiceField): A dropdown field allowing users to select the number of points to purchase.
                              The choices available are 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, and 100000 points.
    """
    points = forms.ChoiceField(
        choices=[(x, f'{x} points') for x in [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]],
        label='Number of points'
    )


class WithdrawPointsForm(forms.Form):
    """
    Form for withdrawing points.

    Fields:
        points (IntegerField): An integer field allowing users to specify the number of points to withdraw.
                               The minimum value is 1 point.
    """
    points = forms.IntegerField(
        min_value=1,
        label='Number of points'
    )
