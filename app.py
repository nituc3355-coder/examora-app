import streamlit as st
import pymupdf
from groq import Groq
import json
import os

# Setări vizuale pentru platformă
st.set_page_config(page_title="EXAMORA", layout="centered")

# --- DESIGN CSS AVANSAT ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    .pricing-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 30px;
        text-align: center;
    }
    .pro-card {
        background: linear-gradient(135deg, #312e81 0%, #1e1b4b 100%);
        border: 2px solid #818cf8;
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- GESTIONAREA STĂRII ȘI AUTENTIFICĂRII ---
if "autentificat" not in st.session_state:
    st.session_state.autentificat = False
if "utilizator" not in st.session_state:
    st.session_state.utilizator = None
if "plan_pro" not in st.session_state:
    st.session_state.plan_pro = False
if "intrebari" not in st.session_state:
    st.session_state.intrebari = []
if "test_trimis" not in st.session_state:
    st.session_state.test_trimis = False
if "modal_google" not in st.session_state:
    st.session_state.modal_google = False

if "chat_oral" not in st.session_state:
    st.session_state.chat_oral = []
if "examen_oral_pornit" not in st.session_state:
    st.session_state.examen_oral_pornit = False
if "text_curs_memorie" not in st.session_state:
    st.session_state.text_curs_memorie = ""

try:
    API_KEY_GROQ = st.secrets["GROQ_API_KEY"]
except:
    API_KEY_GROQ = None

# --- ECRANUL DE AUTENTIFICARE ---
if not st.session_state.autentificat:
    col_l1, col_l2, col_l3 = st.columns([1, 3, 1])
    with col_l2:
        st.markdown("<h1 style='text-align: center;'>🎓 Examora</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; color: #9ca3af;'>Platforma supremă de pregătire pentru examene bazată pe Inteligență Artificială.</p>",
            unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑 Autentificare", "✨ Creează Cont"])

        with tab_login:
            email_login = st.text_input("Adresă Email", key="login_email")
            parola_login = st.text_input("Parolă", type="password", key="login_parola")

            if st.button("Conectare", type="primary", use_container_width=True):
                if email_login:
                    st.session_state.autentificat = True
                    st.session_state.utilizator = email_login
                    st.rerun()
                else:
                    st.warning("Te rog să introduci adresa de email.")

            st.markdown("<p style='text-align: center; color: #6b7280; margin-top: 15px;'>sau continuă cu</p>",
                        unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("Google", use_container_width=True):
                    st.session_state.modal_google = True
            with c2:
                if st.button("Apple", use_container_width=True):
                    st.session_state.autentificat = True
                    st.session_state.utilizator = "student.apple@edu.ro"
                    st.rerun()
            with c3:
                if st.button("Facebook", use_container_width=True):
                    st.session_state.autentificat = True
                    st.session_state.utilizator = "student.facebook@edu.ro"
                    st.rerun()

            if st.session_state.modal_google:
                st.info("Selectează contul Google:")
                email_selectat = st.selectbox("Conturi detectate:",
                                              ["student.universitate@gmail.com", "cont.personal@gmail.com"])
                ca, cb = st.columns(2)
                with ca:
                    if st.button("Confirmă"):
                        st.session_state.autentificat = True
                        st.session_state.utilizator = email_selectat
                        st.session_state.modal_google = False
                        st.rerun()
                with cb:
                    if st.button("Anulează"):
                        st.session_state.modal_google = False
                        st.rerun()

        with tab_register:
            nume_reg = st.text_input("Nume complet")
            email_reg = st.text_input("Adresă Email", key="reg_email")
            parola_reg = st.text_input("Parolă nouă", type="password", key="reg_parola")

            if st.button("Înregistrează-te", type="primary", use_container_width=True):
                if email_reg and parola_reg:
                    st.session_state.autentificat = True
                    st.session_state.utilizator = email_reg
                    st.success("Cont creat cu succes!")
                    st.rerun()
                else:
                    st.error("Completează toate câmpurile.")

# --- APLICAȚIA PRINCIPALĂ ---
else:
    st.sidebar.title(f"✨ Salut, {st.session_state.utilizator.split('@')[0]}!")

    if st.session_state.plan_pro:
        st.sidebar.markdown("👑 **STATUS: PRO ACTIV**")
    else:
        st.sidebar.markdown("🌱 **STATUS: Plan Free**")

    meniu = st.sidebar.radio("Navigare", ["🏠 Teste Grilă", "🗣️ Examen Oral", "💎 Plan PRO", "⚙️ Setări Cont"])

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Deconectare", use_container_width=True):
        st.session_state.autentificat = False
        st.session_state.utilizator = None
        st.session_state.plan_pro = False
        st.session_state.intrebari = []
        st.session_state.chat_oral = []
        st.session_state.examen_oral_pornit = False
        st.rerun()

    # --- 1. TESTE GRILĂ ---
    if meniu == "🏠 Teste Grilă":
        st.title("🎓 Grile Interactive de Examen")
        st.write("Încarcă suportul tău de curs în format PDF și lasă AI-ul să genereze un test de tip grilă riguros.")

        uploaded_file = st.file_uploader("Încarcă fișierul PDF al cursului", type=["pdf"], key="pdf_grile")

        if st.button("🚀 Generează Testul de Examen", type="primary"):
            if not API_KEY_GROQ:
                st.error("Eroare de configurare: Cheia API lipsesc din secrets.toml.")
            elif uploaded_file is None:
                st.error("Te rog să încarci un fișier PDF mai întâi!")
            else:
                with st.spinner("✨ Se analizează documentul și se generează întrebările..."):
                    try:
                        bytes_fisier = uploaded_file.read()
                        document = pymupdf.open(stream=bytes_fisier, filetype="pdf")

                        text_complet = ""
                        for pagina in document:
                            text_complet += pagina.get_text()

                        st.session_state.text_curs_memorie = text_complet

                        client = Groq(api_key=API_KEY_GROQ)
                        prompt = f"""
                        Ești un profesor universitar exigent. Pe baza textului de curs de mai jos, 
                        generează exact 10 întrebări de tip grilă. 
                        Returnează datele STRICT sub formă de listă JSON validă, fără markdown suplimentar, cu cheile:
                        - "id": numărul (1-10)
                        - "intrebare": enunțul
                        - "optiuni": listă cu 4 variante
                        - "raspuns_corect": varianta corectă
                        - "explicatie": motivația

                        Textul: {text_complet[:6000]}
                        """

                        completion = client.chat.completions.create(
                            model="openai/gpt-oss-120b",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.5,
                        )

                        raspuns_ai = completion.choices[0].message.content.strip()
                        if raspuns_ai.startswith("```"):
                            raspuns_ai = raspuns_ai.split("```")[1]
                            if raspuns_ai.startswith("json"):
                                raspuns_ai = raspuns_ai[4:]

                        st.session_state.intrebari = json.loads(raspuns_ai.strip())
                        st.session_state.test_trimis = False
                        st.success("Test generat cu succes!")
                    except Exception as e:
                        st.error(f"Eroare: {e}")

        if st.session_state.intrebari:
            st.markdown("---")
            st.subheader("📝 Chestionar Activ")
            raspunsuri_utilizator = {}

            for i, q in enumerate(st.session_state.intrebari):
                st.markdown(f"**Întrebarea {i + 1}: {q['intrebare']}**")
                ales = st.radio(f"q_{i}", q['optiuni'], index=None, key=f"q_{i}", label_visibility="collapsed")
                raspunsuri_utilizator[i] = ales
                st.markdown("")

            if not st.session_state.test_trimis:
                if st.button("🏁 Trimite Răspunsurile"):
                    necompletate = [i + 1 for i, val in raspunsuri_utilizator.items() if val is None]
                    if necompletate:
                        st.warning(f"Rămân întrebări fără răspuns: {necompletate}")
                    else:
                        st.session_state.test_trimis = True
                        st.rerun()

            if st.session_state.test_trimis:
                st.markdown("---")
                st.subheader("📊 Rezultatul Tău")
                scor = 0
                total = len(st.session_state.intrebari)

                for i, q in enumerate(st.session_state.intrebari):
                    r_ales = raspunsuri_utilizator[i]
                    r_corect = q['raspuns_corect']
                    if r_corect.strip().upper() in r_ales.upper() or r_ales.strip().upper() in r_corect.upper():
                        scor += 1
                        st.markdown(f"✅ **Întrebarea {i + 1}: Corect!**")
                    else:
                        st.markdown(f"❌ **Întrebarea {i + 1}: Greșit.** Ai ales: `{r_ales}` | Corect: `{r_corect}`")
                    st.markdown(f"💡 *Explicație:* {q['explicatie']}")
                    st.markdown("---")

                st.balloons()
                st.success(f"### Scor final: {scor} / {total}")
                if st.button("🔄 Resetează"):
                    st.session_state.test_trimis = False
                    st.rerun()

    # --- 2. EXAMEN ORAL ---
    elif meniu == "🗣️ Examen Oral":
        st.title("👨‍🏫 Profesorul AI - Simulare Examen Oral")
        st.write("Discută direct cu examinatorul virtual bazat pe materialul tău de curs.")

        if not st.session_state.text_curs_memorie:
            uploaded_file_oral = st.file_uploader("Încarcă cursul PDF pentru examen:", type=["pdf"], key="pdf_oral")
            if uploaded_file_oral:
                bytes_fisier = uploaded_file_oral.read()
                document = pymupdf.open(stream=bytes_fisier, filetype="pdf")
                text_extras = "".join([p.get_text() for p in document])
                st.session_state.text_curs_memorie = text_extras
                st.success("Curs încărcat!")

        if st.session_state.text_curs_memorie:
            if not st.session_state.examen_oral_pornit:
                if st.button("🚀 Intră în Sala de Examen", type="primary"):
                    if not API_KEY_GROQ:
                        st.error("Cheia API lipsesc.")
                    else:
                        st.session_state.examen_oral_pornit = True
                        system_prompt = f"Ești un profesor universitar exigent la examenul oral. Pe baza cursului: {st.session_state.text_curs_memorie[:5000]}, salută studentul și pune-i prima întrebare."
                        client = Groq(api_key=API_KEY_GROQ)
                        comp = client.chat.completions.create(model="openai/gpt-oss-120b",
                                                              messages=[{"role": "system", "content": system_prompt}],
                                                              temperature=0.7)
                        st.session_state.chat_oral = [{"role": "assistant", "content": comp.choices[0].message.content}]
                        st.rerun()
            else:
                for msg in st.session_state.chat_oral:
                    if msg["role"] == "assistant":
                        st.chat_message("assistant", avatar="👨‍🏫").write(msg["content"])
                    else:
                        st.chat_message("user", avatar="🎓").write(msg["content"])

                raspuns_student = st.chat_input("Răspunde profesorului...")
                if raspuns_student:
                    st.session_state.chat_oral.append({"role": "user", "content": raspuns_student})
                    istoric = [{"role": "system",
                                "content": f"Ești examinator. Curs: {st.session_state.text_curs_memorie[:4000]}"}] + st.session_state.chat_oral
                    client = Groq(api_key=API_KEY_GROQ)
                    comp = client.chat.completions.create(model="openai/gpt-oss-120b", messages=istoric,
                                                          temperature=0.7)
                    st.session_state.chat_oral.append({"role": "assistant", "content": comp.choices[0].message.content})
                    st.rerun()

                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    if st.button("📊 Finalizează și Cere Nota"):
                        with st.spinner("Se evaluează performanța..."):
                            prompt_ev = f"Pe baza conversației de mai jos, oferă notă (1-10) și feedback detaliat:\n{json.dumps(st.session_state.chat_oral, ensure_ascii=False)}"
                            client = Groq(api_key=API_KEY_GROQ)
                            comp = client.chat.completions.create(model="openai/gpt-oss-120b",
                                                                  messages=[{"role": "user", "content": prompt_ev}],
                                                                  temperature=0.3)
                            st.session_state.chat_oral.append({"role": "assistant",
                                                               "content": f"📋 **REZULTAT EXAMEN:**\n\n{comp.choices[0].message.content}"})
                            st.rerun()
                with c_s2:
                    if st.button("🔄 Resetează"):
                        st.session_state.chat_oral = []
                        st.session_state.examen_oral_pornit = False
                        st.rerun()

    # --- 3. PLAN PRO & STRIPE PAYMENT LINK ---
    elif meniu == "💎 Plan PRO":
        st.title("💎 Deblochează Examora PRO")
        st.markdown(
            "<p style='color: #9ca3af;'>Treci la nivelul următor și pregătește-te pentru sesiune fără stres.</p>",
            unsafe_allow_html=True)

        col_f, col_p = st.columns(2)

        with col_f:
            st.markdown("""
                <div class="pricing-card">
                    <h3>Planul Free</h3>
                    <p style='color: #9ca3af; font-size: 24px; font-weight: bold;'>0 EUR</p>
                    <p>✓ Teste grilă limitate</p>
                    <p>✓ Cursuri de dimensiuni mici</p>
                    <p>✓ Examen oral de bază</p>
                </div>
            """, unsafe_allow_html=True)

        with col_p:
            st.markdown("""
                <div class="pro-card">
                    <h3>Planul PRO 👑</h3>
                    <p style='color: #818cf8; font-size: 24px; font-weight: bold;'>6 EUR / lună</p>
                    <p>✨ Grile nelimitate din orice materie</p>
                    <p>✨ Cărți și tratate integrale în PDF</p>
                    <p>✨ Profesor AI nelimitat + Note oficiale</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if not st.session_state.plan_pro:
                # Link-ul tău real de plată Stripe integrat direct
                stripe_payment_url = "https://buy.stripe.com/test_cNi5kCcr03aWbKC8aCak000"

                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <a href="{stripe_payment_url}" target="_blank">
                            <button style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; border: none; padding: 14px 28px; font-size: 16px; font-weight: bold; border-radius: 10px; cursor: pointer; width: 100%; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);">
                                💳 Plătește 6 EUR/lună prin Stripe
                            </button>
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🛠️ Simulează Plata Reușită (Pentru Teste)", use_container_width=True):
                    st.session_state.plan_pro = True
                    st.success("Plată simulată cu succes! Contul este acum PRO.")
                    st.balloons()
                    st.rerun()
            else:
                st.success("✅ Ai deja abonamentul PRO activ!")

    # --- 4. SETĂRI CONT ---
    elif meniu == "⚙️ Setări Cont":
        st.title("⚙️ Setări Cont & Preferințe")
        st.text_input("Email cont", value=str(st.session_state.utilizator), disabled=True)
        st.text_input("Parolă nouă", type="password")
        if st.button("Salvează Setările"):
            st.success("Modificări salvate!")

        st.markdown("### Preferințe AI")
        st.selectbox("Dificultate", ["Standard", "Avansat / Licență"])
        st.toggle("Efecte vizuale (Confetti)", value=True)