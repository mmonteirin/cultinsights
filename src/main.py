"""
CultInsights — Análise de Dados de Eventos Culturais
Gera relatório PDF completo com estatísticas e gráficos.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
import os
import click
from datetime import datetime

# ── Paleta ──────────────────────────────────────────────────────────────────
VERDE = "#1a4731"
VERDE_MED = "#2d6a4f"
VERDE_CLARO = "#52b788"
CREME = "#f5f5f0"
CINZA = "#555555"
ACCENT = "#d4a843"

PALETTE = [VERDE, VERDE_MED, VERDE_CLARO, ACCENT, "#74c69d", "#95d5b2",
           "#b7e4c7", "#e9c46a", "#f4a261", "#e76f51"]

sns.set_theme(style="whitegrid", palette=PALETTE)
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


# ── Helpers ──────────────────────────────────────────────────────────────────
def fig_to_image(fig, width=15*cm, height=9*cm):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    buf.seek(0)
    plt.close(fig)
    img = Image(buf, width=width, height=height)
    return img


def fmt_brl(value):
    return f"R$ {value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(value):
    return f"{value * 100:.1f}%"


# ── Gráficos ─────────────────────────────────────────────────────────────────
def plot_eventos_por_categoria(df):
    counts = df["categoria"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.barh(counts.index, counts.values, color=PALETTE[:len(counts)], edgecolor="white")
    for bar, val in zip(bars, counts.values):
        ax.text(val + 1, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=9, color=CINZA)
    ax.set_xlabel("Número de eventos", fontsize=9, color=CINZA)
    ax.set_title("Eventos por Categoria", fontsize=12, fontweight="bold", color=VERDE, pad=10)
    ax.invert_yaxis()
    fig.tight_layout()
    return fig_to_image(fig)


def plot_ocupacao_por_categoria(df):
    media = df.groupby("categoria")["ocupacao_pct"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(media.index, media.values * 100, color=PALETTE[:len(media)], edgecolor="white")
    for bar, val in zip(bars, media.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val*100:.0f}%", ha="center", va="bottom", fontsize=8, color=CINZA)
    ax.set_ylabel("Ocupação média (%)", fontsize=9, color=CINZA)
    ax.set_title("Ocupação Média por Categoria", fontsize=12, fontweight="bold", color=VERDE, pad=10)
    ax.set_ylim(0, 110)
    plt.xticks(rotation=25, ha="right", fontsize=8)
    fig.tight_layout()
    return fig_to_image(fig)


def plot_receita_mensal(df):
    df2 = df.copy()
    df2["mes"] = pd.to_datetime(df2["data"]).dt.to_period("M")
    mensal = df2.groupby("mes")["receita_total"].sum().reset_index()
    mensal["mes_str"] = mensal["mes"].astype(str)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.fill_between(mensal["mes_str"], mensal["receita_total"],
                    alpha=0.25, color=VERDE_CLARO)
    ax.plot(mensal["mes_str"], mensal["receita_total"],
            color=VERDE, linewidth=2.5, marker="o", markersize=4)
    ax.set_ylabel("Receita (R$)", fontsize=9, color=CINZA)
    ax.set_title("Receita Total por Mês", fontsize=12, fontweight="bold", color=VERDE, pad=10)
    step = max(1, len(mensal) // 10)
    ax.set_xticks(range(0, len(mensal), step))
    ax.set_xticklabels(mensal["mes_str"].iloc[::step], rotation=30, ha="right", fontsize=7)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"R${x/1000:.0f}k"))
    fig.tight_layout()
    return fig_to_image(fig, width=17*cm, height=7*cm)


def plot_publico_por_bairro(df):
    bairro = df.groupby("bairro")["publico"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(bairro.index, bairro.values, color=PALETTE[:len(bairro)], edgecolor="white")
    for bar, val in zip(bars, bairro.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50,
                f"{val:,.0f}", ha="center", va="bottom", fontsize=7.5, color=CINZA)
    ax.set_ylabel("Total de público", fontsize=9, color=CINZA)
    ax.set_title("Público Total por Bairro", fontsize=12, fontweight="bold", color=VERDE, pad=10)
    plt.xticks(rotation=25, ha="right", fontsize=8)
    fig.tight_layout()
    return fig_to_image(fig)


def plot_heatmap_dia_hora(df):
    df2 = df.copy()
    df2["dia_semana"] = pd.to_datetime(df2["data"]).dt.day_name()
    ordem_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    labels_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    pivot = df2.groupby(["dia_semana", "hora"])["publico"].mean().unstack(fill_value=0)
    pivot = pivot.reindex([d for d in ordem_dias if d in pivot.index])

    fig, ax = plt.subplots(figsize=(9, 4))
    sns.heatmap(pivot, ax=ax, cmap="YlGn", linewidths=0.5, linecolor="white",
                fmt=".0f", annot=True, annot_kws={"size": 7},
                cbar_kws={"label": "Público médio"})
    ax.set_title("Público Médio por Dia da Semana e Horário",
                 fontsize=12, fontweight="bold", color=VERDE, pad=10)
    ax.set_ylabel("")
    ax.set_xlabel("")
    dias_presentes = [d for d in ordem_dias if d in pivot.index]
    ax.set_yticklabels([labels_pt[ordem_dias.index(d)] for d in dias_presentes],
                       rotation=0, fontsize=8)
    plt.xticks(fontsize=8)
    fig.tight_layout()
    return fig_to_image(fig, width=16*cm, height=8*cm)


def plot_top_eventos(df):
    top = df.nlargest(10, "publico")[["nome_evento", "categoria", "publico", "receita_total"]]
    top["nome_curto"] = top["nome_evento"].str[:35] + "..."
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(top["nome_curto"], top["publico"],
                   color=[PALETTE[i % len(PALETTE)] for i in range(len(top))],
                   edgecolor="white")
    for bar, val in zip(bars, top["publico"]):
        ax.text(val + 10, bar.get_y() + bar.get_height() / 2,
                f"{val:,}", va="center", fontsize=8, color=CINZA)
    ax.set_xlabel("Público", fontsize=9, color=CINZA)
    ax.set_title("Top 10 Eventos por Público", fontsize=12, fontweight="bold", color=VERDE, pad=10)
    ax.invert_yaxis()
    plt.yticks(fontsize=7.5)
    fig.tight_layout()
    return fig_to_image(fig, height=10*cm)


# ── Estilos PDF ──────────────────────────────────────────────────────────────
def build_styles():
    styles = getSampleStyleSheet()
    custom = {
        "titulo": ParagraphStyle("titulo", fontSize=26, textColor=colors.white,
                                 fontName="Helvetica-Bold", alignment=TA_LEFT, spaceAfter=4),
        "subtitulo": ParagraphStyle("subtitulo", fontSize=13, textColor=colors.HexColor("#A8D5B5"),
                                    fontName="Helvetica", alignment=TA_LEFT),
        "secao": ParagraphStyle("secao", fontSize=13, textColor=colors.HexColor(VERDE),
                                fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4),
        "corpo": ParagraphStyle("corpo", fontSize=9.5, textColor=colors.HexColor(CINZA),
                                fontName="Helvetica", spaceAfter=6, leading=14),
        "rodape": ParagraphStyle("rodape", fontSize=7.5, textColor=colors.HexColor("#999999"),
                                 fontName="Helvetica", alignment=TA_CENTER),
        "kpi_val": ParagraphStyle("kpi_val", fontSize=20, textColor=colors.HexColor(VERDE),
                                  fontName="Helvetica-Bold", alignment=TA_CENTER),
        "kpi_lbl": ParagraphStyle("kpi_lbl", fontSize=8, textColor=colors.HexColor(CINZA),
                                  fontName="Helvetica", alignment=TA_CENTER),
    }
    return {**{k: styles[k] for k in styles.byName}, **custom}


def build_kpi_table(kpis, styles):
    cells = []
    for label, value in kpis:
        cells.append([
            Paragraph(value, styles["kpi_val"]),
            Paragraph(label, styles["kpi_lbl"]),
        ])
    rows = [cells[i:i+4] for i in range(0, len(cells), 4)]
    table_data = []
    for row in rows:
        table_data.append([cell[0] for cell in row])
        table_data.append([cell[1] for cell in row])

    t = Table(table_data, colWidths=[4.2*cm]*4)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(CREME)),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER_COLOR := "#d0d0c8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor(BORDER_COLOR)),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def build_top_table(df, styles):
    top = df.nlargest(5, "receita_total")[
        ["nome_evento", "categoria", "publico", "ocupacao_pct", "receita_total"]
    ]
    header = ["Evento", "Categoria", "Público", "Ocupação", "Receita"]
    rows = [header]
    for _, r in top.iterrows():
        rows.append([
            r["nome_evento"][:40],
            r["categoria"],
            f"{r['publico']:,}",
            fmt_pct(r["ocupacao_pct"]),
            fmt_brl(r["receita_total"]),
        ])
    t = Table(rows, colWidths=[6.5*cm, 3*cm, 2*cm, 2.2*cm, 3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(VERDE)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor(CREME), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


# ── PDF Builder ──────────────────────────────────────────────────────────────
def build_pdf(df, output_path):
    styles = build_styles()
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=0.5*cm, bottomMargin=1.5*cm,
        title="CultInsights — Relatório de Eventos Culturais"
    )

    story = []

    # ── Cabeçalho ──
    header_data = [[
        Paragraph("CultInsights", styles["titulo"]),
        Paragraph("Relatório de Análise de Eventos Culturais", styles["subtitulo"]),
        Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
                  ParagraphStyle("data_header", fontSize=8, textColor=colors.HexColor("#A8D5B5"),
                                 fontName="Helvetica", alignment=TA_RIGHT)),
    ]]
    header_table = Table(header_data, colWidths=[6*cm, 8*cm, 3*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(VERDE)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*cm))

    # ── KPIs ──
    receita_total = df["receita_total"].sum()
    publico_total = df["publico"].sum()
    ocupacao_media = df["ocupacao_pct"].mean()
    gratuitos = df["gratuito"].sum()

    kpis = [
        ("Total de Eventos", str(len(df))),
        ("Público Total", f"{publico_total:,}".replace(",", ".")),
        ("Receita Total", fmt_brl(receita_total)),
        ("Ocupação Média", fmt_pct(ocupacao_media)),
        ("Categorias", str(df["categoria"].nunique())),
        ("Bairros", str(df["bairro"].nunique())),
        ("Eventos Gratuitos", str(gratuitos)),
        ("Ticket Médio", fmt_brl(df[df["preco_ingresso"] > 0]["preco_ingresso"].mean())),
    ]
    story.append(Paragraph("Indicadores Gerais", styles["secao"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d0d0c8")))
    story.append(Spacer(1, 0.2*cm))
    story.append(build_kpi_table(kpis, styles))
    story.append(Spacer(1, 0.5*cm))

    # ── Gráficos página 1 ──
    story.append(Paragraph("Distribuição e Ocupação por Categoria", styles["secao"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d0d0c8")))
    story.append(Spacer(1, 0.2*cm))

    g1 = plot_eventos_por_categoria(df)
    g2 = plot_ocupacao_por_categoria(df)
    row = Table([[g1, g2]], colWidths=[8.5*cm, 8.5*cm])
    row.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"),
                              ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(row)
    story.append(Spacer(1, 0.4*cm))

    # ── Receita mensal ──
    story.append(Paragraph("Evolução da Receita", styles["secao"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d0d0c8")))
    story.append(Spacer(1, 0.2*cm))
    story.append(plot_receita_mensal(df))
    story.append(PageBreak())

    # ── Página 2 ──
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Público por Bairro e Mapa de Calor", styles["secao"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d0d0c8")))
    story.append(Spacer(1, 0.2*cm))

    g3 = plot_publico_por_bairro(df)
    row2 = Table([[g3]], colWidths=[17*cm])
    row2.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(row2)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Horários de Maior Público", styles["secao"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d0d0c8")))
    story.append(Spacer(1, 0.2*cm))
    story.append(plot_heatmap_dia_hora(df))
    story.append(PageBreak())

    # ── Página 3 ──
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Top 10 Eventos por Público", styles["secao"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d0d0c8")))
    story.append(Spacer(1, 0.2*cm))
    story.append(plot_top_eventos(df))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Top 5 Eventos por Receita", styles["secao"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d0d0c8")))
    story.append(Spacer(1, 0.2*cm))
    story.append(build_top_table(df, styles))
    story.append(Spacer(1, 0.6*cm))

    # ── Insights ──
    story.append(Paragraph("Insights Principais", styles["secao"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d0d0c8")))
    story.append(Spacer(1, 0.2*cm))

    cat_top = df.groupby("categoria")["receita_total"].sum().idxmax()
    cat_ocup = df.groupby("categoria")["ocupacao_pct"].mean().idxmax()
    bairro_top = df.groupby("bairro")["publico"].sum().idxmax()
    hora_top = df.groupby("hora")["publico"].mean().idxmax()
    df["dia_semana"] = pd.to_datetime(df["data"]).dt.day_name()
    dias_pt = {"Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta",
               "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado", "Sunday": "Domingo"}
    dia_top_en = df.groupby("dia_semana")["publico"].mean().idxmax()
    dia_top = dias_pt.get(dia_top_en, dia_top_en)

    insights = [
        f"• A categoria <b>{cat_top}</b> gerou a maior receita total no período analisado.",
        f"• <b>{cat_ocup}</b> apresentou a maior taxa de ocupação média entre todas as categorias.",
        f"• O bairro <b>{bairro_top}</b> concentrou o maior volume de público nos eventos.",
        f"• O horário de pico é <b>{hora_top}</b>, com maior média de público por evento.",
        f"• <b>{dia_top}</b> é o dia da semana com melhor desempenho médio de público.",
        f"• <b>{gratuitos}</b> eventos foram gratuitos ({gratuitos/len(df)*100:.1f}% do total).",
    ]
    for insight in insights:
        story.append(Paragraph(insight, styles["corpo"]))

    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"CultInsights · Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')} · "
        "github.com/mmonteirin",
        styles["rodape"]
    ))

    doc.build(story)
    print(f"✅ Relatório gerado: {output_path}")


# ── CLI ──────────────────────────────────────────────────────────────────────
@click.command()
@click.option("--input", "-i", default="data/eventos.csv",
              help="Caminho para o CSV de eventos", show_default=True)
@click.option("--output", "-o", default="output/relatorio_cultinsights.pdf",
              help="Caminho do PDF gerado", show_default=True)
@click.option("--categoria", "-c", default=None,
              help="Filtrar por categoria específica")
@click.option("--bairro", "-b", default=None,
              help="Filtrar por bairro específico")
def main(input, output, categoria, bairro):
    """CultInsights — Gerador de relatório PDF de eventos culturais."""
    click.echo("📊 CultInsights — Carregando dados...")
    df = pd.read_csv(input)

    if categoria:
        df = df[df["categoria"].str.lower() == categoria.lower()]
        click.echo(f"   Filtrado por categoria: {categoria} ({len(df)} eventos)")
    if bairro:
        df = df[df["bairro"].str.lower() == bairro.lower()]
        click.echo(f"   Filtrado por bairro: {bairro} ({len(df)} eventos)")

    if df.empty:
        click.echo("❌ Nenhum dado encontrado com os filtros aplicados.")
        return

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    click.echo(f"   {len(df)} eventos carregados. Gerando relatório...")
    build_pdf(df, output)


if __name__ == "__main__":
    main()
