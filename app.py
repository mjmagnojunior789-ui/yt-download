import streamlit as st
import yt_dlp
import os
import tempfile

# 1. Configuração da página e Estilo Hooklabs (Dark Mode Premium)
st.set_page_config(
    page_title="Edit-videos Downloader",
    page_icon="📥",
    layout="centered"
)

# Estilização customizada em CSS injetado
st.markdown("""
    <style>
    /* Fundo geral e fonte */
    .stApp {
        background-color: #0d0e12;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Container principal */
    div.block-container {
        background-color: #15171e;
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        border: 1px solid #222530;
        margin-top: 2rem;
    }
    
    /* Inputs de texto */
    .stTextInput>div>div>input {
        background-color: #1a1d26 !important;
        color: #ffffff !important;
        border: 1px solid #2d3142 !important;
        border-radius: 8px !important;
        padding: 10px 14px;
    }
    .stTextInput>div>div>input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }
    
    /* Botões personalizados */
    div.stButton > button {
        background-color: #6366f1 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #4f46e5 !important;
        transform: translateY(-1px);
    }
    
    /* Dropdowns e Selectbox */
    .stSelectbox>div>div {
        background-color: #1a1d26 !important;
        border: 1px solid #2d3142 !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* Alinhamento de Títulos */
    h1 {
        font-weight: 800;
        letter-spacing: -1px;
        color: #ffffff;
        text-align: center;
        margin-bottom: 5px;
    }
    .subtitle {
        text-align: center;
        color: #9ca3af;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho do App (Estilo Hooklabs)
st.markdown("<h1>EDITORS-VIDEOS <span style='color:#6366f1'>DOWNLOADER</span></h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Baixe seus vídeos e áudios favoritos do YouTube de forma rápida e limpa.</p>", unsafe_allow_html=True)

# 2. Input do Usuário
url = st.text_input("Cole o link do YouTube aqui:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    try:
        # Busca informações do vídeo antes de baixar (para exibir miniatura e opções de qualidade)
        with st.spinner("Buscando informações do vídeo..."):
            ydl_opts = {}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Vídeo Sem Título')
                thumbnail = info.get('thumbnail')
                duration_seconds = info.get('duration', 0)
                
        # Exibe um card minimalista com os dados do vídeo encontrado
        col1, col2 = st.columns([1, 2])
        with col1:
            if thumbnail:
                st.image(thumbnail, use_container_width=True)
        with col2:
            st.markdown(f"**Título:** {video_title}")
            st.markdown(f"**Duração:** {duration_seconds // 60}m {duration_seconds % 60}s")

        st.divider()

        # Opções de Configuração de Download
        format_type = st.radio("O que você deseja baixar?", ["Apenas Música (MP3)", "Vídeo Completo (MP4)"], horizontal=True)

        if format_type == "Apenas Música (MP3)":
            quality = st.selectbox("Selecione a qualidade do áudio:", ["320 kbps (Alta)", "192 kbps (Média)", "128 kbps (Econômica)"])
            # Mapeia a seleção para o kbps real
            quality_map = {"320 kbps (Alta)": "320", "192 kbps (Média)": "192", "128 kbps (Econômica)": "128"}
            selected_quality = quality_map[quality]
        else:
            quality = st.selectbox("Selecione a resolução do vídeo:", ["1080p (Full HD)", "720p (HD)", "480p (Padrão)"])
            # Mapeia as opções para os filtros do yt-dlp
            quality_map = {
                "1080p (Full HD)": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                "720p (HD)": "bestvideo[height<=720]+bestaudio/best[height<=720]",
                "480p (Padrão)": "bestvideo[height<=480]+bestaudio/best[height<=480]"
            }
            selected_quality = quality_map[quality]

        # Botão para processar o download no servidor e disponibilizar para o usuário
        if st.button("Preparar Download"):
            with st.spinner("Processando arquivo... Isso pode levar alguns segundos."):
                # Criando um diretório temporário para salvar o arquivo processado
                temp_dir = tempfile.gettempdir()
                
                if format_type == "Apenas Música (MP3)":
                    out_template = os.path.join(temp_dir, f"{video_title}.%(ext)s")
                    ydl_opts_download = {
                        'format': 'bestaudio/best',
                        'outtmpl': out_template,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': selected_quality,
                        }],
                    }
                    expected_ext = "mp3"
                else:
                    # Baixa vídeo + áudio e junta em MP4
                    out_template = os.path.join(temp_dir, f"{video_title}.mp4")
                    ydl_opts_download = {
                        'format': selected_quality,
                        'outtmpl': out_template,
                        'merge_output_format': 'mp4',
                    }
                    expected_ext = "mp4"

                # Executa o download
                with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                    ydl.download([url])
                
                # Caminho final do arquivo salvo
                final_file_path = os.path.join(temp_dir, f"{video_title}.{expected_ext}")

                # Lê o arquivo binário para disponibilizá-lo no Streamlit
                if os.path.exists(final_file_path):
                    with open(final_file_path, "rb") as f:
                        file_bytes = f.read()
                    
                    st.success("🎉 Arquivo preparado com sucesso!")
                    st.download_button(
                        label="Clique aqui para Baixar seu arquivo",
                        data=file_bytes,
                        file_name=f"{video_title}.{expected_ext}",
                        mime="audio/mpeg" if expected_ext == "mp3" else "video/mp4"
                    )
                    
                    # Limpa o arquivo do servidor temporário após a leitura
                    try:
                        os.remove(final_file_path)
                    except Exception:
                        pass
                else:
                    st.error("Ocorreu um erro ao processar o arquivo. Tente novamente.")

    except Exception as e:
        st.error(f"Erro ao processar o link: {str(e)}")
