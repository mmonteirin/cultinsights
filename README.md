# CultInsights — Análise de Dados de Eventos Culturais

Script Python que analisa dados de eventos culturais e gera um **relatório PDF completo** com estatísticas, gráficos e insights automáticos.

Desenvolvido como extensão analítica do ecossistema [MonitoraCult](https://github.com/mmonteirin) — app de descoberta de experiências culturais em Fortaleza.

---

## O que o relatório entrega

- **Indicadores gerais** — total de eventos, público, receita, ocupação média, ticket médio
- **Distribuição por categoria** — quais tipos de evento dominam a programação
- **Ocupação média** — categorias com melhor e pior aproveitamento de capacidade
- **Evolução da receita** — série temporal mês a mês
- **Público por bairro** — onde os eventos atraem mais pessoas
- **Mapa de calor** — dias da semana × horários com maior público médio
- **Top 10 eventos** — por público e por receita
- **Insights automáticos** — conclusões geradas a partir dos dados

---

## Demo

```bash
# Relatório completo
python src/main.py

# Filtrar por categoria
python src/main.py --categoria "Show Musical"

# Filtrar por bairro
python src/main.py --bairro "Meireles"

# Customizar caminhos
python src/main.py --input meus_dados.csv --output meu_relatorio.pdf
```

---

## Estrutura do projeto

```
cultinsights/
├── data/
│   ├── eventos.csv           # Dataset de exemplo (350 eventos)
│   └── generate_dataset.py   # Gerador de dados sintéticos
├── src/
│   └── main.py               # Script principal
├── output/                   # PDFs gerados (ignorado pelo git)
├── requirements.txt
└── README.md
```

---

## Formato do CSV de entrada

| Campo | Tipo | Descrição |
|---|---|---|
| `nome_evento` | string | Nome do evento |
| `categoria` | string | Tipo (Show Musical, Teatro, Festival...) |
| `local` | string | Nome do local |
| `bairro` | string | Bairro do evento |
| `data` | YYYY-MM-DD | Data do evento |
| `hora` | HH:MM | Horário de início |
| `capacidade` | int | Capacidade total do espaço |
| `publico` | int | Público presente |
| `ocupacao_pct` | float | Taxa de ocupação (0.0 a 1.0) |
| `preco_ingresso` | float | Valor do ingresso (0 = gratuito) |
| `receita_total` | float | Receita total do evento |
| `gratuito` | bool | Se o evento foi gratuito |

---

## Instalação

```bash
git clone https://github.com/mmonteirin/cultinsights
cd cultinsights
pip install -r requirements.txt

# Gerar dataset de exemplo
python data/generate_dataset.py

# Rodar análise
python src/main.py
```

---

## Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat)
![Seaborn](https://img.shields.io/badge/Seaborn-4C72B0?style=flat)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF-red?style=flat)
![Click](https://img.shields.io/badge/Click-CLI-green?style=flat)

---

*Desenvolvido por [Marcos Monteiro](https://github.com/mmonteirin)*
# cultinsights
