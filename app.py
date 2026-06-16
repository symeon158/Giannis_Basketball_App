# Αυτό το αρχείο κάνει το ΣΚΟΥΡΟ (dark) θέμα προεπιλογή για όλους,
# ανεξάρτητα από τις ρυθμίσεις του υπολογιστή/φυλλομετρητή τους.
#
# ΠΟΥ ΜΠΑΙΝΕΙ:
#   Στον ΙΔΙΟ φάκελο που τρέχεις το `streamlit run`, φτιάξε υποφάκελο
#   με όνομα  .streamlit  και βάλε αυτό το αρχείο μέσα, δηλαδή:
#
#     ο_φάκελός_σου/
#       ├── basketball_quiz_app.py
#       └── .streamlit/
#             └── config.toml
#
# Μετά τρέξε ξανά:  streamlit run basketball_quiz_app.py

[theme]
base = "dark"
primaryColor = "#E8843A"            # μπασκετικό πορτοκαλί (κουμπιά/τόνοι)
backgroundColor = "#0E1A2B"         # σκούρο navy γηπέδου
secondaryBackgroundColor = "#16263C" # πάνελ / sidebar
textColor = "#F4EDE0"               # κρεμ γραμμές γηπέδου
font = "sans serif"

[client]
# Κρύβει το μενού αλλαγής θέματος ώστε να μένει πάντα σκούρο (προαιρετικό).
toolbarMode = "minimal"
