import streamlit as st
import sqlite3
import json
import boto3
import os

st.set_page_config(
    page_title="CineBot — Agente de Cinema",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Mono:wght@300;400&family=Instrument+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    background-color: #0a0a0b !important;
    color: #e8e4dc !important;
    font-family: 'Instrument Sans', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 800px; }

.filmstrip {
    height: 16px;
    background: repeating-linear-gradient(90deg, transparent 0px, transparent 8px, #1a1a1f 8px, #1a1a1f 14px);
    border-bottom: 1px solid #222;
    margin: -1.5rem -1rem 1.5rem -1rem;
}
.cinebot-header {
    display: flex; align-items: center; gap: 14px;
    padding: 0 0 1rem 0; border-bottom: 1px solid #1e1e24; margin-bottom: 1.2rem;
}
.logo-mark {
    width: 42px; height: 42px; border: 1.5px solid #d4a843; border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Playfair Display', serif; font-size: 20px; color: #d4a843; flex-shrink: 0;
}
.header-text h1 {
    font-family: 'Playfair Display', serif !important; font-size: 22px !important;
    font-weight: 700 !important; color: #e8e4dc !important;
    margin: 0 !important; padding: 0 !important; line-height: 1 !important;
}
.header-text h1 span { color: #d4a843; }
.header-text p {
    font-size: 11px; color: #6b6760; font-family: 'DM Mono', monospace;
    margin: 3px 0 0 0; letter-spacing: 0.08em; text-transform: uppercase;
}
.status-badge {
    margin-left: auto; font-size: 10px; color: #6b6760;
    font-family: 'DM Mono', monospace; display: flex; align-items: center; gap: 5px;
}
.dot-green { width: 6px; height: 6px; border-radius: 50%; background: #2ecc71; display: inline-block; }

.msg-user {
    background: #16161a; border: 1px solid #1e1e24; border-radius: 2px;
    padding: 10px 14px; margin: 6px 0 6px 60px; font-size: 14px; line-height: 1.6;
}
.msg-bot {
    background: #0f0f12; border: 1px solid #1e1e24; border-left: 2px solid #d4a843;
    border-radius: 2px; padding: 10px 14px; margin: 6px 60px 6px 0;
    font-size: 14px; line-height: 1.6;
}
.msg-label { font-size: 10px; color: #6b6760; font-family: 'DM Mono', monospace; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.msg-label.bot { color: rgba(212,168,67,0.6); }

.cred-box {
    background: #111114; border: 1px solid #1e1e24; border-left: 2px solid #d4a843;
    border-radius: 2px; padding: 16px 20px; margin-bottom: 1.2rem;
}
.cred-box h3 { font-size: 13px; color: #d4a843; font-family: 'DM Mono', monospace; margin-bottom: 10px; letter-spacing: 0.06em; }

.stTextInput > div > div > input {
    background: #111114 !important; border: 1px solid #1e1e24 !important;
    border-radius: 2px !important; color: #e8e4dc !important;
    font-family: 'Instrument Sans', sans-serif !important; font-size: 14px !important;
}
.stTextInput > div > div > input:focus { border-color: rgba(212,168,67,0.4) !important; box-shadow: none !important; }
.stSelectbox > div > div { background: #111114 !important; border: 1px solid #1e1e24 !important; border-radius: 2px !important; }

.stButton > button {
    background: #d4a843 !important; color: #0a0a0b !important; border: none !important;
    border-radius: 2px !important; font-family: 'Instrument Sans', sans-serif !important;
    font-weight: 500 !important; padding: 0.5rem 1.2rem !important;
}
.stButton > button:hover { background: #e8b84e !important; }
</style>
""", unsafe_allow_html=True)

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), 'movies.db')

def query_db(sql: str) -> str:
    sql = sql.strip()
    if not sql.upper().startswith("SELECT"):
        return "Erro: apenas SELECT é permitido."
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql).fetchall()
        conn.close()
        if not rows:
            return "Nenhum resultado encontrado."
        return json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2)
    except Exception as e:
        return f"SQL Error: {e}"

def get_schema() -> str:
    return """Tabela: movies
Colunas: id, title, year, genre, director, cast, rating (0-10), votes, runtime (min), language, country, overview
Total: 50 filmes clássicos e modernos"""

TOOLS = [
    {
        "name": "get_schema",
        "description": "Retorna o schema do banco de dados.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "query_movies_db",
        "description": "Executa uma query SQL SELECT no banco de filmes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "Query SQLite SELECT válida. Use LIKE para texto."}
            },
            "required": ["sql"]
        }
    }
]

SYSTEM_PROMPT = """Você é o CineBot, agente especialista em cinema com banco de 50 filmes.
Opere como agente ReAct: Raciocine → Use ferramentas → Observe → Responda.
Sempre use as ferramentas para dados. Responda em português brasileiro. Seja entusiasta sobre cinema."""

def run_agent(user_message: str, history: list, key_id: str, secret: str, region: str) -> str:
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name=region,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
    )
    messages = history + [{"role": "user", "content": user_message}]

    for _ in range(8):
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "system": SYSTEM_PROMPT,
            "tools": TOOLS,
            "messages": messages
        })
        response = bedrock.invoke_model(modelId="anthropic.claude-3-5-sonnet-20241022-v2:0", body=body)
        result = json.loads(response['body'].read())
        content = result.get('content', [])
        stop_reason = result.get('stop_reason', '')
        text_parts = [b['text'] for b in content if b.get('type') == 'text']
        tool_uses = [b for b in content if b.get('type') == 'tool_use']

        if not tool_uses:
            return " ".join(text_parts) if text_parts else "Não consegui processar."

        messages.append({"role": "assistant", "content": content})
        tool_results = []
        for tu in tool_uses:
            if tu['name'] == 'get_schema':
                res = get_schema()
            elif tu['name'] == 'query_movies_db':
                res = query_db(tu.get('input', {}).get('sql', ''))
            else:
                res = "Ferramenta desconhecida."
            tool_results.append({"type": "tool_result", "tool_use_id": tu['id'], "content": res})

        messages.append({"role": "user", "content": tool_results})
        if stop_reason == 'end_turn' and text_parts:
            return " ".join(text_parts)

    return "Atingi o limite de raciocínio. Tente reformular."

# ── Session state ─────────────────────────────────────────────────────────────
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'history' not in st.session_state:
    st.session_state.history = []
if 'aws_configured' not in st.session_state:
    st.session_state.aws_configured = False

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="filmstrip"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="cinebot-header">
  <div class="logo-mark">C</div>
  <div class="header-text">
    <h1>Cine<span>Bot</span></h1>
    <p>Agente IAGen · Amazon Bedrock · ReAct</p>
  </div>
  <div class="status-badge"><span class="dot-green"></span> ONLINE</div>
</div>
""", unsafe_allow_html=True)

# ── Credentials (inline, always visible until configured) ─────────────────────
if not st.session_state.aws_configured:
    st.markdown('<div class="cred-box"><h3>⚙ CREDENCIAIS AWS BEDROCK</h3></div>', unsafe_allow_html=True)
    key_id = st.text_input("Access Key ID", type="password", placeholder="AKIA...")
    secret = st.text_input("Secret Access Key", type="password", placeholder="sua secret key...")
    region = st.selectbox("Região", ["us-east-1", "us-west-2", "eu-central-1"])

    if st.button("Conectar ao Bedrock"):
        if key_id and secret:
            st.session_state.aws_key_id = key_id
            st.session_state.aws_secret = secret
            st.session_state.aws_region = region
            st.session_state.aws_configured = True
            st.rerun()
        else:
            st.error("Preencha os dois campos.")
else:
    # Small reset button
    col1, col2 = st.columns([6,1])
    with col2:
        if st.button("⚙", help="Reconfigurar credenciais"):
            st.session_state.aws_configured = False
            st.session_state.messages = []
            st.session_state.history = []
            st.rerun()

    # ── Suggestions ───────────────────────────────────────────────────────────
    if not st.session_state.messages:
        suggestions = ["Qual o filme mais bem avaliado?", "Filmes de Christopher Nolan", "Dramas acima de 8.5", "Filmes brasileiros", "Recomende um sci-fi"]
        cols = st.columns(len(suggestions))
        for i, (col, sug) in enumerate(zip(cols, suggestions)):
            with col:
                if st.button(sug, key=f"sug_{i}", use_container_width=True):
                    st.session_state._pending = sug

    # ── Chat history ──────────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            st.markdown(f'<div class="msg-label">você</div><div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-label bot">▸ CineBot</div><div class="msg-bot">{msg["content"]}</div>', unsafe_allow_html=True)

    # ── Input ─────────────────────────────────────────────────────────────────
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("", placeholder="Pergunte sobre filmes...", label_visibility="collapsed", key="user_input")
    with col2:
        send = st.button("Enviar", use_container_width=True)

    if '_pending' in st.session_state:
        user_input = st.session_state._pending
        del st.session_state._pending
        send = True

    if send and user_input.strip():
        msg = user_input.strip()
        st.session_state.messages.append({'role': 'user', 'content': msg})
        with st.spinner("🎬 Consultando banco de filmes..."):
            try:
                reply = run_agent(
                    msg,
                    st.session_state.history,
                    st.session_state.aws_key_id,
                    st.session_state.aws_secret,
                    st.session_state.aws_region
                )
                st.session_state.messages.append({'role': 'assistant', 'content': reply})
                st.session_state.history.append({"role": "user", "content": msg})
                st.session_state.history.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Erro Bedrock: {e}")
        st.rerun()
