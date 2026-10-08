import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Streaming Analytics G1", page_icon="🎬", layout="wide")


@st.cache_data
def carregar_dados():
    df = pd.read_csv("dados/simulacao_streaming_brasil.csv")
    df["data"] = pd.to_datetime(df["data"])
    return df


df = carregar_dados()


st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3010/3010973.png", width=100)
st.sidebar.title("Filtros Interativos")

anos = st.sidebar.multiselect(
    "Ano", options=sorted(df["ano"].unique()), default=sorted(df["ano"].unique())
)
meses = st.sidebar.multiselect(
    "Mês", options=sorted(df["mes"].unique()), default=sorted(df["mes"].unique())
)
plataformas = st.sidebar.multiselect(
    "Plataforma", options=df["plataforma"].unique(), default=df["plataforma"].unique()
)
categorias = st.sidebar.multiselect(
    "Categoria", options=df["categoria"].unique(), default=df["categoria"].unique()
)
generos = st.sidebar.multiselect(
    "Gênero", options=df["genero"].unique(), default=df["genero"].unique()
)

titulos_disponiveis = df["titulo"].unique()
titulos = st.sidebar.multiselect("Conteúdo (Opcional)", options=titulos_disponiveis)


df_filtrado = df[
    (df["ano"].isin(anos))
    & (df["mes"].isin(meses))
    & (df["plataforma"].isin(plataformas))
    & (df["categoria"].isin(categorias))
    & (df["genero"].isin(generos))
]

if titulos:
    df_filtrado = df_filtrado[df_filtrado["titulo"].isin(titulos)]


st.title("🎬 Projeto G1 - Análise de Streaming de Música e Filmes")
st.markdown("""
**Descrição do Problema:** Os serviços de streaming transformaram a forma como consumimos mídia. 
Este dashboard visa analisar um grande volume de dados de audiência para identificar **padrões de consumo**, 
**tendências culturais** e a **evolução das plataformas** entre 2015 e o período recente, ajudando a traçar o perfil 
do consumidor digital brasileiro de forma profissional e interativa.
""")


st.subheader("Indicadores de Desempenho (KPIs)")
if not df_filtrado.empty:
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    total_reproducoes = df_filtrado["reproducoes"].sum()
    plat_popular = df_filtrado.groupby("plataforma")["reproducoes"].sum().idxmax()
    cont_reproduzido = df_filtrado.groupby("titulo")["reproducoes"].sum().idxmax()
    receita_total = df_filtrado["receita_plataforma"].sum()
    media_usuarios = int(df_filtrado["usuarios_ativos"].mean())
    genero_consumido = df_filtrado.groupby("genero")["reproducoes"].sum().idxmax()

    col1.metric("Total de Reproduções", f"{total_reproducoes:,.0f}".replace(",", "."))
    col2.metric("Plataforma + Popular", plat_popular)
    col3.metric("Conteúdo Top #1", cont_reproduzido)
    col4.metric("Receita Total (R$)", f"R$ {receita_total:,.2f}".replace(",", "."))
    col5.metric("Média Usuários Ativos", f"{media_usuarios:,.0f}".replace(",", "."))
    col6.metric("Gênero Preferido", genero_consumido)
else:
    st.warning("Nenhum dado encontrado para os filtros aplicados.")

st.divider()


aba1, aba2, aba3, aba4 = st.tabs(
    [
        "📊 Visão Geral",
        "📈 Análise Temporal Avançada",
        "🧩 Comportamento & Correlação",
        "📋 Tabela e Conclusão",
    ]
)

