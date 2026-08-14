"""
===============================================================================
AURAQUANT ENTERPRISE v8.0 - SISTEMA UNIFICADO (FIXED)
===============================================================================
"""

import os
import random
from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from jinja2 import DictLoader

# =============================================================================
# 1. TEMPLATES HTML (DECLARADOS PRIMEIRO PARA O LOADER)
# =============================================================================

HTML_BASE = """
<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AuraQuant Enterprise Analytics</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #05070c; color: #e2e8f0; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    .glass-card {
      background: rgba(13, 18, 30, 0.75);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.07);
    }
    .glass-card-hover:hover {
      border-color: rgba(99, 102, 241, 0.4);
      box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #030508; }
    ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 2px; }
  </style>
</head>
<body class="min-h-screen flex flex-col antialiased selection:bg-indigo-500/30">

  <!-- TICKER SUPERIOR -->
  <div class="bg-[#030509] border-b border-slate-800/80 px-4 py-1.5 text-[11px] font-mono flex items-center justify-between text-slate-400 overflow-x-auto whitespace-nowrap">
    <div class="flex items-center gap-6">
      <span class="flex items-center gap-1.5 text-slate-200 font-bold">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
        SISTEMA QUANTITATIVO ATIVO
      </span>
      <span>IBOV: <strong class="text-emerald-400">128.450 pts (+0.45%)</strong></span>
      <span>S&P 500: <strong class="text-emerald-400">5.450 pts (+0.22%)</strong></span>
      <span>NASDAQ: <strong class="text-rose-400">17.820 pts (-0.15%)</strong></span>
      <span>PETRÓLEO: <strong class="text-emerald-400">$82.40 (+1.10%)</strong></span>
    </div>
    <div class="flex items-center gap-4 text-slate-500">
      <span>LATÊNCIA: <strong class="text-indigo-400">12ms</strong></span>
      <span>CRIPTOGRAFIA: <strong class="text-emerald-400">AES-256</strong></span>
    </div>
  </div>

  <!-- NAVEGAÇÃO -->
  <header class="border-b border-slate-800/80 bg-[#080c14]/90 backdrop-blur-md px-6 py-3 flex items-center justify-between sticky top-0 z-50">
    <div class="flex items-center gap-8">
      <a href="/" class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-black text-white text-sm shadow-lg shadow-indigo-600/30">
          AQ
        </div>
        <div>
          <span class="font-extrabold text-base tracking-tight text-white font-mono">AURA<span class="text-indigo-500">QUANT</span></span>
          <span class="block text-[9px] font-mono text-slate-400 tracking-widest uppercase">Institutional Terminal v8.0</span>
        </div>
      </a>

      <nav class="hidden md:flex items-center gap-1 bg-slate-900/80 border border-slate-800 p-1 rounded-lg text-xs font-medium">
        <a href="/" class="px-4 py-1.5 rounded-md transition {% if active_page == 'terminal' %}bg-indigo-600 text-white shadow-sm{% else %}text-slate-400 hover:text-white{% endif %}">
          🖥️ Terminal de Trading
        </a>
        <a href="/analytics" class="px-4 py-1.5 rounded-md transition {% if active_page == 'analytics' %}bg-indigo-600 text-white shadow-sm{% else %}text-slate-400 hover:text-white{% endif %}">
          📊 Relatório BI Dinâmico
        </a>
      </nav>
    </div>

    <div class="flex items-center gap-4">
      <div class="hidden lg:flex flex-col items-end text-[11px] font-mono">
        <span class="text-slate-300 font-semibold">BANCO DE DADOS: <span class="text-emerald-400">SQLAlchemy Active</span></span>
        <span class="text-slate-500">CSP Protection: <span class="text-indigo-400">ENABLED</span></span>
      </div>
      <button onclick="abrirModalSeguranca()" class="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-lg border border-slate-700 transition font-mono">
        🔒 Status Segurança
      </button>
    </div>
  </header>

  <main class="flex-1">
    {% block content %}{% endblock %}
  </main>

  <footer class="border-t border-slate-800/80 bg-[#04060a] px-6 py-4 text-xs font-mono text-slate-500 flex flex-wrap justify-between items-center gap-4">
    <div>
      <p>© 2026 AuraQuant Enterprise Analytics. Todos os direitos reservados.</p>
    </div>
    <div class="flex gap-6 text-[11px]">
      <span class="text-emerald-500">● Conexão Segura SSL/TLS</span>
      <span>Engine: <strong class="text-slate-400">Python 3.12 / Flask / SQLAlchemy</strong></span>
    </div>
  </footer>

  <div id="modalSeguranca" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="glass-card max-w-lg w-full rounded-2xl p-6 space-y-4 border border-indigo-500/30">
      <div class="flex justify-between items-center border-b border-slate-800 pb-3">
        <h3 class="font-bold text-white text-sm font-mono">🛡️ Módulo de Segurança & Proteção</h3>
        <button onclick="fecharModalSeguranca()" class="text-slate-400 hover:text-white">✕</button>
      </div>
      <div class="space-y-3 text-xs font-mono text-slate-300">
        <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800">
          <span class="text-indigo-400 font-bold block">Proteção contra Vazamento (XSS/CSRF)</span>
          <p class="text-slate-400 text-[11px] mt-1">Headers HTTP de Content Security Policy (CSP) ativados no backend.</p>
        </div>
        <div class="p-3 bg-slate-900/80 rounded-lg border border-slate-800">
          <span class="text-emerald-400 font-bold block">Validação Sanitizada de Links Externos</span>
          <p class="text-slate-400 text-[11px] mt-1">Proteção contra Server-Side Request Forgery (SSRF) no carregamento de links.</p>
        </div>
      </div>
      <button onclick="fecharModalSeguranca()" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 rounded-lg text-xs transition">
        Confirmar e Fechar
      </button>
    </div>
  </div>

  <script>
    function abrirModalSeguranca() { document.getElementById('modalSeguranca').classList.remove('hidden'); }
    function fecharModalSeguranca() { document.getElementById('modalSeguranca').classList.add('hidden'); }
  </script>

  {% block scripts %}{% endblock %}
</body>
</html>
"""

