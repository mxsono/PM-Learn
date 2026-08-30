import streamlit as st
from supabase import create_client, Client

# Configuration de la page
st.set_page_config(page_title="PMP Learning Platform", layout="centered")

# Connexion à Supabase (utilisez les secrets Streamlit en production)
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://zujrcxegdjazqfduexbm.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_4U41r-EZVVb8tkgAvdnEOA_MXY_lKGB")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

# Gestion de l'état de session utilisateur
if "user" not in st.session_state:
    st.session_state.user = None

def get_progress(user_id):
    res = supabase.table("user_progress").select("module_2_unlocked").eq("id", user_id).execute()
    if res.data:
        return res.data[0]["module_2_unlocked"]
    else:
        # Créer la ligne si elle n'existe pas
        supabase.table("user_progress").insert({"id": user_id, "module_2_unlocked": False}).execute()
        return False

# Interface d'authentification si non connecté
if not st.session_state.user:
    st.title("Connexion - Académie PMP")
    
    tab1, tab2 = st.tabs(["Se connecter", "S'inscrire"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Mot de passe", type="password", key="login_password")
        if st.button("Connexion"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.success("Connexion réussie !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur de connexion : {e}")
                
    with tab2:
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Mot de passe (6 car. min)", type="password", key="reg_password")
        if st.button("Créer mon compte"):
            try:
                res = supabase.auth.sign_up({"email": reg_email, "password": reg_password})
                st.success("Compte créé ! Vérifiez vos e-mails ou connectez-vous.")
            except Exception as e:
                st.error(f"Erreur lors de l'inscription : {e}")
else:
    user_id = st.session_state.user.id
    is_module_2_unlocked = get_progress(user_id)
    
    # Barre latérale de navigation
    st.sidebar.title(f"Mon Espace PMP")
    st.sidebar.write(f"Connecté en tant que :\n{st.session_state.user.email}")
    
    menu = st.sidebar.radio("Navigation", ["Module 1 : Fondamentaux", "Module 2 : Agile & Scrum (Bloqué)", "Ressources"])
    
    if st.sidebar.button("Se déconnecter"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # Contenu des modules
    if menu == "Module 1 : Fondamentaux":
        st.header("Module 1 : Introduction au cadre PMI")
        st.markdown("Révisez les fondements de la gestion de projet prédictive et les processus clés.")
        
        st.subheader("Quiz de validation - Module 1")
        q1 = st.radio(
            "Quel est le rôle principal d'un chef de projet dans l'approche prédictive ?",
            ("Suivre strictement le plan et gérer les contraintes", "Laisser l'équipe s'auto-organiser totalement", "Coder les fonctionnalités du produit")
        )
        
        if st.button("Valider le quiz"):
            if q1 == "Suivre strictement le plan et gérer les contraintes":
                # Mettre à jour la base de données Supabase pour débloquer le module 2
                supabase.table("user_progress").update({"module_2_unlocked": True}).eq("id", user_id).execute()
                st.success("Bonne réponse ! Le Module 2 est maintenant débloqué.")
                st.rerun()
            else:
                st.error("Mauvaise réponse. Relisez le cours et tentez à nouveau.")

    elif menu == "Module 2 : Agile & Scrum (Bloqué)":
        if is_module_2_unlocked:
            st.header("Module 2 : Approche Agile & Scrum")
            st.markdown("Ici vous apprenez le manifeste agile, les sprints, et la gestion des incertitudes.")
            st.info("Accès autorisé : Vous avez validé le quiz du Module 1.")
        else:
            st.warning("🔒 Module verrouillé. Vous devez réussir le quiz du Module 1 pour y accéder.")

    elif menu == "Ressources":
        st.header("Centre de Téléchargement")
        st.markdown("- [Modèle de Charte de Projet (PDF)](https://www.pmi.org)")
        st.markdown("- [Fiche mémo : Formules Earned Value Management](https://www.pmi.org)")
