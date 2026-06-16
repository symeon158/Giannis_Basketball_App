import streamlit as strl
import random
from collections import deque
import pandas as pd

# --- ΡΥΘΜΙΣΕΙΣ & ΔΕΔΟΜΕΝΑ ---
strl.set_page_config(page_title="Basketball Quiz App", page_icon="🏀", layout="centered")

MAX_QUESTIONS = 15

# Βάση δεδομένων
all_questions = [
    # --- Η ΕΡΩΤΗΣΗ ΠΑΓΙΔΑ ---
    {"q": "Ποια είναι η καλύτερη ελληνική ομάδα;", "opts": ["Ολυμπιακός", "ΠΑΟ", "ΠΑΟΚ", "ΑΕΚ"], "ans": "C", "troll": True, "diff": "Μυστικό"},
    
    # --- ΕΥΚΟΛΑ ---
    {"q": "Πόσοι παίκτες μιας ομάδας βρίσκονται ταυτόχρονα στο παρκέ;", "opts": ["4", "5", "6", "7"], "ans": "B", "troll": False, "diff": "Εύκολο"},
    {"q": "Από ποια χώρα κατάγεται ο Γιάννης Αντετοκούνμπος;", "opts": ["Νιγηρία", "Ελλάδα", "ΗΠΑ", "Ισπανία"], "ans": "B", "troll": False, "diff": "Εύκολο"},
    {"q": "Πόσες περιόδους (δεκάλεπτα) έχει ένας κανονικός αγώνας μπάσκετ;", "opts": ["2", "3", "4", "5"], "ans": "C", "troll": False, "diff": "Εύκολο"},
    {"q": "Ποιο είναι το παρατσούκλι της Εθνικής Ελλάδος μπάσκετ;", "opts": ["Η επίσημη αγαπημένη", "Η 'χρυσή' ομάδα", "Τα λιοντάρια", "Οι αετοί"], "ans": "A", "troll": False, "diff": "Εύκολο"},
    {"q": "Πόσους πόντους παίρνει μια ομάδα για κάθε εύστοχη ελεύθερη βολή;", "opts": ["1", "2", "3", "0.5"], "ans": "A", "troll": False, "diff": "Εύκολο"},
    {"q": "Ποια ομάδα του NBA έχει ως σήμα ένα ελάφι (Bucks);", "opts": ["Σικάγο", "Μιλγουόκι", "Μαϊάμι", "Βοστώνη"], "ans": "B", "troll": False, "diff": "Εύκολο"},
    {"q": "Τι χρώμα έχει η μπάλα στους επίσημους αγώνες μπάσκετ;", "opts": ["Κίτρινο", "Πορτοκαλί", "Καφέ", "Κόκκινο"], "ans": "B", "troll": False, "diff": "Εύκολο"},

    # --- ΜΕΤΡΙΑ ---
    {"q": "Ποιος παίκτης έχει το παρατσούκλι 'Air' στην ιστορία του NBA;", "opts": ["LeBron James", "Kobe Bryant", "Michael Jordan", "Shaquille O'Neal"], "ans": "C", "troll": False, "diff": "Μέτριο"},
    {"q": "Πόσα δευτερόλεπτα έχει μια ομάδα για να εκδηλώσει επίθεση;", "opts": ["14", "20", "24", "30"], "ans": "C", "troll": False, "diff": "Μέτριο"},
    {"q": "Ποιος είναι ο πρώτος σκόρερ όλων των εποχών στην ιστορία του NBA;", "opts": ["Michael Jordan", "Kobe Bryant", "LeBron James", "Kareem Abdul-Jabbar"], "ans": "C", "troll": False, "diff": "Μέτριο"},
    {"q": "Ποια ελληνική ομάδα έχει τα περισσότερα τρόπαια EuroLeague;", "opts": ["Ολυμπιακός", "Παναθηναϊκός", "ΑΕΚ", "ΠΑΟΚ"], "ans": "B", "troll": False, "diff": "Μέτριο"},
    {"q": "Πόσα φάουλ χρειάζεται να κάνει ένας παίκτης στην EuroLeague για να αποβληθεί;", "opts": ["4", "5", "6", "7"], "ans": "B", "troll": False, "diff": "Μέτριο"},
    {"q": "Ποιος θρυλικός Έλληνας παίκτης είχε το παρατσούκλι 'Γκάγκστερ';", "opts": ["Παναγιώτης Γιαννάκης", "Νίκος Γκάλης", "Φάνης Χριστοδούλου", "Δημήτρης Διαμαντίδης"], "ans": "B", "troll": False, "diff": "Μέτριο"},
    {"q": "Πόσα λεπτά διαρκεί η παράταση σε έναν αγώνας μπάσκετ;", "opts": ["3 λεπτά", "5 λεπτά", "8 λεπτά", "10 λεπτά"], "ans": "B", "troll": False, "diff": "Μέτριο"},
    {"q": "Σε ποια πόλη βρίσκεται η έδρα της Ζαλγκίρις;", "opts": ["Βίλνιους", "Κάουνας", "Ρίγα", "Ταλίν"], "ans": "B", "troll": False, "diff": "Μέτριο"},

    # --- ΔΥΣΚΟΛΑ ---
    {"q": "Ποια ομάδα έχει κατακτήσει τα περισσότερα πρωταθλήματα NBA στην ιστορία (ισοπαλία);", "opts": ["Lakers & Celtics", "Bulls & Warriors", "Spurs & Heat", "Knicks & Nets"], "ans": "A", "troll": False, "diff": "Δύσκολο"},
    {"q": "Πόσα δευτερόλεπτα μπορεί να μείνει ένας επιθετικός μέσα στη ρακέτα;", "opts": ["3", "5", "8", "24"], "ans": "A", "troll": False, "diff": "Δύσκολο"},
    {"q": "Ποιο είναι το ύψος της στεφάνης του μπάσκετ από το έδαφος (σε μέτρα);", "opts": ["2.95 μ.", "3.05 μ.", "3.15 μ.", "3.25 μ."], "ans": "B", "troll": False, "diff": "Δύσκολο"},
    {"q": "Πόσα δευτερόλεπτα έχει μια ομάδα για να περάσει τη μπάλα στο μπροστινό γήπεδο;", "opts": ["5", "8", "10", "14"], "ans": "B", "troll": False, "diff": "Δύσκολο"},
    {"q": "Ποιος παίκτης είναι γνωστός για το απίστευτο σουτ του έξω από τα 9 μέτρα;", "opts": ["Stephen Curry", "Klay Thompson", "Kevin Durant", "Kyrie Irving"], "ans": "A", "troll": False, "diff": "Δύσκολο"},
    {"q": "Ποιος Σέρβος σέντερ των Ντένβερ Νάγκετς έχει κερδίσει πολλαπλά βραβεία MVP;", "opts": ["Nikola Jokic", "Bogdan Bogdanovic", "Luka Doncic", "Vlade Divac"], "ans": "A", "troll": False, "diff": "Δύσκολο"},
    {"q": "Ποιος προπονητής έχει κατακτήσει τις περισσότερες EuroLeague;", "opts": ["Zeljko Obradovic", "Ettore Messina", "Ergin Ataman", "Pablo Laso"], "ans": "A", "troll": False, "diff": "Δύσκολο"},
    {"q": "Πόσα φάουλ ομαδικά πρέπει να κάνει μια ομάδα σε ένα δεκάλεπτο για να στείλει τον αντίπαλο στις βολές;", "opts": ["3", "4", "5", "6"], "ans": "B", "troll": False, "diff": "Δύσκολο"}
]