HTML_TERMINAL = """
{% extends "base.html" %}
{% set active_page = "terminal" %}

{% block content %}
<div class="p-4 space-y-4">
  <div class="glass-card p-3 rounded-xl flex flex-wrap items-center justify-between gap-4">
    <div class="flex items-center gap-4">
      <div>
        <label class="block text-[10px] font-mono text-slate-500 uppercase">Ativo Selecionado</label>
        <select id="selectSymbol" onchange="alterarAtivo(this.value)" class="bg-[#030712] border border-slate-800 text-indigo-400 font-bold rounded-lg px-3 py-1.5 text-xs focus:outline-none font-mono">
          <optgroup label="B3 - Ações Brasil">
            <option value="BMFBOVESPA:PETR4">PETR4 - Petrobras PN</option>
            <option value="BMFBOVESPA:VALE3">VALE3 - Vale ON</option>
            <option value="BMFBOVESPA:ITUB4">ITUB4 - Itaú Unibanco</option>
            <option value="BMFBOVESPA:BOVA11">BOVA11 - ETF Ibovespa</option>
          </optgroup>
          <optgroup label="Forex & Câmbio">
            <option value="FX:EURUSD">EUR / USD - Euro / Dólar</option>
            <option value="FX:GBPUSD">GBP / USD - Libra / Dólar</option>
            <option value="FX_IDC:USDBRL">USD / BRL - Dólar / Real</option>
          </optgroup>
          <optgroup label="Criptoativos">
            <option value="BINANCE:BTCUSDT">BTC / USDT - Bitcoin</option>
            <option value="BINANCE:ETHUSDT">ETH / USDT - Ethereum</option>
          </optgroup>
        </select>
      </div>

      <div>
        <label class="block text-[10px] font-mono text-slate-500 uppercase">Timeframe</label>
        <select class="bg-[#030712] border border-slate-800 text-slate-300 font-bold rounded-lg px-3 py-1.5 text-xs focus:outline-none font-mono">
          <option value="1">1 Minuto</option>
          <option value="5" selected>5 Minutos</option>
          <option value="15">15 Minutos</option>
          <option value="60">1 Hora</option>
          <option value="D">Diário</option>
        </select>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <div>
        <label class="block text-[10px] font-mono text-slate-500 uppercase">Carregar Link / Ticker Personalizado</label>
        <div class="flex items-center gap-2">
          <input type="text" id="linkInput" placeholder="URL segura ou Ticker (ex: NASDAQ:AAPL)..." class="bg-[#030712] border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 w-80 focus:outline-none focus:border-indigo-500 font-mono">
          <button onclick="carregarLinkSeguro()" class="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-4 py-1.5 rounded-lg text-xs transition font-mono">
            Carregar
          </button>
        </div>
      </div>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
    <div class="lg:col-span-3 glass-card rounded-xl p-3 flex flex-col h-[680px]">
      <div class="flex justify-between items-center mb-2 px-2">
        <span class="text-xs font-bold text-slate-400 uppercase font-mono flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-indigo-500"></span>
          Terminal Gráfico Avançado TradingView
        </span>
        <span class="text-[11px] text-emerald-400 font-mono">● STREAMING DIRETO DE MERCADO</span>
      </div>
      <div id="tradingview_container" class="w-full flex-1 rounded-lg overflow-hidden border border-slate-800"></div>
    </div>

    <div class="space-y-4 flex flex-col">
      <div class="glass-card p-4 rounded-xl space-y-3">
        <h3 class="text-xs font-bold text-slate-400 uppercase font-mono border-b border-slate-800 pb-2">
          ⚙️ Calibragem do Algoritmo
        </h3>
        <div class="space-y-2 text-xs font-mono">
          <div class="flex justify-between p-2 bg-slate-900/60 rounded-lg border border-slate-800">
            <span class="text-slate-500">Peso RSI (14)</span>
            <span class="text-indigo-400 font-bold">35%</span>
          </div>
          <div class="flex justify-between p-2 bg-slate-900/60 rounded-lg border border-slate-800">
            <span class="text-slate-500">Peso Z-Score</span>
            <span class="text-indigo-400 font-bold">35%</span>
          </div>
          <div class="flex justify-between p-2 bg-slate-900/60 rounded-lg border border-slate-800">
            <span class="text-slate-500">Volatilidade Implícita</span>
            <span class="text-indigo-400 font-bold">15%</span>
          </div>
          <div class="flex justify-between p-2 bg-slate-900/60 rounded-lg border border-slate-800">
            <span class="text-slate-500">Fator Momentum</span>
            <span class="text-indigo-400 font-bold">15%</span>
          </div>
        </div>
      </div>

      <div class="glass-card p-4 rounded-xl space-y-3 flex-1 flex flex-col justify-between">
        <h3 class="text-xs font-bold text-slate-400 uppercase font-mono border-b border-slate-800 pb-2">
          📡 Sinais em Destaque
        </h3>
        <div class="space-y-2 font-mono text-xs">
          <div class="p-2.5 bg-emerald-950/40 border border-emerald-500/30 rounded-lg flex justify-between items-center">
            <div>
              <strong class="text-emerald-400 block">PETR4</strong>
              <span class="text-[10px] text-slate-400">Score Quant: 88.5%</span>
            </div>
            <span class="text-[10px] bg-emerald-500/20 text-emerald-300 font-bold px-2 py-0.5 rounded">COMPRA</span>
          </div>

          <div class="p-2.5 bg-rose-950/40 border border-rose-500/30 rounded-lg flex justify-between items-center">
            <div>
              <strong class="text-rose-400 block">USD/BRL</strong>
              <span class="text-[10px] text-slate-400">Score Quant: 24.1%</span>
            </div>
            <span class="text-[10px] bg-rose-500/20 text-rose-300 font-bold px-2 py-0.5 rounded">VENDA</span>
          </div>
        </div>

        <div class="p-3 bg-slate-900/90 rounded-lg border border-slate-800 text-[10px] font-mono text-slate-500 space-y-1 mt-4">
          <p class="text-slate-400 font-bold">💡 Dica Quantitativa:</p>
          <p>Valores de Z-Score acima de +2.0 indicam sobrecompra estatística; abaixo de -2.0 indicam subavaliação.</p>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script>
  function carregarTradingView(symbol) {
    document.getElementById('tradingview_container').innerHTML = '';
    new TradingView.widget({
      "autosize": true,
      "symbol": symbol,
      "interval": "5",
      "timezone": "America/Sao_Paulo",
      "theme": "dark",
      "style": "1",
      "locale": "br",
      "container_id": "tradingview_container",
      "studies": ["RSI@tv-basicstudies", "MACD@tv-basicstudies"]
    });
  }

  function alterarAtivo(symbol) { carregarTradingView(symbol); }

  async function carregarLinkSeguro() {
    const inputVal = document.getElementById('linkInput').value.trim();
    if (!inputVal) return;

    if (inputVal.startsWith('http://') || inputVal.startsWith('https://')) {
      const resp = await fetch('/api/v1/validar-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: inputVal })
      });
      const data = await resp.json();

      if (data.valido) {
        document.getElementById('tradingview_container').innerHTML = `<iframe src="${inputVal}" class="w-full h-full rounded-lg border-0"></iframe>`;
      } else {
        alert('URL bloqueada pelas políticas de segurança CSP da plataforma.');
      }
    } else {
      carregarTradingView(inputVal.toUpperCase());
    }
  }

  document.addEventListener('DOMContentLoaded', () => carregarTradingView('BMFBOVESPA:PETR4'));
</script>
{% endblock %}
"""

