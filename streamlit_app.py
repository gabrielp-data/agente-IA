import streamlit as st
import sqlite3
import json
import boto3
import os

st.set_page_config(
    page_title="CineBot",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Space+Mono:wght@400;700&family=Outfit:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    background-color: #080809 !important;
    color: #f0ebe0 !important;
    font-family: 'Outfit', sans-serif !important;
}

#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Layout ── */
.main-layout {
    display: grid;
    grid-template-columns: 320px 1fr;
    min-height: 100vh;
    position: relative;
}

/* ── Sidebar panel ── */
.sidebar-panel {
    background: #0c0c0e;
    border-right: 1px solid #1c1c22;
    display: flex;
    flex-direction: column;
    position: fixed;
    left: 0; top: 0; bottom: 0;
    width: 320px;
    z-index: 10;
    overflow: hidden;
}

.sidebar-grain {
    position: absolute;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.035'/%3E%3C/svg%3E");
    pointer-events: none;
}

.sidebar-top {
    padding: 40px 32px 32px;
    border-bottom: 1px solid #1c1c22;
    position: relative;
}

.logo-container {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 24px;
}

.logo-icon {
    width: 48px; height: 48px;
    border: 1px solid #c8a94a;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Cormorant Garamond', serif;
    font-size: 22px; color: #c8a94a;
    flex-shrink: 0;
    position: relative;
}
.logo-icon::after {
    content: '';
    position: absolute;
    inset: 3px;
    border: 1px solid rgba(200,169,74,0.2);
}

.logo-text {
    padding-top: 4px;
}
.logo-text .title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 28px;
    font-weight: 300;
    letter-spacing: 0.12em;
    color: #f0ebe0;
    line-height: 1;
    text-transform: uppercase;
}
.logo-text .title em {
    color: #c8a94a;
    font-style: italic;
}
.logo-text .sub {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #44444e;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 5px;
}

.status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #44444e;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.status-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #2a9d5c;
    animation: glow 2s ease-in-out infinite;
}
@keyframes glow {
    0%,100% { box-shadow: 0 0 4px #2a9d5c; opacity: 1; }
    50% { box-shadow: 0 0 10px #2a9d5c; opacity: 0.6; }
}

/* ── Credentials section ── */
.cred-section {
    padding: 28px 32px;
    flex: 1;
    overflow-y: auto;
}
.cred-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #c8a94a;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.cred-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #c8a94a33, transparent);
}

.field-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #44444e;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 6px;
    margin-top: 14px;
}

/* ── Stats ── */
.stats-section {
    padding: 20px 32px 32px;
    border-top: 1px solid #1c1c22;
}
.stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #13131a;
}
.stat-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #44444e;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.stat-value {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #c8a94a;
}

/* ── Main content area ── */
.main-content {
    margin-left: 320px;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    position: relative;
}

/* ── Top decoration ── */
.top-strip {
    height: 3px;
    background: linear-gradient(90deg, transparent, #c8a94a 20%, #c8a94a 80%, transparent);
    opacity: 0.4;
}

/* ── Chat area ── */
.chat-container {
    flex: 1;
    padding: 48px 64px 24px;
    max-width: 860px;
    width: 100%;
}

/* ── Welcome ── */
.welcome-area {
    padding: 80px 0 40px;
    text-align: left;
}
.welcome-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #c8a94a;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.welcome-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 56px;
    font-weight: 300;
    line-height: 1.05;
    color: #f0ebe0;
    margin-bottom: 20px;
}
.welcome-title em {
    color: #c8a94a;
    font-style: italic;
}
.welcome-desc {
    font-size: 15px;
    color: #6b6760;
    line-height: 1.7;
    max-width: 480px;
    font-weight: 300;
}

/* ── Suggestion pills ── */
.suggestions-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 32px 0;
}

