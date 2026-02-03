from aplicacao.DTOs import AuthServiceResponse
from infra.index import log_user
from infra.pagamentos import gerar_invoice

class GerarQrCode:
      def __init__(self, user):
            self.user = user
            self.username = user.username

      def gerar_qrcode(self):
            qr_code = gerar_invoice(self.username)
            if not qr_code: return AuthServiceResponse(msg = "Erro ao gerar invoice.", code = 500, data = None)
            log_user(self.username).info("✅ Novo qrcode gerado.")
            return AuthServiceResponse(msg = None, code = 200, data = qr_code)