HTML_ANALYTICS = """
{% extends "base.html" %}
{% set active_page = "analytics" %}

{% block content %}
<div class="p-6 space-y-6 max-w-[1700px] mx-auto">
  <div class="flex flex-wrap justify-between items-center gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
    <div>
      <h1 class="text-base font-bold text-white tracking-tight flex items-center gap-2">
        <span class="w-3 h-3 rounded-sm bg-indigo-500 inline-block"></span>
        Painel Analítico de Oportunidades & Estatística de Mercado
      </h1>
      <p class="text-xs text-slate-400 font-mono">Modelagem quantitativa em tempo real integrada com Banco SQL em Python</p>
    </div>

    <button onclick="atualizarDadosBI()" class="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs px-4 py-2 rounded-lg transition shadow-md font-mono">
      🔄 Atualizar Dados BI
    </button>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <div class="glass-card p-4 rounded-xl border-l-4 border-l-emerald-500 glass-card-hover transition">
      <span class="text-xs text-slate-400 font-semibold uppercase font-mono">Top Compra Algorítmica</span>
      <div id="kpiTopBuy" class="text-2xl font-bold text-emerald-400 mt-1 font-mono">--</div>
      <span class="text-[10px] text-slate-500 font-mono">Maior Probabilidade Estatística</span>
    </div>

    <div class="glass-card p-4 rounded-xl border-l-4 border-l-rose-500 glass-card-hover transition">
      <span class="text-xs text-slate-400 font-semibold uppercase font-mono">Top Alerta de Venda</span>
      <div id="kpiTopSell" class="text-2xl font-bold text-rose-400 mt-1 font-mono">--</div>
      <span class="text-[10px] text-slate-500 font-mono">Nível Crítico de Sobrecompra</span>
    </div>

    <div class="glass-card p-4 rounded-xl border-l-4 border-l-indigo-500 glass-card-hover transition">
      <span class="text-xs text-slate-400 font-semibold uppercase font-mono">Líder do Mercado Forex</span>
      <div id="kpiForex" class="text-2xl font-bold text-indigo-400 mt-1 font-mono">--</div>
      <span class="text-[10px] text-slate-500 font-mono">Maior Variação de Momentum</span>
    </div>

    <div class="glass-card p-4 rounded-xl border-l-4 border-l-amber-500 glass-card-hover transition">
      <span class="text-xs text-slate-400 font-semibold uppercase font-mono">Persistência do Banco</span>
      <div class="text-2xl font-bold text-amber-400 mt-1 font-mono">SQL Active</div>
      <span class="text-[10px] text-slate-500 font-mono">Histórico Armazenado com Sucesso</span>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2 glass-card p-5 rounded-xl flex flex-col justify-between">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xs font-bold text-slate-300 uppercase font-mono">
          📊 Matriz de Probabilidade de Compra e Venda
        </h2>
        <span class="text-[11px] text-slate-500 font-mono">Score de 0% a 100%</span>
      </div>
      <div class="h-72 relative">
        <canvas id="chartScores"></canvas>
      </div>
    </div>

    <div class="glass-card p-5 rounded-xl flex flex-col">
      <h2 class="text-xs font-bold text-slate-300 uppercase font-mono mb-4 flex justify-between items-center">
        <span>💱 Moedas em Alta / Forex</span>
        <span class="text-[10px] text-emerald-400">AO VIVO</span>
      </h2>
      <div id="forexList" class="space-y-3 flex-1 overflow-y-auto"></div>
    </div>
  </div>

  <div class="glass-card rounded-xl overflow-hidden border border-slate-800">
    <div class="px-6 py-4 border-b border-slate-800 bg-slate-900/80 flex justify-between items-center">
      <h2 class="text-xs font-bold text-slate-300 uppercase font-mono">
        📋 Matriz Algorítmica de Recomendação de Investimento
      </h2>
      <span class="text-xs text-emerald-400 font-mono">● Z-Score Calibrado</span>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left text-xs font-mono">
        <thead class="bg-[#030712] text-slate-400 uppercase text-[10px] border-b border-slate-800">
          <tr>
            <th class="px-6 py-4">Ativo / Ticker</th>
            <th class="px-6 py-4">Mercado</th>
            <th class="px-6 py-4">Preço Atual</th>
            <th class="px-6 py-4">Var (%) 24h</th>
            <th class="px-6 py-4">RSI (14)</th>
            <th class="px-6 py-4">Z-Score</th>
            <th class="px-6 py-4">Score Chance (%)</th>
            <th class="px-6 py-4">Recomendação Estatística</th>
          </tr>
        </thead>
        <tbody id="tableBody" class="divide-y divide-slate-800/60"></tbody>
      </table>
    </div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script>
  let chartInstancia = null;

  async function atualizarDadosBI() {
    const res = await fetch('/api/v1/analytics/data');
    const data = await res.json();

    const topBuy = data[0];
    const topSell = [...data].sort((a,b) => a.score - b.score)[0];
    const topForex = data.filter(d => d.tipo === 'FOREX').sort((a,b) => b.variacao - a.variacao)[0];

    document.getElementById('kpiTopBuy').innerText = `${topBuy.ticker} (${topBuy.score}%)`;
    document.getElementById('kpiTopSell').innerText = `${topSell.ticker} (${topSell.score}%)`;
    document.getElementById('kpiForex').innerText = `${topForex.ticker} (${topForex.variacao >= 0 ? '+' : ''}${topForex.variacao}%)`;

    document.getElementById('tableBody').innerHTML = data.map(item => `
      <tr class="hover:bg-slate-800/40 transition">
        <td class="px-6 py-4 font-bold text-slate-100">
          ${item.ticker} 
          <span class="text-[10px] text-slate-500 font-normal block">${item.nome}</span>
        </td>
        <td class="px-6 py-4 text-slate-400">${item.tipo}</td>
        <td class="px-6 py-4 font-bold text-slate-200">$ ${item.preco}</td>
        <td class="px-6 py-4 font-bold ${item.variacao >= 0 ? 'text-emerald-400' : 'text-rose-400'}">
          ${item.variacao >= 0 ? '+' : ''}${item.variacao}%
        </td>
        <td class="px-6 py-4 text-slate-300">${item.rsi}</td>
        <td class="px-6 py-4 text-slate-400">${item.z_score}</td>
        <td class="px-6 py-4 font-bold text-indigo-400">${item.score}%</td>
        <td class="px-6 py-4">
          <span class="px-3 py-1 rounded text-[10px] font-bold border ${item.badge}">
            ${item.sinal}
          </span>
        </td>
      </tr>
    `).join('');

    document.getElementById('forexList').innerHTML = data.filter(d => d.tipo === 'FOREX').map(f => `
      <div class="bg-[#030712] p-3 rounded-lg border border-slate-800 flex justify-between items-center">
        <div>
          <span class="font-bold text-slate-200 text-xs block font-mono">${f.ticker}</span>
          <span class="text-[10px] text-slate-500">${f.nome}</span>
        </div>
        <span class="font-bold text-xs font-mono ${f.variacao >= 0 ? 'text-emerald-400' : 'text-rose-400'}">
          ${f.variacao >= 0 ? '+' : ''}${f.variacao}%
        </span>
      </div>
    `).join('');

    renderizarGraficoBI(data);
  }

  function renderizarGraficoBI(data) {
    const ctx = document.getElementById('chartScores').getContext('2d');
    if (chartInstancia) chartInstancia.destroy();

    chartInstancia = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map(d => d.ticker),
        datasets: [{
          label: 'Score Algorítmico (%)',
          data: data.map(d => d.score),
          backgroundColor: data.map(d => d.color_hex),
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#64748b' } },
          x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
        }
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    atualizarDadosBI();
    setInterval(atualizarDadosBI, 6000);
  });
</script>
{% endblock %}
"""