/* ── Messages ── */
.msg-wrapper { margin-bottom: 28px; }
.msg-meta {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.msg-meta.user-meta { color: #44444e; justify-content: flex-end; }
.msg-meta.bot-meta { color: #c8a94a; }
.msg-meta.bot-meta::before {
    content: '';
    width: 20px; height: 1px;
    background: #c8a94a;
    opacity: 0.5;
}

.msg-bubble-user {
    background: #0f0f12;
    border: 1px solid #1c1c22;
    padding: 16px 20px;
    font-size: 14.5px;
    line-height: 1.7;
    color: #c8c3b8;
    margin-left: 80px;
    font-weight: 300;
}

.msg-bubble-bot {
    background: linear-gradient(135deg, #0c0c10 0%, #0a0a0d 100%);
    border: 1px solid #1c1c22;
    border-left: 2px solid #c8a94a;
    padding: 20px 24px;
    font-size: 14.5px;
    line-height: 1.75;
    color: #d8d3c8;
    margin-right: 80px;
    font-weight: 300;
    position: relative;
}
.msg-bubble-bot::before {
    content: '"';
    position: absolute;
    top: -8px; left: 20px;
    font-family: 'Cormorant Garamond', serif;
    font-size: 40px;
    color: #c8a94a;
    opacity: 0.15;
    line-height: 1;
}

/* ── Divider ── */
.msg-divider {
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 32px 0;
    opacity: 0.2;
}
.msg-divider::before, .msg-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #f0ebe0;
}
.msg-divider span {
    font-family: 'Cormorant Garamond', serif;
    font-size: 16px;
    color: #f0ebe0;
}

/* ── Input area ── */
.input-area-wrap {
    padding: 0 64px 40px;
    max-width: 860px;
    width: 100%;
}
.input-border {
    border: 1px solid #1c1c22;
    border-top: 1px solid #c8a94a44;
    padding: 2px;
    background: #0c0c10;
    position: relative;
}
.input-border::before {
    content: 'CONSULTAR BASE';
    position: absolute;
    top: -8px; left: 16px;
    background: #080809;
    padding: 0 8px;
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    color: #c8a94a;
    letter-spacing: 0.2em;
}

/* ── Streamlit overrides ── */
.stTextInput > div > div > input {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: #f0ebe0 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 15px !important;
    font-weight: 300 !important;
    padding: 14px 16px !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input::placeholder { color: #33333a !important; }
.stTextInput > div > div > input:focus { outline: none !important; box-shadow: none !important; }
.stTextInput > label { display: none !important; }

.stButton > button {
    background: #c8a94a !important;
    color: #080809 !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    padding: 14px 24px !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #dfc05a !important;
    transform: none !important;
}

.stSelectbox > div > div {
    background: #0c0c10 !important;
    border: 1px solid #1c1c22 !important;
    border-radius: 0 !important;
    color: #f0ebe0 !important;
}
.stSelectbox label {
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important;
    color: #44444e !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}

/* Spinner */
.stSpinner > div {
    border-color: #c8a94a !important;
    border-right-color: transparent !important;
}

/* Alert */
.stAlert {
    background: #1a0a0a !important;
    border: 1px solid #5a1a1a !important;
    border-radius: 0 !important;
    color: #f0a0a0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
}

/* ── Film perforations decoration ── */
.perfs {
    position: fixed;
    left: 320px;
    top: 0; bottom: 0;
    width: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    pointer-events: none;
    z-index: 5;
    opacity: 0.08;
}
.perf {
    width: 10px; height: 14px;
    border: 1px solid #f0ebe0;
    border-radius: 1px;
}

/* ── Thinking ── */
.thinking-wrap {
    margin-bottom: 28px;
}
.thinking-bubble {
    background: #0c0c10;
    border: 1px solid #1c1c22;
    border-left: 2px solid #c8a94a;
    padding: 16px 24px;
    margin-right: 80px;
    display: flex;
    align-items: center;
    gap: 14px;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #44444e;
    letter-spacing: 0.1em;
}
.thinking-dots { display: flex; gap: 5px; }
.thinking-dots span {
    width: 4px; height: 4px;
    border-radius: 50%;
    background: #c8a94a;
    animation: tdot 1.3s ease infinite;
    opacity: 0.5;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes tdot {
    0%,60%,100% { transform: translateY(0); opacity: 0.4; }
    30% { transform: translateY(-4px); opacity: 1; }
}
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
                "sql": {"type": "string", "description": "Query SQLite SELECT válida."}
            },
            "required": ["sql"]
        }
    }
]

SYSTEM_PROMPT = """Você é o CineBot, agente especialista em cinema com banco de 50 filmes.
Opere como agente ReAct: Raciocine → Use ferramentas → Observe → Responda.
Sempre use as ferramentas para dados. Responda em português brasileiro de forma elegante e apaixonada por cinema."""

def run_agent(user_message: str, history: list, key_id: str, secret: str, session_token: str, region: str) -> str:
    kwargs = dict(
        service_name='bedrock-runtime',
        region_name=region,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
    )
    if session_token:
        kwargs['aws_session_token'] = session_token
    bedrock = boto3.client(**kwargs)

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
for key, val in [('messages', []), ('history', []), ('aws_configured', False)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── SIDEBAR (rendered as HTML fixed panel + Streamlit inputs overlaid) ─────────
# We use columns to simulate sidebar
col_side, col_main = st.columns([320, 860], gap="small")

with col_side:
    st.markdown("""
    <div style="background:#0c0c0e; border-right:1px solid #1c1c22; min-height:100vh; padding:40px 28px 28px; position:relative;">
      <div style="position:absolute;inset:0;pointer-events:none;background-image:url('data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22><filter id=%22n%22><feTurbulence type=%22fractalNoise%22 baseFrequency=%220.9%22 numOctaves=%224%22 stitchTiles=%22stitch%22/></filter><rect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23n)%22 opacity=%220.03%22/></svg>');"></div>

      <div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:28px;">
        <div style="width:48px;height:48px;border:1px solid #c8a94a;display:flex;align-items:center;justify-content:center;font-family:'Cormorant Garamond',serif;font-size:22px;color:#c8a94a;flex-shrink:0;position:relative;">
          C
          <div style="position:absolute;inset:4px;border:1px solid rgba(200,169,74,0.15);"></div>
        </div>
        <div style="padding-top:4px;">
          <div style="font-family:'Cormorant Garamond',serif;font-size:26px;font-weight:300;letter-spacing:0.12em;color:#f0ebe0;line-height:1;text-transform:uppercase;">Cine<em style="color:#c8a94a;font-style:italic;">Bot</em></div>
          <div style="font-family:'Space Mono',monospace;font-size:8px;color:#33333a;letter-spacing:0.2em;text-transform:uppercase;margin-top:5px;">Agente IAGen</div>
        </div>
      </div>

      <div style="display:flex;align-items:center;gap:8px;font-family:'Space Mono',monospace;font-size:8px;color:#33333a;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:32px;padding-bottom:24px;border-bottom:1px solid #1c1c22;">
        <div style="width:5px;height:5px;border-radius:50%;background:#2a9d5c;box-shadow:0 0 6px #2a9d5c;"></div>
        Sistema Ativo
      </div>
    """, unsafe_allow_html=True)

    if not st.session_state.aws_configured:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:8px;color:#c8a94a;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:16px;">⬡ Credenciais AWS</div>', unsafe_allow_html=True)
        key_id = st.text_input("Access Key ID", type="password", placeholder="AKIA...", label_visibility="visible")
        secret = st.text_input("Secret Access Key", type="password", placeholder="secret...", label_visibility="visible")
        session_token = st.text_input("Session Token (opcional)", type="password", placeholder="token SSO...", label_visibility="visible")
        region = st.selectbox("Região", ["us-east-1", "us-west-2", "eu-central-1"])

        if st.button("CONECTAR AO BEDROCK"):
            if key_id and secret:
                st.session_state.aws_key_id = key_id
                st.session_state.aws_secret = secret
                st.session_state.aws_session_token = session_token
                st.session_state.aws_region = region
                st.session_state.aws_configured = True
                st.rerun()
            else:
                st.error("Preencha Key ID e Secret.")
    else:
        st.markdown(f"""
        <div style="font-family:'Space Mono',monospace;font-size:8px;color:#c8a94a;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:16px;">⬡ Conexão Ativa</div>
        <div style="font-size:11px;color:#44444e;line-height:1.8;font-family:'Space Mono',monospace;">
          <div>Região: <span style="color:#c8a94a;">{st.session_state.get('aws_region','—')}</span></div>
          <div>Modelo: <span style="color:#c8a94a;">Claude 3.5 Sonnet v2</span></div>
          <div>Base: <span style="color:#c8a94a;">50 filmes</span></div>
          <div>Agente: <span style="color:#c8a94a;">ReAct Loop</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        if st.button("RECONFIGURAR"):
            st.session_state.aws_configured = False
            st.session_state.messages = []
            st.session_state.history = []
            st.rerun()

        # Stats
        n_msgs = len([m for m in st.session_state.messages if m['role'] == 'user'])
        st.markdown(f"""
        <div style="margin-top:32px;padding-top:24px;border-top:1px solid #1c1c22;">
          <div style="font-family:'Space Mono',monospace;font-size:8px;color:#33333a;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:12px;">Sessão</div>
          <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #13131a;">
            <span style="font-family:'Space Mono',monospace;font-size:9px;color:#33333a;letter-spacing:0.1em;text-transform:uppercase;">Consultas</span>
            <span style="font-family:'Space Mono',monospace;font-size:10px;color:#c8a94a;">{n_msgs:03d}</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #13131a;">
            <span style="font-family:'Space Mono',monospace;font-size:9px;color:#33333a;letter-spacing:0.1em;text-transform:uppercase;">Filmes</span>
            <span style="font-family:'Space Mono',monospace;font-size:10px;color:#c8a94a;">050</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:8px 0;">
            <span style="font-family:'Space Mono',monospace;font-size:9px;color:#33333a;letter-spacing:0.1em;text-transform:uppercase;">Padrão</span>
            <span style="font-family:'Space Mono',monospace;font-size:10px;color:#c8a94a;">ReAct</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────
with col_main:
    st.markdown('<div style="height:3px;background:linear-gradient(90deg,transparent,rgba(200,169,74,0.3) 20%,rgba(200,169,74,0.3) 80%,transparent);margin-bottom:0;"></div>', unsafe_allow_html=True)

    if not st.session_state.aws_configured:
        st.markdown("""
        <div style="padding:80px 48px 40px;">
          <div style="font-family:'Space Mono',monospace;font-size:9px;color:#c8a94a;letter-spacing:0.25em;text-transform:uppercase;margin-bottom:20px;">Configure as credenciais para começar</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:52px;font-weight:300;line-height:1.05;color:#f0ebe0;margin-bottom:20px;">
            O cinema<br><em style="color:#c8a94a;font-style:italic;">à sua disposição</em>
          </div>
          <div style="font-size:15px;color:#33333a;line-height:1.7;max-width:420px;font-weight:300;">
            Insira suas credenciais AWS no painel ao lado para ativar o agente de inteligência artificial.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="padding:40px 48px 0;">', unsafe_allow_html=True)

        # Suggestions
        if not st.session_state.messages:
            st.markdown("""
            <div style="padding-bottom:8px;">
              <div style="font-family:'Cormorant Garamond',serif;font-size:48px;font-weight:300;line-height:1.05;color:#f0ebe0;margin-bottom:8px;">
                O cinema<br><em style="color:#c8a94a;font-style:italic;">em dados</em>
              </div>
              <div style="font-size:14px;color:#33333a;line-height:1.7;max-width:400px;font-weight:300;margin-bottom:28px;">
                Faça perguntas sobre filmes, diretores, avaliações e gêneros.
              </div>
            </div>
            """, unsafe_allow_html=True)

            suggestions = [
                "Qual o filme mais bem avaliado?",
                "Filmes de Christopher Nolan",
                "Dramas acima de 8.5",
                "Filmes brasileiros",
                "Recomende um sci-fi clássico",
                "Filmes com mais de 2h de duração",
            ]
            cols = st.columns(3)
            for i, sug in enumerate(suggestions):
                with cols[i % 3]:
                    if st.button(sug, key=f"sug_{i}"):
                        st.session_state._pending = sug

        # Chat messages
        for i, msg in enumerate(st.session_state.messages):
            if msg['role'] == 'user':
                st.markdown(f"""
                <div style="margin-bottom:28px;">
                  <div style="font-family:'Space Mono',monospace;font-size:8px;color:#33333a;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px;text-align:right;">você</div>
                  <div style="background:#0f0f12;border:1px solid #1c1c22;padding:16px 20px;font-size:14px;line-height:1.7;color:#9c9890;margin-left:80px;font-weight:300;">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="margin-bottom:28px;">
                  <div style="font-family:'Space Mono',monospace;font-size:8px;color:#c8a94a;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:10px;"><span style="display:inline-block;width:20px;height:1px;background:#c8a94a;opacity:0.5;"></span>cinebot</div>
                  <div style="background:linear-gradient(135deg,#0c0c10,#0a0a0d);border:1px solid #1c1c22;border-left:2px solid #c8a94a;padding:20px 24px;font-size:14px;line-height:1.75;color:#c8c3b8;margin-right:80px;font-weight:300;">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)

            if i < len(st.session_state.messages) - 1 and i % 2 == 1:
                st.markdown('<div style="height:1px;background:linear-gradient(90deg,rgba(200,169,74,0.08),transparent);margin:4px 0 4px;"></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Input
        st.markdown('<div style="padding:16px 48px 40px;">', unsafe_allow_html=True)
        st.markdown("""
        <div style="border:1px solid #1c1c22;border-top:1px solid rgba(200,169,74,0.25);background:#0a0a0d;position:relative;margin-bottom:0;">
          <div style="position:absolute;top:-8px;left:16px;background:#080809;padding:0 8px;font-family:'Space Mono',monospace;font-size:7px;color:#c8a94a;letter-spacing:0.2em;text-transform:uppercase;">CONSULTAR BASE</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([5, 1])
        with c1:
            user_input = st.text_input("msg", placeholder="Pergunte sobre filmes...", label_visibility="collapsed", key="user_input")
        with c2:
            send = st.button("ENVIAR", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Handle pending suggestion
        if '_pending' in st.session_state:
            user_input = st.session_state._pending
            del st.session_state._pending
            send = True

        if send and user_input.strip():
            msg = user_input.strip()
            st.session_state.messages.append({'role': 'user', 'content': msg})
            with st.spinner("Consultando base cinematográfica..."):
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
                    st.error(f"Erro: {e}")
            st.rerun()