# --- SIDEBAR: ΥΠΟΓΡΑΦΗ ΔΗΜΙΟΥΡΓΟΥ ---
strl.sidebar.title("🏀 Info")
strl.sidebar.info("Ένα διασκεδαστικό κουίζ μπάσκετ για την παρέα!")
strl.sidebar.markdown("---")
strl.sidebar.markdown("👨‍💻 **Δημιουργός:**")
strl.sidebar.markdown("### Γιάννης Παπαδόπουλος")

# --- ΑΡΧΙΚΟΠΟΙΗΣΗ GLOBAL STATE (Leaderboard) ---
if "leaderboard" not in strl.session_state:
    strl.session_state.leaderboard = []

# --- ΑΡΧΙΚΟΠΟΙΗΣΗ GAME STATE ---
if "app_page" not in strl.session_state:
    strl.session_state.app_page = "login" 
if "username" not in strl.session_state:
    strl.session_state.username = ""
if "team" not in strl.session_state:
    strl.session_state.team = ""
if "fav_player" not in strl.session_state:
    strl.session_state.fav_player = ""

def init_game(diff):
    strl.session_state.current_diff = diff
    
    filtered = [q for q in all_questions if not q.get("troll")]
    if diff != "Τυχαίες (Mix)":
        filtered = [q for q in filtered if q["diff"] == diff]
        
    random.shuffle(filtered)
    queue_list = filtered[:MAX_QUESTIONS]
    
    if random.random() < 0.35:
        troll_q = all_questions[0]
        insert_idx = random.randint(1, len(queue_list)-1)
        queue_list.insert(insert_idx, troll_q)
        
    strl.session_state.question_queue = deque(queue_list)
    strl.session_state.initial_count = len(queue_list)
    strl.session_state.unique_completed = 0 
    strl.session_state.score = 0  
    strl.session_state.mistakes = 0 
    strl.session_state.streak = 0
    strl.session_state.current_question = None
    strl.session_state.feedback = None
    strl.session_state.app_page = "quiz"