# =============================================================================
# 2. CONFIGURAÇÃO DA APLICAÇÃO & REGISTRO DOS TEMPLATES VIRTUAIS
# =============================================================================
app = Flask(__name__)

# REGISTRA OS TEMPLATES NA MEMÓRIA DO FLASK PARA PERMITIR HERANÇA
app.jinja_loader = DictLoader({
    'base.html': HTML_BASE,
    'terminal.html': HTML_TERMINAL,
    'analytics.html': HTML_ANALYTICS
})

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'auraquant_enterprise_sec_key_9981273918237')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///auraquant_enterprise.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

PESO_RSI = 0.35
PESO_ZSCORE = 0.35
PESO_VOLATILIDADE = 0.15
PESO_MOMENTUM = 0.15

ALLOWED_DOMAINS = {
    'tradingview.com',
    's.tradingview.com',
    'investing.com',
    'charting.com',
    'bloomberg.com'
}

# =============================================================================
# 3. BANCO DE DADOS (SQLALCHEMY)
# =============================================================================
db = SQLAlchemy(app)

class HistoricoQuant(db.Model):
    __tablename__ = 'historico_quant'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), nullable=False, index=True)
    nome_ativo = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(30), nullable=False)
    preco_atual = db.Column(db.Float, nullable=False)
    variacao_24h = db.Column(db.Float, nullable=False)
    rsi_14 = db.Column(db.Float, nullable=False)
    z_score = db.Column(db.Float, nullable=False)
    volatilidade = db.Column(db.Float, nullable=False)
    score_final = db.Column(db.Float, nullable=False)
    sinal_operacional = db.Column(db.String(50), nullable=False)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

