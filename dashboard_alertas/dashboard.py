# Dashboard do cliente - parte do Vinícius
# Como abrir: py -m streamlit run dashboard_alertas/dashboard.py

import json
import subprocess
import sys
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PASTA_DASHBOARD = Path(__file__).parent
PASTA_PROJETO = PASTA_DASHBOARD.parent
PASTA_RELATORIOS = PASTA_DASHBOARD / "relatorios"
PASTA_EXEMPLOS = PASTA_PROJETO / "exemplos"


def aplicar_estilo():
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #07111f 0%, #101827 55%, #050810 100%);
            color: #edf6ff;
        }
        [data-testid="stSidebar"] {
            background-color: #0b1220;
            border-right: 1px solid rgba(148, 163, 184, 0.18);
        }
        .hero {
            padding: 28px;
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.22), rgba(34, 197, 94, 0.12));
            border: 1px solid rgba(125, 211, 252, 0.22);
            margin-bottom: 22px;
        }
        .hero h1 {
            margin: 0;
            font-size: 2.2rem;
            color: #f8fafc;
        }
        .hero p {
            margin: 8px 0 0 0;
            color: #bae6fd;
        }
        .card {
            background: rgba(15, 23, 42, 0.88);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
            padding: 18px;
            min-height: 118px;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.24);
        }
        .card small {
            color: #93c5fd;
            font-size: 0.86rem;
        }
        .card strong {
            display: block;
            margin-top: 8px;
            color: #f8fafc;
            font-size: 1.75rem;
            line-height: 1;
        }
        .card span {
            display: block;
            margin-top: 10px;
            color: #94a3b8;
            font-size: 0.9rem;
        }
        .section-title {
            color: #e0f2fe;
            font-size: 1.25rem;
            font-weight: 700;
            margin: 16px 0 12px 0;
        }
        .alerta {
            padding: 12px 14px;
            border-radius: 14px;
            margin-bottom: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .aviso { background: rgba(250, 204, 21, 0.12); color: #fde68a; }
        .atencao { background: rgba(249, 115, 22, 0.13); color: #fed7aa; }
        .critico { background: rgba(239, 68, 68, 0.16); color: #fecaca; }
        .ok { background: rgba(34, 197, 94, 0.14); color: #bbf7d0; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def cartao(titulo, valor, legenda):
    st.markdown(
        f"""
        <div class="card">
            <small>{escape(str(titulo))}</small>
            <strong>{escape(str(valor))}</strong>
            <span>{escape(str(legenda))}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def bloco_alerta(nivel, mensagem):
    nivel = str(nivel or "aviso").lower()
    classe = {"critico": "critico", "atencao": "atencao", "atenção": "atencao"}.get(nivel, "aviso")
    st.markdown(
        f'<div class="alerta {classe}"><strong>{escape(nivel.title())}</strong><br>{escape(str(mensagem))}</div>',
        unsafe_allow_html=True,
    )


def achar_video(caminho_no_json):
    if not caminho_no_json:
        return None
    nome = Path(caminho_no_json).name
    candidatos = [
        PASTA_PROJETO / caminho_no_json,
        PASTA_EXEMPLOS / nome,
        PASTA_PROJETO / nome,
    ]
    for candidato in candidatos:
        if candidato.is_file():
            return candidato
    return None


def numero(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


def tempo_total(refeicoes):
    total = sum(numero(item.get("duracao_s")) for item in refeicoes)
    if total >= 60:
        return f"{total / 60:.1f} min"
    return f"{total:.1f} s"


def ultima_refeicao(refeicoes):
    horarios = [item.get("inicio") for item in refeicoes if item.get("inicio")]
    return max(horarios) if horarios else "Não detectada"


def periodo(dados):
    inicio = dados.get("horario_inicio")
    fim = dados.get("horario_fim")
    if inicio and fim:
        return f"{inicio} até {fim}"
    return dados.get("data", "Não informado")


def status_geral(refeicoes, alertas):
    niveis = [str(item.get("nivel", "")).lower() for item in alertas]
    if "critico" in niveis:
        return "Crítico"
    if alertas or not refeicoes:
        return "Atenção"
    return "Normal"


def montar_tabela(refeicoes, cheiradas):
    linhas = []
    for item in refeicoes:
        linhas.append(
            {
                "Horário": item.get("inicio"),
                "Evento": "Refeição",
                "Duração (s)": numero(item.get("duracao_s")),
                "Status": "Confirmada",
            }
        )
    for item in cheiradas:
        linhas.append(
            {
                "Horário": item.get("horario"),
                "Evento": "Aproximação",
                "Duração (s)": numero(item.get("duracao_s")),
                "Status": "Sem alimentação",
            }
        )
    return pd.DataFrame(linhas)


def grafico_eventos(tabela):
    if tabela.empty:
        return None
    fig = px.bar(
        tabela,
        x="Horário",
        y="Duração (s)",
        color="Evento",
        title="Eventos registrados",
        color_discrete_map={"Refeição": "#22c55e", "Aproximação": "#38bdf8"},
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.35)",
        font_color="#e5e7eb",
        height=340,
        margin=dict(l=20, r=20, t=55, b=20),
    )
    return fig


def dashboard():
    st.set_page_config(page_title="Smart Pet Monitoring", page_icon="🐾", layout="wide")
    aplicar_estilo()
    PASTA_RELATORIOS.mkdir(exist_ok=True)

    relatorios = sorted(
        PASTA_RELATORIOS.glob("relatorio_*.json"),
        key=lambda arquivo: arquivo.stat().st_mtime,
        reverse=True,
    )
    if not relatorios:
        st.warning("Ainda não existe relatório para exibir.")
        st.info("Rode `py detectar_alimentacao.py` para gerar os relatórios.")
        return

    st.sidebar.title("Smart Pet")
    nome_relatorio = st.sidebar.selectbox("Relatório", [arquivo.name for arquivo in relatorios])

    with open(PASTA_RELATORIOS / nome_relatorio, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    refeicoes = dados.get("refeicoes") or []
    cheiradas = dados.get("cheiradas") or []
    alertas = dados.get("alertas") or []
    tabela = montar_tabela(refeicoes, cheiradas)
    video = achar_video(dados.get("video_analisado"))
    status = status_geral(refeicoes, alertas)

    st.markdown(
        """
        <div class="hero">
            <h1>Smart Pet Monitoring</h1>
            <p>Acompanhamento simples da alimentação e dos alertas do pet.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        cartao("Status", status, "Situação geral do pet")
    with col2:
        cartao("Última alimentação", ultima_refeicao(refeicoes), "Último horário detectado")
    with col3:
        cartao("Refeições", len(refeicoes), "Alimentações confirmadas")
    with col4:
        cartao("Alertas", len(alertas), "Pontos que merecem atenção")

    st.write("")
    esquerda, direita = st.columns([1.2, 1])

    with esquerda:
        st.markdown('<div class="section-title">Vídeo do monitoramento</div>', unsafe_allow_html=True)
        if video:
            st.video(str(video))
        else:
            st.info("Vídeo original não encontrado. O relatório continua disponível.")

    with direita:
        st.markdown('<div class="section-title">Resumo</div>', unsafe_allow_html=True)
        st.write(f"**Período analisado:** {periodo(dados)}")
        st.write(f"**Tempo total comendo:** {tempo_total(refeicoes)}")
        st.write(f"**Aproximações da tigela:** {len(cheiradas)}")

        st.markdown('<div class="section-title">Alertas</div>', unsafe_allow_html=True)
        if alertas:
            for item in alertas:
                bloco_alerta(item.get("nivel", "aviso"), item.get("mensagem", "Alerta detectado."))
        else:
            st.markdown(
                '<div class="alerta ok"><strong>Normal</strong><br>Nenhum alerta encontrado.</div>',
                unsafe_allow_html=True,
            )

    grafico_col, tabela_col = st.columns([1, 1])
    with grafico_col:
        st.markdown('<div class="section-title">Eventos de alimentação</div>', unsafe_allow_html=True)
        fig = grafico_eventos(tabela)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum evento registrado para montar gráfico.")

    with tabela_col:
        st.markdown('<div class="section-title">Histórico do pet</div>', unsafe_allow_html=True)
        if not tabela.empty:
            st.dataframe(tabela, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum evento registrado neste relatório.")


def _esta_no_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__":
    if _esta_no_streamlit():
        dashboard()
    else:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(Path(__file__).resolve())],
            check=False,
        )
