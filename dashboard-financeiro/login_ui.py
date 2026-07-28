from html import escape

import streamlit as st


def render_login(User, login_user, reset_password_with_code, logger):
    """Tela de login nativa, segura e responsiva."""

    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"],
        header[data-testid="stHeader"],
        #MainMenu,
        footer {
            display: none !important;
        }

        html, body, .stApp, .stMain {
            width: 100% !important;
            min-height: 100% !important;
            background: #0D0D1A !important;
        }

        [data-testid="stAppViewContainer"] {
            width: 100% !important;
            min-height: 100dvh !important;
            background: linear-gradient(90deg, #0D0D1A 0 42%, #11112A 42% 100%) !important;
        }

        .stMainBlockContainer, .block-container {
            width: 100% !important;
            max-width: none !important;
            min-height: 100dvh !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.login-anchor) {
            position: fixed !important;
            inset: 0 !important;
            width: 100vw !important;
            height: 100dvh !important;
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
            min-height: 100dvh !important;
            align-items: stretch !important;
            overflow: hidden !important;
            z-index: 1 !important;
        }

        div[data-testid="stColumn"]:has(.login-anchor),
        div[data-testid="stColumn"]:has(.showcase-anchor) {
            min-height: 100dvh !important;
        }

        div[data-testid="stColumn"]:has(.login-anchor) {
            background: #0D0D1A;
            border-right: 1px solid #1E1E3A;
        }

        div[data-testid="stColumn"]:has(.showcase-anchor) {
            position: relative !important;
            overflow: hidden !important;
            background:
                linear-gradient(135deg, rgba(83, 74, 183, .20), transparent 34%),
                linear-gradient(220deg, rgba(127, 119, 221, .24), transparent 42%),
                #11112A;
        }

        div[data-testid="stColumn"]:has(.showcase-anchor)::before {
            content: "" !important;
            position: absolute !important;
            inset: 0 !important;
            pointer-events: none !important;
            background:
                radial-gradient(circle at 23% 25%, rgba(127, 119, 221, .22) 0 9%, transparent 9.5%),
                radial-gradient(circle at 75% 72%, rgba(83, 74, 183, .18) 0 17%, transparent 17.5%),
                repeating-radial-gradient(ellipse at 15% 85%,
                    rgba(226, 232, 240, .14) 0 1px,
                    transparent 1px 16px);
            opacity: .65;
        }

        div[data-testid="stColumn"]:has(.showcase-anchor)::after {
            content: "" !important;
            position: absolute !important;
            top: 56px !important;
            right: 64px !important;
            width: 120px !important;
            height: 180px !important;
            pointer-events: none !important;
            opacity: .62;
            background-image:
                radial-gradient(circle, rgba(226, 232, 240, .82) 1.4px, transparent 1.6px);
            background-size: 14px 14px;
            mask-image: linear-gradient(180deg, #000, transparent);
        }

        div[data-testid="stColumn"]:has(.login-anchor) > div,
        div[data-testid="stColumn"]:has(.showcase-anchor) > div {
            min-height: 100dvh !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }

        div[data-testid="stColumn"]:has(.login-anchor) > div {
            padding: clamp(36px, 5vw, 88px) !important;
        }

        div[data-testid="stColumn"]:has(.showcase-anchor) > div {
            align-items: center !important;
            padding: 40px !important;
            position: relative !important;
            z-index: 2 !important;
        }

        .login-logo {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 40px;
        }

        .login-logo-icon {
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #534AB7, #7F77DD);
            border-radius: 8px;
        }

        .login-logo-text {
            color: #7F77DD;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: .12em;
            text-transform: uppercase;
        }

        .login-greeting {
            color: #E2E8F0;
            font-size: clamp(27px, 2vw, 34px);
            font-weight: 700;
            margin-bottom: 4px;
        }

        .login-subtitle {
            color: #62628F;
            font-size: 13px;
            margin-bottom: 24px;
        }

        div[data-testid="stColumn"]:has(.login-anchor) label p {
            color: #A0A0C0 !important;
            font-size: 11px !important;
            font-weight: 600 !important;
            letter-spacing: .05em !important;
            text-transform: uppercase !important;
        }

        div[data-testid="stColumn"]:has(.login-anchor) input {
            color: #E2E8F0 !important;
            background: #11112A !important;
            border: 1px solid #2A2A4A !important;
            border-radius: 7px !important;
        }

        div[data-testid="stColumn"]:has(.login-anchor) input:focus {
            border-color: #6B63D9 !important;
            box-shadow: 0 0 0 2px rgba(83,74,183,.22) !important;
        }

        div[data-testid="stColumn"]:has(.login-anchor)
        div[data-testid="InputInstructions"] {
            display: none !important;
        }

        div[data-testid="stColumn"]:has(.login-anchor)
        div[data-testid="stFormSubmitButton"] button {
            width: 100% !important;
            color: #FFF !important;
            background: linear-gradient(135deg, #534AB7, #7F77DD) !important;
            border: 0 !important;
            border-radius: 7px !important;
            font-weight: 600 !important;
        }

        .login-message {
            min-height: 22px;
            margin-top: 10px;
            color: #F09595;
            font-size: 12px;
            text-align: center;
        }

        .login-message.success {
            color: #1D9E75;
        }

        .login-forgot {
            margin-top: 6px;
            color: #7F77DD;
            font-size: 12px;
            text-align: center;
            text-decoration: underline;
        }

        .showcase-card {
            width: min(100%, 320px);
            padding: 28px 24px;
            color: #E2E8F0;
            background: rgba(13, 13, 26, .78);
            border: 1px solid rgba(127, 119, 221, .34);
            border-radius: 20px;
            box-shadow: 0 28px 70px rgba(0,0,0,.46);
            backdrop-filter: blur(12px);
        }

        .showcase-badge {
            display: inline-block;
            margin-bottom: 12px;
            padding: 4px 11px;
            color: #FFF;
            background: linear-gradient(135deg, #534AB7, #7F77DD);
            border-radius: 20px;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: .07em;
            text-transform: uppercase;
        }

        .showcase-title {
            margin-bottom: 18px;
            font-size: 18px;
            font-weight: 700;
            line-height: 1.3;
        }

        .showcase-chart {
            height: 90px;
            padding: 10px 14px;
            display: flex;
            align-items: flex-end;
            gap: 7px;
            background: #11112A;
            border: 1px solid #1E1E3A;
            border-radius: 10px;
        }

        .showcase-bar {
            width: 26px;
            background: #242440;
            border-radius: 4px 4px 0 0;
        }

        .showcase-bar.accent {
            background: linear-gradient(180deg, #7F77DD, #534AB7);
        }

        .showcase-values {
            display: flex;
            gap: 8px;
            margin-top: 14px;
        }

        .showcase-value {
            flex: 1;
            padding: 8px 10px;
            background: #11112A;
            border: 1px solid #1E1E3A;
            border-radius: 9px;
        }

        .showcase-label {
            color: #62628F;
            font-size: 9px;
            letter-spacing: .06em;
            text-transform: uppercase;
        }

        .showcase-money {
            color: #1D9E75;
            font-family: monospace;
            font-size: 12px;
            font-weight: 700;
        }

        .showcase-money.red {
            color: #F09595;
        }

        .showcase-cta {
            margin-top: 14px;
            padding: 9px;
            color: #7F77DD;
            border: 1px solid #534AB7;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: .07em;
            text-align: center;
            text-transform: uppercase;
        }

        @media (max-width: 800px) {
            div[data-testid="stHorizontalBlock"]:has(.login-anchor) {
                display: block !important;
            }

            div[data-testid="stColumn"]:has(.login-anchor) {
                width: 100% !important;
                min-height: 100dvh !important;
                border-right: 0;
            }

            div[data-testid="stColumn"]:has(.showcase-anchor) {
                display: none !important;
            }

            [data-testid="stAppViewContainer"] {
                background: #0D0D1A !important;
            }

            div[data-testid="stColumn"]:has(.login-anchor) > div {
                padding: 30px 24px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    login_column, showcase_column = st.columns([42, 58], gap=None)

    with login_column:
        st.markdown('<div class="login-anchor"></div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="login-logo">
                <div class="login-logo-icon">💰</div>
                <span class="login-logo-text">Dashboard Financeiro</span>
            </div>
            <div class="login-greeting">Olá!</div>
            <div class="login-subtitle">Seja bem-vindo de volta</div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Usuário",
                placeholder="seu_usuario",
                autocomplete="username",
            )
            password = st.text_input(
                "Senha",
                type="password",
                placeholder="••••••••",
                autocomplete="current-password",
            )
            submitted = st.form_submit_button("Entrar", use_container_width=True)

        if submitted:
            username = username.strip()

            if not username or not password:
                st.session_state.login_erro = "❌ Preencha usuário e senha."
            else:
                try:
                    user_data = login_user(username, password)
                    if user_data:
                        st.session_state.user = User(
                            id=user_data[0],
                            username=user_data[1],
                            is_admin=bool(user_data[2]),
                        )
                        st.session_state.pagina = "visao"
                        st.session_state.pop("login_erro", None)
                        logger.info("User logged in: %s", username)
                        st.rerun()
                    else:
                        st.session_state.login_erro = (
                            "❌ Usuário ou senha incorretos."
                        )
                except Exception:
                    logger.exception("Erro durante o login")
                    st.session_state.login_erro = (
                        "❌ Não foi possível entrar. Tente novamente."
                    )

        message = escape(st.session_state.get("login_erro", ""))
        message_class = (
            "login-message success"
            if message.startswith("✅")
            else "login-message"
        )
        st.markdown(
            f'<div class="{message_class}">{message}</div>',
            unsafe_allow_html=True,
        )
        if st.button(
            "Esqueceu sua senha?",
            key="abrir_recuperacao_senha",
            use_container_width=True,
        ):
            st.session_state.mostrar_recuperacao_senha = (
                not st.session_state.get("mostrar_recuperacao_senha", False)
            )

        if st.session_state.get("mostrar_recuperacao_senha", False):
            st.caption(
                "Solicite ao administrador um código temporário e use-o abaixo. "
                "O código expira em 15 minutos."
            )
            with st.form("password_recovery_form", clear_on_submit=False):
                recovery_username = st.text_input(
                    "Usuário",
                    key="recovery_username",
                )
                recovery_code = st.text_input(
                    "Código temporário",
                    key="recovery_code",
                    placeholder="Ex.: A1B2C3D4E5F6",
                )
                new_password = st.text_input(
                    "Nova senha",
                    type="password",
                    key="recovery_new_password",
                )
                confirm_password = st.text_input(
                    "Confirmar nova senha",
                    type="password",
                    key="recovery_confirm_password",
                )
                recover = st.form_submit_button(
                    "Redefinir senha",
                    use_container_width=True,
                )

            if recover:
                recovery_username = recovery_username.strip()
                recovery_code = recovery_code.strip()
                if not recovery_username or not recovery_code:
                    st.error("Informe o usuário e o código temporário.")
                elif len(new_password) < 8:
                    st.error("A nova senha deve ter pelo menos 8 caracteres.")
                elif new_password != confirm_password:
                    st.error("As senhas informadas não coincidem.")
                elif reset_password_with_code(
                    recovery_username,
                    recovery_code,
                    new_password,
                ):
                    st.session_state.mostrar_recuperacao_senha = False
                    st.session_state.login_erro = (
                        "✅ Senha alterada. Entre com a nova senha."
                    )
                    st.rerun()
                else:
                    st.error("Código inválido, usado ou expirado.")

    with showcase_column:
        st.markdown(
            """
            <div class="showcase-anchor"></div>
            <div class="showcase-card">
                <div class="showcase-badge">✦ Visão do mês</div>
                <div class="showcase-title">Gestão Financeira Inteligente</div>
                <div class="showcase-chart">
                    <div class="showcase-bar" style="height:32px"></div>
                    <div class="showcase-bar" style="height:50px"></div>
                    <div class="showcase-bar accent" style="height:76px"></div>
                    <div class="showcase-bar" style="height:58px"></div>
                    <div class="showcase-bar accent" style="height:70px"></div>
                </div>
                <div class="showcase-values">
                    <div class="showcase-value">
                        <div class="showcase-label">Recebimentos</div>
                        <div class="showcase-money">R$ 0,00</div>
                    </div>
                    <div class="showcase-value">
                        <div class="showcase-label">Despesas</div>
                        <div class="showcase-money red">R$ 0,00</div>
                    </div>
                </div>
                <div class="showcase-cta">Acesse o painel →</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.stop()
