from django import forms

class TelegramForm(forms.Form):
      TOKEN_TELEGRAM = forms.TextInput()
      ID_TELEGRAM = forms.TextInput

class CadastroForm(forms.Form):
      email = forms.EmailField()
      senha = forms.CharField()

class AutomacaoForm(forms.Form):
      quantity1 = forms.IntegerField()
      quantity2 = forms.IntegerField()
      quantity3 = forms.IntegerField()
      quantity4 = forms.IntegerField()

      preco_referencia = forms.FloatField()
      comprar_abaixo = forms.FloatField()

      percentual_lucro = forms.FloatField()
      variacao_compra = forms.IntegerField()

      limite_margem = forms.IntegerField()
      percentual_seguranca_liquidacao = forms.FloatField()


# DJANGO FORMS VALIDA OS DADOS E MONTA UM OBJETO AUTOMATICAMENTE
