import unittest
import json
from app import app, db, HistoricoQuant, LogAuditoriaSeguranca


class TestAuraQuantEnterprise(unittest.TestCase):

    def setUp(self):
        """Configurações executadas antes de CADA teste."""
        # Força o modo de teste no Flask
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        # Usa um banco SQLite temporário em memória para isolar os testes
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = app.test_client()

        # Cria as tabelas do banco no ambiente de teste
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Limpeza executada após CADA teste."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # =========================================================================
    # 1. TESTES DE ROTAS / FRONTEND
    # =========================================================================

    def test_rota_terminal_status_code(self):
        """Garante que a rota principal (Terminal) carrega com HTTP 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AuraQuant Enterprise Analytics', response.data)
        self.assertIn(b'Terminal Gr\xc3\xa1fico Avan\xc3\xa7ado', response.data)

    def test_rota_analytics_status_code(self):
        """Garante que a rota de BI (Analytics) carrega com HTTP 200."""
        response = self.client.get('/analytics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Painel Anal\xc3\xadtico de Oportunidades', response.data)

    # =========================================================================
    # 2. TESTES DA API E MOTOR QUANTITATIVO
    # =========================================================================

    def test_api_analytics_data_estrutura(self):
        """Valida se o endpoint de BI retorna a estrutura JSON e campos corretos."""
        response = self.client.get('/api/v1/analytics/data')
        self.assertEqual(response.status_code, 200)

        dados = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(dados, list)
        self.assertGreater(len(dados), 0)

        # Valida as chaves obrigatórias do primeiro ativo retornado
        ativo = dados[0]
        chaves_esperadas = [
            "ticker", "tv_symbol", "nome", "tipo", "preco",
            "variacao", "rsi", "z_score", "score", "sinal", "badge"
        ]
        for chave in chaves_esperadas:
            self.assertIn(chave, ativo)

    def test_persistencia_banco_dados_ao_chamar_api(self):
        """Valida se as análises geradas estão gravando no histórico do banco SQL."""
        # Executa a API
        self.client.get('/api/v1/analytics/data')

        # Verifica no banco em memória se os registros foram gravados
        with app.app_context():
            registros = HistoricoQuant.query.all()
            self.assertGreater(len(registros), 0)
            self.assertIsNotNone(registros[0].ticker)
            self.assertIsNotNone(registros[0].score_final)

    # =========================================================================
    # 3. TESTES DE SEGURANÇA (CSP & VALIDAR URL/SSRF)
    # =========================================================================

    def test_headers_seguranca_http(self):
        """Verifica se os headers de proteção (CSP, XSS, Frame Options) estão presentes."""
        response = self.client.get('/')
        self.assertIn('Content-Security-Policy', response.headers)
        self.assertEqual(response.headers['X-Frame-Options'], 'SAMEORIGIN')
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')

    def test_validacao_url_permitida(self):
        """Valida se domínio permitido (TradingView) é aprovado."""
        payload = {"url": "https://www.tradingview.com/chart/"}
        response = self.client.post(
            '/api/v1/validar-url',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['valido'])

    def test_validacao_url_bloqueada(self):
        """Valida se domínios não autorizados são rejeitados pelo sistema."""
        payload = {"url": "https://site-malicioso-desconhecido.com/test"}
        response = self.client.post(
            '/api/v1/validar-url',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data.decode('utf-8'))
        self.assertFalse(data['valido'])

    def test_auditoria_seguranca_no_banco(self):
        """Garante que as tentativas de validação de URL geram log no banco."""
        payload = {"url": "https://www.tradingview.com"}
        self.client.post(
            '/api/v1/validar-url',
            data=json.dumps(payload),
            content_type='application/json'
        )

        with app.app_context():
            logs = LogAuditoriaSeguranca.query.all()
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0].status_seguranca, "PERMITIDO")


if __name__ == '__main__':
    print("Iniciando Suíte de Testes Automatizados AuraQuant Enterprise...")
    unittest.main(verbosity=2)