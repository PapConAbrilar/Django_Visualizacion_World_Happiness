from django import forms

from .models import Pais


class PaisForm(forms.ModelForm):
    """Formulario estándar para crear o editar países."""

    class Meta:
        model = Pais
        fields = [
            "nombre",
            "id_region",
            "happiness_score",
            "standard_error",
            "economy",
            "family",
            "health",
            "freedom",
            "trust",
            "generosity",
            "dystopia",
        ]
        labels = {
            "id_region": "Región",
            "happiness_score": "Happiness Score",
            "standard_error": "Standard Error",
            "economy": "Economy (GDP per Capita)",
            "family": "Family",
            "health": "Health (Life Expectancy)",
            "freedom": "Freedom",
            "trust": "Trust (Government Corruption)",
            "generosity": "Generosity",
            "dystopia": "Dystopia Residual",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del país"}),
            "id_region": forms.Select(attrs={"class": "form-control"}),
            "happiness_score": forms.NumberInput(attrs={"class": "form-control", "step": "0.00001"}),
            "standard_error": forms.NumberInput(attrs={"class": "form-control", "step": "0.00001"}),
            "economy": forms.NumberInput(attrs={"class": "form-control", "step": "0.00001"}),
            "family": forms.NumberInput(attrs={"class": "form-control", "step": "0.00001"}),
            "health": forms.NumberInput(attrs={"class": "form-control", "step": "0.00001"}),
            "freedom": forms.NumberInput(attrs={"class": "form-control", "step": "0.00001"}),
            "trust": forms.NumberInput(attrs={"class": "form-control", "step": "0.00001"}),
            "generosity": forms.NumberInput(attrs={"class": "form-control", "step": "0.00001"}),
            "dystopia": forms.NumberInput(attrs={"class": "form-control", "step": "0.00001"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        qs = Pais.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un país con ese nombre.")
        return nombre