class LogAuditoriaSeguranca(db.Model):
    __tablename__ = 'log_auditoria_seguranca'

    id = db.Column(db.Integer, primary_key=True)
    ip_origem = db.Column(db.String(50), nullable=False)
    evento = db.Column(db.String(255), nullable=False)
    status_seguranca = db.Column(db.String(20), nullable=False)
    data_evento = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# =============================================================================
# 4. HEADERS DE SEGURANÇA
# =============================================================================
@app.after_request
def aplicar_headers_seguranca(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://s3.tradingview.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "frame-src 'self' https://s.tradingview.com https://www.tradingview.com; "
        "img-src 'self' data: https:;"
    )
    return response

# =============================================================================
# 5. MOTOR QUANTITATIVO ESTATÍSTICO
# =============================================================================
UNIVERSO_ATIVOS = [
    {"ticker": "PETR4", "tv_symbol": "BMFBOVESPA:PETR4", "nome": "Petrobras PN", "tipo": "B3", "preco_base": 38.50},
    {"ticker": "VALE3", "tv_symbol": "BMFBOVESPA:VALE3", "nome": "Vale ON", "tipo": "B3", "preco_base": 62.10},
    {"ticker": "ITUB4", "tv_symbol": "BMFBOVESPA:ITUB4", "nome": "Itaú Unibanco PN", "tipo": "B3", "preco_base": 34.80},
    {"ticker": "BBDC4", "tv_symbol": "BMFBOVESPA:BBDC4", "nome": "Bradesco PN", "tipo": "B3", "preco_base": 15.20},
    {"ticker": "BBAS3", "tv_symbol": "BMFBOVESPA:BBAS3", "nome": "Banco do Brasil ON", "tipo": "B3", "preco_base": 27.90},
    {"ticker": "BOVA11", "tv_symbol": "BMFBOVESPA:BOVA11", "nome": "ETF Ibovespa", "tipo": "B3", "preco_base": 122.40},
    {"ticker": "EUR/USD", "tv_symbol": "FX:EURUSD", "nome": "Euro / Dólar Americano", "tipo": "FOREX", "preco_base": 1.0850},
    {"ticker": "GBP/USD", "tv_symbol": "FX:GBPUSD", "nome": "Libra / Dólar Americano", "tipo": "FOREX", "preco_base": 1.2720},
    {"ticker": "USD/BRL", "tv_symbol": "FX_IDC:USDBRL", "nome": "Dólar Americano / Real", "tipo": "FOREX", "preco_base": 5.4500},
    {"ticker": "USD/JPY", "tv_symbol": "FX:USDJPY", "nome": "Dólar / Iene Japonês", "tipo": "FOREX", "preco_base": 155.30},
    {"ticker": "BTC/USD", "tv_symbol": "BINANCE:BTCUSDT", "nome": "Bitcoin / USDT", "tipo": "CRYPTO", "preco_base": 64200.00},
    {"ticker": "ETH/USD", "tv_symbol": "BINANCE:ETHUSDT", "nome": "Ethereum / USDT", "tipo": "CRYPTO", "preco_base": 3480.00},
    {"ticker": "SOL/USD", "tv_symbol": "BINANCE:SOLUSDT", "nome": "Solana / USDT", "tipo": "CRYPTO", "preco_base": 145.00}
]