if not df_filtrado.empty:
    with aba1:
        col_a, col_b = st.columns(2)
        with col_a:
            fig_plat = px.bar(
                df_filtrado.groupby("plataforma")["reproducoes"].sum().reset_index(),
                x="plataforma",
                y="reproducoes",
                color="plataforma",
                title="Comparação Digital: Reproduções por Plataforma",
            )
            st.plotly_chart(fig_plat, use_container_width=True)

        with col_b:
            fig_gen = px.bar(
                df_filtrado.groupby("genero")["reproducoes"]
                .sum()
                .reset_index()
                .sort_values(by="reproducoes"),
                x="reproducoes",
                y="genero",
                orientation="h",
                color="genero",
                title="Preferências do Público: Reproduções por Gênero",
            )
            st.plotly_chart(fig_gen, use_container_width=True)

    with aba2:
        st.markdown(
            "### Evolução do Consumo (Com Séries Temporais Avançadas - Média Móvel)"
        )
        temp_df = (
            df_filtrado.groupby("data")["reproducoes"]
            .sum()
            .reset_index()
            .sort_values("data")
        )
        temp_df["Media_Movel_3meses"] = (
            temp_df["reproducoes"].rolling(window=3, min_periods=1).mean()
        )

        fig_temp = go.Figure()
        fig_temp.add_trace(
            go.Scatter(
                x=temp_df["data"],
                y=temp_df["reproducoes"],
                mode="lines",
                name="Reproduções",
                line=dict(color="blue", width=1),
            )
        )
        fig_temp.add_trace(
            go.Scatter(
                x=temp_df["data"],
                y=temp_df["Media_Movel_3meses"],
                mode="lines",
                name="Média Móvel",
                line=dict(color="red", width=3),
            )
        )
        fig_temp.update_layout(title="Linha Temporal: Evolução das Reproduções")
        st.plotly_chart(fig_temp, use_container_width=True)

    with aba3:
        col_c, col_d = st.columns(2)
        with col_c:
            heatmap_data = pd.crosstab(
                df_filtrado["horario_pico"], df_filtrado["plataforma"]
            )
            fig_heat = px.imshow(
                heatmap_data,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Oranges",
                title="Horários de Pico por Plataforma",
            )
            st.plotly_chart(fig_heat, use_container_width=True)

        with col_d:
            fig_scatter = px.scatter(
                df_filtrado,
                x="avaliacao_media",
                y="reproducoes",
                color="categoria",
                title="Correlação: Avaliação Média vs. Reproduções",
                hover_data=["titulo", "plataforma"],
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    with aba4:
        st.markdown("### Exploração Detalhada (Tabela Dinâmica)")
        st.dataframe(
            df_filtrado[
                [
                    "data",
                    "plataforma",
                    "categoria",
                    "genero",
                    "titulo",
                    "reproducoes",
                    "avaliacao_media",
                ]
            ],
            use_container_width=True,
        )

        st.divider()
        st.markdown("### 📝 Interpretação Textual")
        st.write("""
        - A visualização em gráficos de barras nos permite confirmar os **líderes de engajamento** em determinadas categorias.
        - Analisando as séries temporais com a linha de **média móvel**, notamos os reflexos do tempo na adesão a mídias de streaming.
        - O Heatmap de horários de pico nos mostra os momentos de maior retenção dos usuários, indicando o melhor momento para eventuais campanhas de marketing ou lançamentos de temporada.
        - O gráfico de dispersão revela que nem sempre uma alta **avaliação média** se reflete no conteúdo **mais reproduzido**, indicando que a acessibilidade ou o "hype" podem superar a nota crítica no primeiro momento.
        """)

        st.markdown("### 🎯 Conclusão Executiva")
        st.success("""
        **Conclusão Geral do Projeto:**
        O presente estudo valida a escalabilidade dos serviços digitais no Brasil. O padrão cultural de consumo aponta para um pico noturno, onde conteúdos de curta/média duração (músicas/podcasts) competem pela atenção do usuário junto às produções audiovisuais extensas. Para futuras estratégias, as plataformas devem priorizar investimentos nos gêneros que historicamente seguram a métrica de "Tempo Médio de Consumo", aliando esse engajamento orgânico a pacotes de assinaturas atrativos.
        """)