def get_next_question():
    if len(strl.session_state.question_queue) == 0:
        strl.session_state.leaderboard.append({
            "Όνομα": strl.session_state.username,
            "Ομάδα": strl.session_state.team,
            "Αγ. Παίκτης": strl.session_state.fav_player,
            "Επίπεδο": strl.session_state.current_diff,
            "Σκορ (1η)": strl.session_state.score,
            "Λάθη": strl.session_state.mistakes
        })
        strl.session_state.app_page = "game_over"
    else:
        strl.session_state.current_question = strl.session_state.question_queue.popleft()
        strl.session_state.feedback = None


# ==========================================
# ΣΕΛΙΔΑ 1: LOBBY & ΕΓΓΡΑΦΗ ΧΡΗΣΤΗ
# ==========================================
if strl.session_state.app_page == "login":
    strl.title("🏀 Καλώς ήρθες στο Basketball Quiz!")
    strl.markdown("Δείξε μας τι ξέρεις από μπάσκετ. Φτιάξε το προφίλ σου για να ξεκινήσουμε!")
    
    with strl.form("login_form"):
        player_name = strl.text_input("Το Όνομά σου / Nickname:")
        
        teams_list = ["Ολυμπιακός", "Παναθηναϊκός", "ΑΕΚ", "ΠΑΟΚ", "Άρης", "Ηρακλής", 
                      "Φενέρμπαχτσε", "Εφές", "Ρεάλ Μαδρίτης", "Μπαρτσελόνα", "Μονακό", "Άλλη/Καμία"]
        fav_team = strl.selectbox("Ποια είναι η ομάδα σου;", teams_list)
        
        f_player = strl.text_input("Ποιος είναι ο αγαπημένος σου παίκτης;")
        
        selected_diff = strl.radio("Επίλεξε Δυσκολία:", ["Εύκολο", "Μέτριο", "Δύσκολο", "Τυχαίες (Mix)"], horizontal=True)
        
        submitted = strl.form_submit_button("🚀 Έναρξη Παιχνιδιού!", type="primary")
        
        if submitted:
            if not player_name.strip():
                strl.error("Βάλε ένα όνομα για να παίξεις!")
            else:
                strl.session_state.username = player_name
                strl.session_state.team = fav_team
                strl.session_state.fav_player = f_player.strip() if f_player.strip() else "Κανένας"
                init_game(selected_diff)
                strl.rerun()

    strl.markdown("---")
    if strl.session_state.leaderboard:
        strl.subheader("🏆 Leaderboard (Σημερινά Αποτελέσματα)")
        df_lb = pd.DataFrame(strl.session_state.leaderboard)
        df_lb = df_lb.sort_values(by=["Σκορ (1η)", "Λάθη"], ascending=[False, True]).reset_index(drop=True)
        df_lb.index = df_lb.index + 1
        strl.dataframe(df_lb, use_container_width=True)
        
    strl.markdown("<br><center><i>Ανάπτυξη και Σχεδιασμός: Γιάννης Παπαδόπουλος © 2026</i></center>", unsafe_allow_html=True)