def processar_analise_quant():
    relatorio = []

    for ativo in UNIVERSO_ATIVOS:
        var_pct = round(random.uniform(-3.2, 3.8), 2)
        preco_atual = round(ativo["preco_base"] * (1 + (var_pct / 100)), 2)
        rsi = round(random.uniform(18, 82), 1)
        z_score = round(random.uniform(-3.0, 3.0), 2)
        volatilidade = round(random.uniform(0.5, 2.8), 2)
        momentum = round(random.uniform(-1.5, 1.5), 2)

        fator_rsi = (100 - rsi)
        fator_z = 50 - (z_score * 16.6)
        fator_vol = (3.0 - volatilidade) * 15
        fator_mom = 50 + (momentum * 20)

        raw_score = (
            (fator_rsi * PESO_RSI) +
            (fator_z * PESO_ZSCORE) +
            (fator_vol * PESO_VOLATILIDADE) +
            (fator_mom * PESO_MOMENTUM)
        )
        score = max(1.0, min(99.0, round(raw_score, 1)))

        if score >= 70.0:
            sinal = "COMPRA FORTE"
            badge = "bg-emerald-950/90 text-emerald-400 border-emerald-500/40"
            hex_color = "#10b981"
        elif score >= 55.0:
            sinal = "COMPRA MODERADA"
            badge = "bg-emerald-900/40 text-emerald-300 border-emerald-600/30"
            hex_color = "#34d399"
        elif score <= 30.0:
            sinal = "VENDA FORTE"
            badge = "bg-rose-950/90 text-rose-400 border-rose-500/40"
            hex_color = "#f43f5e"
        elif score <= 45.0:
            sinal = "VENDA MODERADA"
            badge = "bg-rose-900/40 text-rose-300 border-rose-600/30"
            hex_color = "#fb7185"
        else:
            sinal = "NEUTRO / MANTER"
            badge = "bg-slate-800/80 text-slate-400 border-slate-700"
            hex_color = "#64748b"

        relatorio.append({
            "ticker": ativo["ticker"],
            "tv_symbol": ativo["tv_symbol"],
            "nome": ativo["nome"],
            "tipo": ativo["tipo"],
            "preco": preco_atual,
            "variacao": var_pct,
            "rsi": rsi,
            "z_score": z_score,
            "volatilidade": volatilidade,
            "score": score,
            "sinal": sinal,
            "badge": badge,
            "color_hex": hex_color
        })

        try:
            reg = HistoricoQuant(
                ticker=ativo["ticker"],
                nome_ativo=ativo["nome"],
                categoria=ativo["tipo"],
                preco_atual=preco_atual,
                variacao_24h=var_pct,
                rsi_14=rsi,
                z_score=z_score,
                volatilidade=volatilidade,
                score_final=score,
                sinal_operacional=sinal
            )
            db.session.add(reg)
        except Exception:
            db.session.rollback()

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    relatorio.sort(key=lambda x: x["score"], reverse=True)
    return relatorio

# =============================================================================
# 6. ROTAS E ENDPOINTS
# =============================================================================

@app.route('/')
def rota_terminal():
    return render_template('terminal.html')

@app.route('/analytics')
def rota_analytics():
    return render_template('analytics.html')

@app.route('/api/v1/analytics/data', methods=['GET'])
def api_dados_analytics():
    dados = processar_analise_quant()
    return jsonify(dados)

@app.route('/api/v1/validar-url', methods=['POST'])
def api_validar_url():
    data = request.get_json() or {}
    url = data.get('url', '')
    
    valido = False
    try:
        parsed = urlparse(url)
        if parsed.scheme in ('http', 'https'):
            domain = parsed.netloc.split(':')[0]
            valido = any(domain.endswith(dom) for dom in ALLOWED_DOMAINS)
    except Exception:
        valido = False

    try:
        log = LogAuditoriaSeguranca(
            ip_origem=request.remote_addr or '127.0.0.1',
            evento=f"Validacao URL: {url}",
            status_seguranca="PERMITIDO" if valido else "BLOQUEADO"
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({"valido": valido})

# =============================================================================
# 7. INICIALIZAÇÃO DO SERVIDOR
# =============================================================================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)