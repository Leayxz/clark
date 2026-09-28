# Módulo Afiliação — Documentação Técnica

## Arquitetura

Módulo Django standalone seguindo o padrão do projeto DRF com separação em camadas, api para endpoints, serializers para validação, service para lógica de negócio e repository para acesso ao banco, sem try/except explícito no repositório usando filter().first() para buscas que podem não retornar resultado.

## Estrutura de arquivos

O módulo está organizado em source/affiliate com models.py contendo o modelo Affiliate com OneToOneField para User e campos para cupom líquido e descrição de divulgação, serializers.py com AffiliateRegisterSerializer usando to_internal_value para normalização de dados, service.py com AffiliateService que valida cupom único e usuário único antes de persistir, repository.py com AffiliateRepository usando filter().first() em vez de try/except, api.py com endpoint POST protegido por decorator authenticated do DRF, urls.py com rotas para página HTML e API, views.py renderizando a página HTML, static/affiliate.css com estilos premium para botões e modal de confirmação.

## Modelo de dados

A tabela affiliate possui user_id como OneToOneField para authentication.user garantindo um afiliado por usuário, coupon_code único com até 10 caracteres e índice para busca rápida, liquid_address único com até 100 caracteres para receber em DEPIX, promotion_description texto livre obrigatório para descrever estratégia de divulgação, terms_accepted_at registrando momento do aceite, created_at e updatedat para auditoria temporal.

## Container e injeção de dependência

O source/container.py instancia AffiliateRepository e AffiliateService no padrão do projeto, expondo affiliate_service como singleton importável via from source.container import affiliate_service, sem try/except na instanciação.

## Validações

O AffiliateRegisterSerializer valida liquid_address com mínimo 20 caracteres e máximo 100, coupon com mínimo 3 e máximo 10 caracteres, promotion_description com mínimo 10 caracteres, normaliza liquid_address com strip, coupon com strip upper e remoção de espaços, promotion_description com strip. O service valida unicidade de cupom e usuário antes de persistir. O frontend valida prefixo lq1 e tamanho mínimo no liquid_address, mínimo 3 caracteres no cupom, mínimo 10 caracteres na descrição e aceitação obrigatória dos termos.

## Endpoints

GET /affiliate/ renderiza a página HTML de afiliação via views.page_affiliate, POST /api/v1/affiliates/register processa o cadastro via api.register_affiliate ambos registrados em source/affiliate/urls.py.

## Decisões técnicas

Sem try/except no repositório usando filter().first() que retorna None naturalmente, sem status de moderação no modelo por decisão consciente, sem campo telegram no cadastro pois o usuário configura via módulo de comunicação próprio, sem FK direta Invoice→Affiliate usando relação indireta via coupon_code, tipagem forte com cast do typing para evitar warnings do Pylance no serializer.validated_data, OneToOneField em vez de ForeignKey unique para relação user-afiliado.

# Fluxos do Módulo

### Registro de novos afiliados
O frontend faz POST para /api/v1/affiliates/register com liquid_address, cupom e promotion_description, o decorator authenticated valida o JWT e injeta request.subject com o user_id, o serializer valida e normaliza os dados retornando 400 se inválido, o service repassa para o repository que constrói o Affiliate e persiste com objects.create dentro de try/except para capturar IntegrityError, retorna 201 Created no sucesso ou 409 com o erro específico caso o cupom ou o endereço liquid já estejam em uso, tudo rastreado por tracer.start_as_current_span e logado com logger.info e logger.error, o frontend então abre o modal de confirmação em vez de mostrar mensagem inline, com animação de scale e opacidade no overlay, bloqueio do scroll do body, e fechamento via botão Enter ou clique no overlay.
