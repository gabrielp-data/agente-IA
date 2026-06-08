import streamlit as st
import sqlite3
import json
import boto3
import os

st.set_page_config(
    page_title="CineBot",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"], .stApp {
    background: #08080a !important;
    color: #ede8de !important;
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d0d10 !important;
    border-right: 1px solid #1a1a22 !important;
}
[data-testid="stSidebar"] .block-container { padding: 2rem 1.5rem !important; }

.brand {
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #1a1a22;
}
.brand-title {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: #ede8de;
    line-height: 1;
    margin-bottom: 4px;
}
.brand-title span { color: #d4a843; }
.brand-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: #3a3a48;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: #d4a843;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin: 1.5rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, #d4a84344, transparent); }

.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid #111116;
    font-size: 12px;
}
.info-key { color: #44444e; font-family: 'JetBrains Mono', monospace; font-size: 10px; }
.info-val { color: #d4a843; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 500; }

.online-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: rgba(42,157,92,0.1);
    border: 1px solid rgba(42,157,92,0.3);
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: #2a9d5c;
    letter-spacing: 0.1em;
}
.online-dot { width: 5px; height: 5px; border-radius: 50%; background: #2a9d5c; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* ── Main ── */
.page-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #1a1a22;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 36px;
    font-weight: 800;
    color: #ede8de;
    line-height: 1;
}
.page-title em { color: #d4a843; font-style: normal; }
.page-desc { font-size: 13px; color: #44444e; margin-top: 6px; font-weight: 300; }

/* ── Suggestion buttons ── */
.stButton > button {
    background: #0f0f14 !important;
    color: #6b6760 !important;
    border: 1px solid #1a1a22 !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    padding: 0.5rem 0.8rem !important;
    text-align: left !important;
    transition: all 0.15s !important;
    width: 100% !important;
}
.stButton > button:hover {
    border-color: #d4a843 !important;
    color: #d4a843 !important;
    background: rgba(212,168,67,0.05) !important;
}

/* ── Send button override ── */
.send-btn > button {
    background: #d4a843 !important;
    color: #08080a !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.5rem !important;
}
.send-btn > button:hover { background: #e8b84e !important; }

/* ── Input ── */
.stTextInput > div > div > input {
    background: #0f0f14 !important;
    border: 1px solid #1a1a22 !important;
    border-radius: 6px !important;
    color: #ede8de !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 16px !important;
    padding: 0.8rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(212,168,67,0.5) !important;
    box-shadow: 0 0 0 2px rgba(212,168,67,0.08) !important;
}
.stTextInput > div > div > input::placeholder { color: #2a2a36 !important; }
.stTextInput > label { display: none !important; }

/* ── Password / Select ── */
.stSelectbox > div > div {
    background: #0f0f14 !important;
    border: 1px solid #1a1a22 !important;
    border-radius: 6px !important;
}
.stSelectbox label {
    font-size: 11px !important;
    color: #44444e !important;
    font-family: 'JetBrains Mono', monospace !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* ── Chat bubbles ── */
.chat-wrap { display: flex; flex-direction: column; gap: 20px; margin: 1.5rem 0; }

.bubble-user {
    align-self: flex-end;
    max-width: 70%;
    background: #131318;
    border: 1px solid #1a1a22;
    border-radius: 12px 12px 2px 12px;
    padding: 14px 18px;
    font-size: 16px;
    line-height: 1.65;
    color: #c8c3b8;
}

.bubble-bot {
    align-self: flex-start;
    max-width: 80%;
    background: #0d0d12;
    border: 1px solid #1a1a22;
    border-left: 3px solid #d4a843;
    border-radius: 2px 12px 12px 12px;
    padding: 18px 20px;
    font-size: 16px;
    line-height: 1.8;
    color: #ede8de;
    font-weight: 300;
}

.bubble-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.bubble-label.user { color: #2a2a36; text-align: right; }
.bubble-label.bot { color: rgba(212,168,67,0.5); }

.msg-group { display: flex; flex-direction: column; }
.msg-group.user { align-items: flex-end; }
.msg-group.bot { align-items: flex-start; }

/* ── Divider ── */
.chat-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 8px 0;
    opacity: 0.15;
}
.chat-divider::before, .chat-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #ede8de;
}
.chat-divider span {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #ede8de;
}

/* ── Welcome ── */
.welcome {
    padding: 3rem 0 1rem;
    text-align: center;
    border-bottom: 1px solid #1a1a22;
    margin-bottom: 1.5rem;
}
.welcome-icon { font-size: 48px; margin-bottom: 16px; }
.welcome-title {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: #ede8de;
    margin-bottom: 8px;
}
.welcome-title span { color: #d4a843; }
.welcome-desc {
    font-size: 14px;
    color: #44444e;
    line-height: 1.6;
    max-width: 400px;
    margin: 0 auto 24px;
    font-weight: 300;
}

/* ── Input area ── */
.stForm { background: transparent !important; border: none !important; padding: 0 !important; }

/* ── Alert / Error ── */
.stAlert { border-radius: 6px !important; }

/* ── Suggestions grid label ── */
.sug-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: #2a2a36;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* ── Stats chips ── */
.stat-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: rgba(212,168,67,0.08);
    border: 1px solid rgba(212,168,67,0.2);
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #d4a843;
}
</style>
""", unsafe_allow_html=True)

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), 'movies.db')

def query_db(sql: str) -> str:
    if not sql.strip().upper().startswith("SELECT"):
        return "Erro: apenas SELECT é permitido."
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql.strip()).fetchall()
        conn.close()
        return json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2) if rows else "Nenhum resultado."
    except Exception as e:
        return f"SQL Error: {e}"

def get_schema() -> str:
    return """Tabela: movies (12.404 filmes reais do IMDb)
Colunas:
  imdb_id TEXT, title TEXT, year INTEGER, genre TEXT, director TEXT DEFAULT empty, cast TEXT DEFAULT empty
  rating REAL (nota IMDb 0-10), votes INTEGER
  runtime INTEGER (minutos), language TEXT, country TEXT
  overview TEXT (sinopse)
  oscars_won INTEGER (Oscars ganhos)
  oscars_nominated INTEGER (indicações ao Oscar)
  box_office_million_usd REAL (bilheteria em milhões USD)
  metascore INTEGER (nota da crítica 0-100)"""

TOOLS = [
    {
        "name": "get_schema",
        "description": "Retorna o schema do banco. Use sempre que precisar saber os nomes das colunas.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "query_movies_db",
        "description": "Executa SQL SELECT no banco de filmes. Use para qualquer pergunta sobre dados.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "SQLite SELECT válido. Use LIKE para buscas de texto. Limite 10 resultados por padrão."}
            },
            "required": ["sql"]
        }
    }
]

SYSTEM_PROMPT = """Você é o CineBot, um agente especialista em cinema com acesso a banco de 115 filmes com dados do IMDb, Oscar e bilheteria.

Opere como agente ReAct: Razão → Ação (ferramenta) → Observação → Repita até ter resposta completa.

SEMPRE use as ferramentas para dados concretos. NUNCA invente números ou fatos.
Responda em português brasileiro de forma clara, direta e apaixonada por cinema.
Use emojis com moderação para deixar as respostas mais visuais.
Formate listas de filmes de forma legível."""

def run_agent(user_message: str, history: list, key_id: str, secret: str, session_token: str, region: str) -> str:
    kwargs = dict(service_name='bedrock-runtime', region_name=region,
                  aws_access_key_id=key_id, aws_secret_access_key=secret)
    if session_token:
        kwargs['aws_session_token'] = session_token
    bedrock = boto3.client(**kwargs)
    messages = history + [{"role": "user", "content": user_message}]

    for _ in range(10):
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1500,
            "system": SYSTEM_PROMPT,
            "tools": TOOLS,
            "messages": messages
        })
        result = json.loads(bedrock.invoke_model(modelId="anthropic.claude-3-5-sonnet-20241022-v2:0", body=body)['body'].read())
        content = result.get('content', [])
        stop_reason = result.get('stop_reason', '')
        text_parts = [b['text'] for b in content if b.get('type') == 'text']
        tool_uses = [b for b in content if b.get('type') == 'tool_use']

        if not tool_uses:
            return " ".join(text_parts) if text_parts else "Não consegui processar."

        messages.append({"role": "assistant", "content": content})
        tool_results = []
        for tu in tool_uses:
            res = get_schema() if tu['name'] == 'get_schema' else query_db(tu.get('input', {}).get('sql', ''))
            tool_results.append({"type": "tool_result", "tool_use_id": tu['id'], "content": res})
        messages.append({"role": "user", "content": tool_results})

        if stop_reason == 'end_turn' and text_parts:
            return " ".join(text_parts)

    return "Atingi o limite de raciocínio. Tente reformular a pergunta."

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [('messages', []), ('history', []), ('configured', False), ('msg_count', 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-title">Cine<span>Bot</span></div>
        <div class="brand-sub">Agente de IA · IMDb Database</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.configured:
        st.markdown('<div class="section-label">Credenciais AWS</div>', unsafe_allow_html=True)
        key_id = st.text_input("Access Key ID", type="password", placeholder="AKIA...")
        secret = st.text_input("Secret Access Key", type="password", placeholder="sua secret key...")
        session_token = st.text_input("Session Token", type="password", placeholder="(opcional — para SSO)")
        region = st.selectbox("Região", ["us-east-1", "us-west-2", "eu-central-1", "ap-southeast-1"])

        if st.button("🔌 Conectar ao Bedrock", use_container_width=True):
            if key_id and secret:
                st.session_state.aws_key_id = key_id
                st.session_state.aws_secret = secret
                st.session_state.aws_session_token = session_token
                st.session_state.aws_region = region
                st.session_state.configured = True
                st.rerun()
            else:
                st.error("Preencha Key ID e Secret Access Key.")
    else:
        st.markdown('<div class="online-badge"><div class="online-dot"></div>Conectado</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Configuração</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-row"><span class="info-key">Região</span><span class="info-val">{st.session_state.aws_region}</span></div>
        <div class="info-row"><span class="info-key">Modelo</span><span class="info-val">Claude 3.5 Sonnet</span></div>
        <div class="info-row"><span class="info-key">Agente</span><span class="info-val">ReAct Loop</span></div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Base de dados</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-row"><span class="info-key">Filmes</span><span class="info-val">12.404</span></div>
        <div class="info-row"><span class="info-key">Rating IMDb</span><span class="info-val">✓</span></div>
        <div class="info-row"><span class="info-key">Oscar</span><span class="info-val">✓</span></div>
        <div class="info-row"><span class="info-key">Bilheteria</span><span class="info-val">✓</span></div>
        <div class="info-row"><span class="info-key">Metascore</span><span class="info-val">✓</span></div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Sessão</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-row"><span class="info-key">Consultas</span><span class="info-val">{st.session_state.msg_count:03d}</span></div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑 Limpar conversa", use_container_width=True):
            st.session_state.messages = []
            st.session_state.history = []
            st.session_state.msg_count = 0
            st.rerun()
        if st.button("⚙ Reconfigurar", use_container_width=True):
            st.session_state.configured = False
            st.session_state.messages = []
            st.session_state.history = []
            st.rerun()

# ── MAIN ──────────────────────────────────────────────────────────────────────
if not st.session_state.configured:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:60vh;text-align:center;">
      <div style="font-size:64px;margin-bottom:24px;">🎬</div>
      <div style="font-family:'Syne',sans-serif;font-size:40px;font-weight:800;color:#ede8de;margin-bottom:12px;">
        Bem-vindo ao <span style="color:#d4a843;">CineBot</span>
      </div>
      <div style="font-size:15px;color:#44444e;line-height:1.7;max-width:440px;font-weight:300;">
        Configure suas credenciais AWS Bedrock no painel lateral para começar a explorar o banco de dados de cinema.
      </div>
      <div style="margin-top:32px;display:flex;gap:12px;flex-wrap:wrap;justify-content:center;">
        <div class="stat-chip">🏆 Oscar</div>
        <div class="stat-chip">⭐ IMDb Rating</div>
        <div class="stat-chip">💰 Bilheteria</div>
        <div class="stat-chip">📝 Metascore</div>
        <div class="stat-chip">🎭 115 Filmes</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Header
    st.markdown("""
    <div class="page-header">
      <div>
        <div class="page-title">Base <em>IMDb</em></div>
        <div class="page-desc">12.404 filmes · IMDb · Rating · Votos · Gênero</div>
      </div>
      <div class="online-badge"><div class="online-dot"></div>Agente Ativo</div>
    </div>
    """, unsafe_allow_html=True)

    # Welcome + suggestions
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome">
          <div class="welcome-icon">🎬</div>
          <div class="welcome-title">O que você quer <span>descobrir?</span></div>
          <div class="welcome-desc">Pergunte sobre filmes, diretores, prêmios, bilheteria, avaliações e muito mais.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sug-label">Sugestões de perguntas</div>', unsafe_allow_html=True)
        suggestions = [
            "🏆 Qual filme ganhou mais Oscars?",
            "⭐ Top 5 filmes com maior rating IMDb",
            "💰 Filmes com mais de 1 bilhão de bilheteria",
            "🎬 Todos os filmes de Christopher Nolan",
            "🌍 Filmes não americanos na base",
            "📊 Média de rating por gênero",
            "🎭 Filmes com Oscars ganhos acima de 5",
            "🗓 Filmes lançados depois de 2020",
            "🇧🇷 Filmes brasileiros",
            "🎵 Melhores filmes de música",
            "👻 Filmes de terror com alto rating",
            "📽 Diretores com mais filmes na base",
        ]
        cols = st.columns(3)
        for i, sug in enumerate(suggestions):
            with cols[i % 3]:
                if st.button(sug, key=f"s{i}"):
                    st.session_state._pending = sug

    # Chat history
    for i, msg in enumerate(st.session_state.messages):
        if msg['role'] == 'user':
            st.markdown(f"""
            <div class="msg-group user">
              <div class="bubble-label user">você</div>
              <div class="bubble-user">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-group bot">
              <div class="bubble-label bot">▸ CineBot</div>
              <div class="bubble-bot">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Input — using form so Enter key submits
    with st.form(key="chat_form", clear_on_submit=True):
        c1, c2 = st.columns([5, 1])
        with c1:
            user_input = st.text_input("q", placeholder="Pergunte sobre filmes, diretores, Oscar... (Enter para enviar)", label_visibility="collapsed")
        with c2:
            st.markdown('<div class="send-btn">', unsafe_allow_html=True)
            send = st.form_submit_button("Enviar →", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Pending suggestion
    if '_pending' in st.session_state:
        user_input = st.session_state._pending
        del st.session_state._pending
        send = True

    if send and user_input.strip():
        msg = user_input.strip()
        st.session_state.messages.append({'role': 'user', 'content': msg})
        st.session_state.msg_count += 1
        with st.spinner("🎬 Consultando banco de filmes..."):
            try:
                reply = run_agent(
                    msg,
                    st.session_state.history,
                    st.session_state.aws_key_id,
                    st.session_state.aws_secret,
                    st.session_state.get('aws_session_token', ''),
                    st.session_state.aws_region
                )
                st.session_state.messages.append({'role': 'assistant', 'content': reply})
                st.session_state.history.append({"role": "user", "content": msg})
                st.session_state.history.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Erro Bedrock: {str(e)}")
        st.rerun()