# ==========================================
# ΣΕΛΙΔΑ 2: ΤΟ ΚΟΥΙΖ
# ==========================================
elif strl.session_state.app_page == "quiz":
    strl.title(f"🏀 {strl.session_state.username} | 🛡️ {strl.session_state.team} | ⭐ {strl.session_state.fav_player}")

    if strl.session_state.current_question is None:
        get_next_question()

    progress_val = strl.session_state.unique_completed / strl.session_state.initial_count if strl.session_state.initial_count > 0 else 0
    strl.progress(progress_val, text=f"Πρόοδος: Έχεις βρει {strl.session_state.unique_completed} από {strl.session_state.initial_count} ερωτήσεις")
    
    col1, col2, col3 = strl.columns(3)
    col1.metric(label="Σκορ (Με την 1η)", value=strl.session_state.score)
    col2.metric(label="Λάθη", value=strl.session_state.mistakes)
    col3.metric(label="🔥 Σερί", value=strl.session_state.streak)

    strl.markdown("---")

    q_data = strl.session_state.current_question

    diff_badge = f"[{q_data['diff']}]" if "diff" in q_data and q_data["diff"] != "Μυστικό" else ""
    repeat_badge = " 🔄 (Επανάληψη)" if q_data.get("is_repeat") else ""
    strl.subheader(f"❓ {diff_badge}{repeat_badge} {q_data['q']}")

    mapping = ["A", "B", "C", "D"]
    options_with_letters = [f"{mapping[i]}) {opt}" for i, opt in enumerate(q_data["opts"])]

    is_disabled = strl.session_state.feedback is not None

    radio_key = f"radio_{strl.session_state.unique_completed}_{strl.session_state.mistakes}"
    user_choice = strl.radio("Επιλέξτε την απάντησή σας:", options_with_letters, index=None, key=radio_key, disabled=is_disabled)

    if strl.button("🎯 Υποβολή Απάντησης", use_container_width=True, disabled=is_disabled):
        if user_choice is None:
            strl.warning("Παρακαλώ επιλέξτε μια απάντηση πρώτα!")
        else:
            chosen_letter = user_choice[0] 
            
            if chosen_letter == q_data["ans"]:
                strl.session_state.unique_completed += 1
                strl.session_state.streak += 1 
                
                if not q_data.get("is_repeat"):
                    strl.session_state.score += 1
                
                if q_data.get("troll"):
                    strl.session_state.feedback = ("success", f"🦅 ΜΠΑΜ! Έτσι μπράβο ρε {strl.session_state.username}! Μόνο ΠΑΟΚ!")
                    strl.balloons() 
                else:
                    msg = "✅ ΣΩΣΤΟ! Εξαιρετικό σουτ!"
                    if strl.session_state.streak >= 3:
                        msg = f"✅ ΣΩΣΤΟ! 🔥 Είσαι On Fire ({strl.session_state.streak} σερί) σαν τον {strl.session_state.fav_player}!"
                    strl.session_state.feedback = ("success", msg)
            else:
                strl.session_state.mistakes += 1
                strl.session_state.streak = 0 
                
                if q_data.get("troll"):
                    team_taunt = f"Είσαι {strl.session_state.team}" if strl.session_state.team != "Άλλη/Καμία" else "Παίζεις μπάσκετ"
                    player_taunt = f"έχεις είδωλο τον {strl.session_state.fav_player}" if strl.session_state.fav_player != "Κανένας" else ""
                    strl.session_state.feedback = ("error", f"❌ ΛΑΘΟΣ! {team_taunt}, {player_taunt} και νομίζεις ξέρεις; Μόνο ΠΑΟΚ ρε! 🦅")
                else:
                    player_trash = f"Ούτε ο {strl.session_state.fav_player} δεν έριχνε τέτοια τούβλα!" if strl.session_state.fav_player != "Κανένας" else "Έσπασες τα καλάθια!"
                    strl.session_state.feedback = ("error", f"❌ ΛΑΘΟΣ! {player_trash} Η σωστή ήταν η {q_data['ans']}. (Πάει στο τέλος)")
                
                repeat_q = q_data.copy()
                repeat_q["is_repeat"] = True
                strl.session_state.question_queue.append(repeat_q)
            
            strl.rerun() 

    if strl.session_state.feedback:
        status, msg = strl.session_state.feedback
        if status == "success":
            strl.success(msg)
        else:
            strl.error(msg)
        
        btn_text = "➡️ Επόμενη Ερώτηση" if len(strl.session_state.question_queue) > 0 else "🏆 Τέλος! Πάμε στα Αποτελέσματα!"
        
        if strl.button(btn_text, type="primary", use_container_width=True):
            get_next_question()
            strl.rerun()

# ==========================================
# ΣΕΛΙΔΑ 3: ΑΠΟΤΕΛΕΣΜΑΤΑ
# ==========================================
elif strl.session_state.app_page == "game_over":
    strl.title("🏆 Τέλος Παιχνιδιού!")
    strl.markdown(f"Μπράβο **{strl.session_state.username}**! Το σκορ σου καταγράφηκε.")
    strl.markdown("---")
    
    col1, col2 = strl.columns(2)
    col1.metric(label="✅ Σκορ (Με την 1η)", value=f"{strl.session_state.score} / {strl.session_state.initial_count}")
    col2.metric(label="❌ Συνολικά Λάθη", value=strl.session_state.mistakes)
    
    percentage = (strl.session_state.score / strl.session_state.initial_count) * 100 if strl.session_state.initial_count > 0 else 0
    
    strl.markdown("### Αξιολόγηση Εμφάνισης:")
    if percentage >= 80:
        strl.success(f"🔥 Είσαι MVP! Ο {strl.session_state.fav_player} θα ήταν περήφανος!")
        strl.balloons()
    elif percentage >= 50:
        strl.info("🏀 Τίμια εμφάνιση. Έχεις ταλέντο αλλά θέλεις δουλειά.")
    else:
        strl.error(f"🧱 Ούτε σε μπασκέτα σε λούνα παρκ... Θέλεις προπόνηση!")
        
    strl.markdown("---")
    if strl.button("🏠 Επιστροφή στο Αρχικό Μενού", use_container_width=True, type="primary"):
        strl.session_state.app_page = "login"
        strl.rerun()
        
    strl.markdown("<br><center><i>Ανάπτυξη και Σχεδιασμός: Γιάννης Παπαδόπουλος © 2026</i></center>", unsafe_allow_html=True)
