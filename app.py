# ============================================================
#  🏀 BASKETBALL QUIZ ARENA — Streamlit edition
#  Αναβαθμισμένη έκδοση: χρονόμετρο, ζωές, σερί, βοήθειες,
#  πόντοι μπόνους, ήχοι, confetti και παράσημα (badges).
#
#  ΕΚΤΕΛΕΣΗ:   streamlit run basketball_quiz_app.py
#  ΑΠΑΙΤΗΣΕΙΣ: pip install --upgrade streamlit pandas
#  (Το ζωντανό χρονόμετρο θέλει Streamlit >= 1.37. Αν έχεις
#   παλιότερη έκδοση, το παιχνίδι παίζει κανονικά — απλώς το
#   ρολόι δεν "χτυπάει" κάθε δευτερόλεπτο.)
# ============================================================

import io
import time
import math
import wave
import struct
import random
from datetime import datetime
import pandas as pd
import streamlit as st

# Το gspread είναι προαιρετικό: αν δεν υπάρχει (π.χ. τοπικά χωρίς ρυθμίσεις),
# το παιχνίδι παίζει κανονικά με τοπικό leaderboard.
try:
    import gspread
    _HAS_GSPREAD = True
except Exception:
    _HAS_GSPREAD = False

# ------------------- ΡΥΘΜΙΣΕΙΣ -------------------
st.set_page_config(page_title="Basketball Quiz Arena", page_icon="🏀", layout="centered")

MAX_QUESTIONS = 12     # ερωτήσεις ανά παιχνίδι
START_LIVES   = 3
TIME_LIMIT    = 22     # δευτερόλεπτα ανά ερώτηση
TROLL_CHANCE  = 0.35
FAVORED_TEAM  = "ΠΑΟΚ"  # το easter-egg της ομάδας — άλλαξέ το ελεύθερα!

DIFF_BASE = {"Εύκολο": 1, "Μέτριο": 2, "Δύσκολο": 3}
LETTERS = ["A", "B", "C", "D"]

# --- Ρυθμίσεις leaderboard ---
# Πώς ομαδοποιούμε τις εγγραφές ώστε κάθε παίκτης να εμφανίζεται ΜΙΑ φορά.
# Για ομαδοποίηση μόνο με βάση το όνομα, βάλε: ["Όνομα"]
LEADERBOARD_GROUP = ["Όνομα"]
# "best" = κρατάμε το καλύτερο σκορ κάθε παίκτη · "total" = άθροισμα όλων
LEADERBOARD_MODE = "total"

# ------------------- ΒΑΣΗ ΕΡΩΤΗΣΕΩΝ -------------------
# diff: "Εύκολο" | "Μέτριο" | "Δύσκολο" ;  ans: γράμμα "A"-"D"
ALL_QUESTIONS = [
    # --- ΕΥΚΟΛΑ ---
    {"q": "Πόσοι παίκτες μιας ομάδας βρίσκονται ταυτόχρονα στο παρκέ;", "opts": ["4", "5", "6", "7"], "ans": "B", "diff": "Εύκολο"},
    {"q": "Από ποια χώρα κατάγεται ο Γιάννης Αντετοκούνμπο;", "opts": ["Νιγηρία", "Ελλάδα", "ΗΠΑ", "Ισπανία"], "ans": "B", "diff": "Εύκολο"},
    {"q": "Πόσες περιόδους (δεκάλεπτα) έχει ένας κανονικός αγώνας μπάσκετ;", "opts": ["2", "3", "4", "5"], "ans": "C", "diff": "Εύκολο"},
    {"q": "Πόσους πόντους παίρνεις για κάθε εύστοχη ελεύθερη βολή;", "opts": ["1", "2", "3", "μισό"], "ans": "A", "diff": "Εύκολο"},
    {"q": "Ποια ομάδα του NBA έχει σήμα ένα ελάφι (Bucks);", "opts": ["Σικάγο", "Μιλγουόκι", "Μαϊάμι", "Βοστώνη"], "ans": "B", "diff": "Εύκολο"},
    {"q": "Τι χρώμα έχει η μπάλα στους επίσημους αγώνες μπάσκετ;", "opts": ["Κίτρινο", "Πορτοκαλί", "Καφέ", "Κόκκινο"], "ans": "B", "diff": "Εύκολο"},
    {"q": "Πόσους πόντους αξίζει ένα κανονικό καλάθι μέσα στο γήπεδο;", "opts": ["1", "2", "3", "4"], "ans": "B", "diff": "Εύκολο"},
    {"q": "Σε ποια χώρα εφευρέθηκε το άθλημα του μπάσκετ;", "opts": ["Ελλάδα", "ΗΠΑ", "Καναδάς", "Ισπανία"], "ans": "B", "diff": "Εύκολο"},
    {"q": "Με ποιο μέρος του σώματος ΔΕΝ επιτρέπεται να παίξεις σκόπιμα την μπάλα;", "opts": ["Χέρι", "Κεφάλι", "Πόδι", "Στήθος"], "ans": "C", "diff": "Εύκολο"},
    {"q": "Πώς είναι το παρατσούκλι του Γιάννη Αντετοκούνμπο στο NBA;", "opts": ["Greek Freak", "The King", "Air", "The Beard"], "ans": "A", "diff": "Εύκολο"},
    {"q": "Πόσα καλάθια (μπασκέτες) υπάρχουν σε ένα γήπεδο;", "opts": ["1", "2", "3", "4"], "ans": "B", "diff": "Εύκολο"},

    # --- ΜΕΤΡΙΑ ---
    {"q": "Ποιος παίκτης έχει το παρατσούκλι «Air» στην ιστορία του NBA;", "opts": ["LeBron James", "Kobe Bryant", "Michael Jordan", "Shaquille O'Neal"], "ans": "C", "diff": "Μέτριο"},
    {"q": "Πόσα δευτερόλεπτα έχει μια ομάδα για να ολοκληρώσει την επίθεσή της;", "opts": ["14", "20", "24", "30"], "ans": "C", "diff": "Μέτριο"},
    {"q": "Ποιος είναι ο πρώτος σκόρερ όλων των εποχών στην ιστορία του NBA;", "opts": ["Michael Jordan", "Kobe Bryant", "LeBron James", "Kareem Abdul-Jabbar"], "ans": "C", "diff": "Μέτριο"},
    {"q": "Ποια ελληνική ομάδα έχει τα περισσότερα τρόπαια EuroLeague;", "opts": ["Ολυμπιακός", "Παναθηναϊκός", "ΑΕΚ", "ΠΑΟΚ"], "ans": "B", "diff": "Μέτριο"},
    {"q": "Πόσα φάουλ χρειάζεται ένας παίκτης για να αποβληθεί (FIBA/EuroLeague);", "opts": ["4", "5", "6", "7"], "ans": "B", "diff": "Μέτριο"},
    {"q": "Ποιος θρυλικός Έλληνας παίκτης είχε το παρατσούκλι «Γκάγκστερ»;", "opts": ["Παναγιώτης Γιαννάκης", "Νίκος Γκάλης", "Φάνης Χριστοδούλου", "Δημήτρης Διαμαντίδης"], "ans": "B", "diff": "Μέτριο"},
    {"q": "Πόσα λεπτά διαρκεί μια παράταση στο μπάσκετ;", "opts": ["3", "5", "8", "10"], "ans": "B", "diff": "Μέτριο"},
    {"q": "Σε ποια πόλη βρίσκεται η έδρα της Ζαλγκίρις;", "opts": ["Βίλνιους", "Κάουνας", "Ρίγα", "Ταλίν"], "ans": "B", "diff": "Μέτριο"},
    {"q": "Ποιος έβαλε 100 πόντους σε έναν μόνο αγώνα NBA (ρεκόρ όλων των εποχών);", "opts": ["Wilt Chamberlain", "Kobe Bryant", "Michael Jordan", "James Harden"], "ans": "A", "diff": "Μέτριο"},
    {"q": "Σε ποια πόλη κατέκτησε η Εθνική Ελλάδος το πρώτο της Ευρωμπάσκετ, το 1987;", "opts": ["Αθήνα", "Θεσσαλονίκη", "Μαδρίτη", "Ρώμη"], "ans": "A", "diff": "Μέτριο"},
    {"q": "Σε ποια εθνική ομάδα αγωνίζεται ο Λούκα Ντόντσιτς;", "opts": ["Κροατία", "Σλοβενία", "Σερβία", "Ελλάδα"], "ans": "B", "diff": "Μέτριο"},
    {"q": "Πόσους πόντους αξίζει ένα σουτ πίσω από τη γραμμή των τριών πόντων;", "opts": ["1", "2", "3", "4"], "ans": "C", "diff": "Μέτριο"},
    {"q": "Το 2005 η Εθνική Ελλάδος κέρδισε ξανά το Ευρωμπάσκετ. Ποια νίκησε στον τελικό;", "opts": ["Γερμανία", "Γαλλία", "Ισπανία", "Λιθουανία"], "ans": "A", "diff": "Μέτριο"},

    # --- ΔΥΣΚΟΛΑ ---
    {"q": "Ποια ομάδα έχει κατακτήσει τα περισσότερα πρωταθλήματα στην ιστορία του NBA;", "opts": ["LA Lakers", "Boston Celtics", "Chicago Bulls", "Golden State"], "ans": "B", "diff": "Δύσκολο"},
    {"q": "Πόσα δευτερόλεπτα μπορεί να μείνει ένας επιθετικός μέσα στη ρακέτα;", "opts": ["3", "5", "8", "24"], "ans": "A", "diff": "Δύσκολο"},
    {"q": "Ποιο είναι το ύψος της στεφάνης από το έδαφος;", "opts": ["2.95 μ.", "3.05 μ.", "3.15 μ.", "3.25 μ."], "ans": "B", "diff": "Δύσκολο"},
    {"q": "Πόσα δευτερόλεπτα έχει μια ομάδα για να περάσει τη μπάλα στο μπροστινό γήπεδο;", "opts": ["5", "8", "10", "14"], "ans": "B", "diff": "Δύσκολο"},
    {"q": "Ποιος παίκτης φημίζεται για το σουτ του από τεράστια απόσταση;", "opts": ["Stephen Curry", "Klay Thompson", "Kevin Durant", "Kyrie Irving"], "ans": "A", "diff": "Δύσκολο"},
    {"q": "Ποιος Σέρβος σέντερ των Ντένβερ έχει κερδίσει πολλαπλά βραβεία MVP;", "opts": ["Nikola Jokic", "Bogdan Bogdanovic", "Luka Doncic", "Vlade Divac"], "ans": "A", "diff": "Δύσκολο"},
    {"q": "Ποιος προπονητής έχει κατακτήσει τις περισσότερες EuroLeague;", "opts": ["Zeljko Obradovic", "Ettore Messina", "Ergin Ataman", "Pablo Laso"], "ans": "A", "diff": "Δύσκολο"},
    {"q": "Ποια είναι η διάμετρος της στεφάνης (μπασκέτας);", "opts": ["40 εκ.", "45 εκ.", "50 εκ.", "55 εκ."], "ans": "B", "diff": "Δύσκολο"},
    {"q": "Ποιες είναι οι διαστάσεις ενός επίσημου γηπέδου FIBA;", "opts": ["26x14 μ.", "28x15 μ.", "30x16 μ.", "25x13 μ."], "ans": "B", "diff": "Δύσκολο"},
    {"q": "Σε ποια απόσταση βρίσκεται η γραμμή των τριών πόντων στη FIBA;", "opts": ["6.25 μ.", "6.75 μ.", "7.24 μ.", "5.80 μ."], "ans": "B", "diff": "Δύσκολο"},
    {"q": "Ποιος Έλληνας γκαρντ είχε το παρατσούκλι «Kill Bill»;", "opts": ["Βασίλης Σπανούλης", "Νικ Καλάθης", "Κώστας Σλούκας", "Γιάννης Μπουρούσης"], "ans": "A", "diff": "Δύσκολο"},
]

TROLL_Q = {
    "q": "Ποια είναι η καλύτερη ελληνική ομάδα; 🤔",
    "opts": ["Ολυμπιακός", "Παναθηναϊκός", "ΠΑΟΚ", "ΑΕΚ"],
    "ans": "C", "diff": "Μυστικό", "troll": True,
}

TEAMS = ["Ολυμπιακός", "Παναθηναϊκός", "ΑΕΚ", "ΠΑΟΚ", "Άρης", "Ηρακλής",
         "Φενέρμπαχτσε", "Εφές", "Ρεάλ Μαδρίτης", "Μπαρτσελόνα", "Μονακό", "Άλλη / Καμία"]

# Λίστα ονομάτων για το dropdown. Το τελευταίο ("Άλλο…") εμφανίζει πεδίο
# ώστε να μπει όνομα που ΔΕΝ υπάρχει στη λίστα.
NAME_OTHER = "✏️ Άλλο (γράψε νέο)…"
names_list = [
    "Γιάννης Π",
    "Φώτης Π",
    "Γιώργος Π",
    "Κυριάκος Α",
    "Δημήτρης Κ",
    "Χρήστος Κ",
    "Σταύρος Δ",
    "Γιάννης Λ",
    "Γιώργος Κ",
    "Ιωάννης Χ",
    "Λάζαρος Τ",
    "Νικολέτα Δ",
    "Μαρκέλλα Α",
    "Μαριαλένα Φ",
    "Κωνσταντίνος Π",
]

# ------------------- SIDEBAR -------------------
st.sidebar.title("🏀 Info")
st.sidebar.info("Ένα διασκεδαστικό κουίζ μπάσκετ για την παρέα!")
st.sidebar.checkbox("🔊 Ήχοι", value=True, key="sound_on")
st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 **Δημιουργός:**")
st.sidebar.markdown("### Γιάννης Παπαδόπουλος")

# ------------------- ΛΙΓΟ ΧΡΩΜΑ (CSS) -------------------
st.markdown("""
<style>
.stApp { background: radial-gradient(1000px 500px at 50% -10%, #1d3553 0%, transparent 60%), linear-gradient(180deg,#0E1A2B,#0A1422); }
div[data-testid="stMetric"] { background:#0b1726; border:1px solid #243f5d; border-radius:14px; padding:10px; }
/* Κρύβει το player του ήχου — ο ήχος παίζει αυτόματα στο παρασκήνιο */
div[data-testid="stAudio"] { height:0 !important; min-height:0 !important; margin:0 !important; padding:0 !important; overflow:hidden !important; }
.stApp audio { height:0; }
</style>
""", unsafe_allow_html=True)

# ------------------- ΑΡΧΙΚΟΠΟΙΗΣΗ STATE -------------------
def ss_default(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

ss_default("page", "login")
ss_default("leaderboard", [])
ss_default("name", "")
ss_default("team", "")
ss_default("player", "")
ss_default("diff", "Τυχαίες (Mix)")

# ------------------- ΉΧΟΣ -------------------
# Φτιάχνουμε τους ήχους ως πραγματικά αρχεία WAV και τους παίζουμε με
# st.audio(autoplay=True). Έτσι παίζουν στην ΚΥΡΙΑ σελίδα (εκεί που έγινε
# το κλικ του χρήστη) και ΟΧΙ μέσα σε sandboxed iframe — που τους μπλόκαρε.
@st.cache_data(show_spinner=False)
def _tone_wav(freqs, dur=0.16, sr=22050, vol=0.35, shape="sine"):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)   # 16-bit
        w.setframerate(sr)
        frames = bytearray()
        attack = int(0.012 * sr)  # μικρό fade in/out για να μην "κλικάρει"
        for f in freqs:
            n = int(sr * dur)
            for i in range(n):
                if i < attack:
                    env = i / attack
                elif i > n - attack:
                    env = max(0.0, (n - i) / attack)
                else:
                    env = 1.0
                v = math.sin(2 * math.pi * f * i / sr)
                if shape == "square":   # πιο "βραχνός" ήχος, ακούγεται καλά
                    v = 1.0 if v >= 0 else -1.0  # και σε μικρά ηχεία laptop/κινητού
                s = vol * env * v
                frames += struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767))
        w.writeframes(bytes(frames))
    return buf.getvalue()

SOUND_SPECS = {
    "correct": {"freqs": (660, 880, 1180),      "dur": 0.16, "vol": 0.35, "shape": "sine"},
    "wrong":   {"freqs": (440, 330, 247),       "dur": 0.16, "vol": 0.32, "shape": "square"},
    "timeout": {"freqs": (392, 311, 233, 175),  "dur": 0.22, "vol": 0.34, "shape": "square"},
    "win":     {"freqs": (523, 659, 784, 1046), "dur": 0.18, "vol": 0.35, "shape": "sine"},
    "tick":    {"freqs": (1568,),               "dur": 0.06, "vol": 0.25, "shape": "square"},
}

def play_sound(kind):
    if not st.session_state.get("sound_on", True):
        return
    spec = SOUND_SPECS.get(kind)
    if not spec:
        return
    st.audio(_tone_wav(spec["freqs"], dur=spec["dur"], vol=spec["vol"],
                       shape=spec.get("shape", "sine")),
             format="audio/wav", autoplay=True)

def rerun_app():
    try:
        st.rerun(scope="app")
    except TypeError:
        st.rerun()

# ------------------- ΛΟΓΙΚΗ ΠΑΙΧΝΙΔΙΟΥ -------------------
def init_game(name, team, player, diff, timer_on=True):
    s = st.session_state
    s.name, s.team, s.player, s.diff = name, team, player, diff
    s.timer_on = timer_on

    pool = [dict(q) for q in ALL_QUESTIONS if diff == "Τυχαίες (Mix)" or q["diff"] == diff]
    random.shuffle(pool)
    pool = pool[:MAX_QUESTIONS]
    if random.random() < TROLL_CHANCE and len(pool) > 1:
        idx = random.randint(1, len(pool) - 1)
        pool.insert(idx, dict(TROLL_Q))

    s.queue = pool
    s.total = len(pool)
    s.done = 0
    s.score = 0
    s.mistakes = 0
    s.streak = 0
    s.best_streak = 0
    s.err_streak = 0
    s.lives = START_LIVES
    s.used_5050 = False
    s.used_skip = False
    s.used_any_lifeline = False
    s.cur = None
    s.q_serial = 0
    s.removed_opts = []
    s.answered = False
    s.feedback = None
    s.emoji = ""
    s.celebrate = None
    s.snd = None
    s.time_left = TIME_LIMIT
    s.q_start = time.time()
    s.page = "quiz"

def load_next():
    s = st.session_state
    if s.lives <= 0 or len(s.queue) == 0:
        finish_game()
        return
    s.cur = s.queue.pop(0)
    s.answered = False
    s.removed_opts = []
    s.feedback = None
    s.emoji = ""
    s.celebrate = None
    s.snd = None
    s.q_serial += 1
    s.time_left = TIME_LIMIT
    s._last_tick = None
    s.q_start = time.time()

def register_correct():
    s = st.session_state
    s.done += 1
    s.streak += 1
    s.err_streak = 0
    s.best_streak = max(s.best_streak, s.streak)
    base = 2 if s.cur.get("troll") else DIFF_BASE.get(s.cur["diff"], 1)
    time_bonus = (s.time_left // 3) if s.get("timer_on", True) else 0
    streak_bonus = 2 if s.streak >= 3 else 0
    gained = base + time_bonus + streak_bonus
    s.score += gained
    s.snd = "correct"

    if s.cur.get("troll"):
        s.feedback = ("ok", f"🦅 ΜΠΑΜ! Έτσι μπράβο {s.name}! (+{gained} πόντοι)")
        s.emoji, s.celebrate = "🦅", "balloons"
    elif s.streak >= 3:
        s.feedback = ("ok", f"✅ ΣΩΣΤΟ! 🔥 Είσαι ON FIRE — {s.streak} στη σειρά! (+{gained} πόντοι)")
        s.emoji, s.celebrate = "🔥", "balloons"
    else:
        cheer = random.choice(["Εξαιρετικό σουτ!", "Καθαρό καλάθι! 🏀", "Μπράβο, swish!", "Το βρήκες!"])
        s.feedback = ("ok", f"✅ ΣΩΣΤΟ! {cheer} (+{gained} πόντοι)")
        s.emoji, s.celebrate = "🏀", None

def register_wrong(by_time=False):
    s = st.session_state
    s.mistakes += 1
    s.err_streak += 1
    s.streak = 0
    s.lives -= 1
    s.snd = "timeout" if by_time else "wrong"
    s.celebrate = None
    correct_txt = s.cur["opts"][LETTERS.index(s.cur["ans"])]

    if s.cur.get("troll"):
        s.feedback = ("bad", f"❌ Ε όχι! Η σωστή (για το παιχνίδι μας 😉) ήταν: **{correct_txt}**. Μόνο {FAVORED_TEAM}! 🦅")
        s.emoji = "😅"
    else:
        pl = f"Ούτε ο/η {s.player} δεν θα την έχανε αυτή! " if s.player != "Κανένας" else "Σχεδόν! "
        lead = "⏰ Σε πρόλαβε το χρονόμετρο! " if by_time else "❌ Όχι αυτή. "
        fire = "Πάρε ανάσα και ξαναμπές δυνατά! " if s.err_streak >= 3 else ""
        extra = "" if s.lives > 0 else " Τέλειωσαν οι ζωές σου!"
        s.feedback = ("bad", f"{lead}{fire}{pl}Σωστή απάντηση: **{correct_txt}**.{extra}")
        s.emoji = "😅" if s.lives > 0 else "🛑"

    if s.lives > 0 and not s.cur.get("troll"):
        rq = dict(s.cur)
        rq["repeat"] = True
        s.queue.append(rq)

def finish_game():
    s = st.session_state
    save_score({
        "Όνομα": s.name, "Ομάδα": s.team, "Αγ. Παίκτης": s.player,
        "Σκορ": s.score, "Λάθη": s.mistakes,
    })
    s.page = "over"

# ------------------- ΖΩΝΤΑΝΟ ΧΡΟΝΟΜΕΤΡΟ -------------------
def _shot_clock_body():
    s = st.session_state
    if s.get("answered"):
        rem = s.get("time_left", 0)
        st.progress(rem / TIME_LIMIT if TIME_LIMIT else 0, text=f"⏱️ Χρόνος: {rem}s")
        return
    elapsed = time.time() - s.q_start
    rem = max(0, TIME_LIMIT - int(elapsed))
    icon = "⏱️" if rem > 5 else "⚠️"
    st.progress(rem / TIME_LIMIT, text=f"{icon} Χρόνος επίθεσης: {rem}s")
    if rem <= 0:
        s.time_left = 0
        s.answered = True
        register_wrong(by_time=True)
        rerun_app()
        return
    # Τικ αντίστροφης μέτρησης στα τελευταία 5 δευτερόλεπτα (μία φορά ανά δευτ.)
    if 1 <= rem <= 5 and s.get("_last_tick") != rem:
        s._last_tick = rem
        play_sound("tick")

if hasattr(st, "fragment"):
    try:
        shot_clock = st.fragment(run_every=1)(_shot_clock_body)
    except TypeError:
        shot_clock = _shot_clock_body
else:
    shot_clock = _shot_clock_body

# ------------------- ΚΟΙΝΟ LEADERBOARD (GOOGLE SHEETS) -------------------
# Στήλες του φύλλου:
SHEET_HEADERS = ["Χρόνος", "Όνομα", "Ομάδα", "Αγ. Παίκτης", "Σκορ", "Λάθη"]

@st.cache_resource(show_spinner=False)
def _get_sheet():
    """Επιστρέφει το worksheet ή None (τότε γίνεται fallback σε τοπικό leaderboard)."""
    if not _HAS_GSPREAD:
        return None
    try:
        creds = dict(st.secrets["gcp_service_account"])
        # Δέχεται το private_key είτε με πραγματικές αλλαγές γραμμής
        # είτε με literal \n — διορθώνει το πιο συχνό λάθος ρυθμίσεων.
        if "private_key" in creds and "\\n" in creds["private_key"]:
            creds["private_key"] = creds["private_key"].replace("\\n", "\n")
        key = st.secrets["leaderboard"]["sheet_key"]
        gc = gspread.service_account_from_dict(creds)
        ws = gc.open_by_key(key).sheet1
        if ws.row_values(1) != SHEET_HEADERS:   # βάζει επικεφαλίδες αν λείπουν
            if not ws.row_values(1):
                ws.append_row(SHEET_HEADERS)
        return ws
    except Exception:
        return None

def diagnose_sheet():
    """Επιστρέφει (ok: bool, μήνυμα) για έλεγχο σύνδεσης με το Google Sheet."""
    if not _HAS_GSPREAD:
        return False, "Το gspread δεν είναι εγκατεστημένο. Πρόσθεσέ το στο requirements.txt."
    try:
        creds = dict(st.secrets["gcp_service_account"])
    except Exception:
        return False, "Λείπει η ενότητα [gcp_service_account] από τα Secrets."
    try:
        key = st.secrets["leaderboard"]["sheet_key"]
    except Exception:
        return False, "Λείπει το [leaderboard] sheet_key από τα Secrets."
    if key in ("", "THE_LONG_ID_FROM_STEP_1", "THE_LONG_ID_FROM_YOUR_SHEET_URL"):
        return False, f"Το sheet_key είναι ακόμα placeholder ('{key}'). Βάλε το πραγματικό ID του φύλλου."
    if "private_key" in creds and "\\n" in creds["private_key"]:
        creds["private_key"] = creds["private_key"].replace("\\n", "\n")
    try:
        gc = gspread.service_account_from_dict(creds)
    except Exception as e:
        return False, f"Πρόβλημα με τα credentials: {type(e).__name__}: {e}"
    try:
        sh = gc.open_by_key(key)
    except Exception as e:
        return False, (f"Δεν άνοιξε το φύλλο. {type(e).__name__}. "
                       f"Έλεγξε ότι το sheet_key είναι σωστό ΚΑΙ ότι μοιράστηκες "
                       f"το φύλλο με το client_email ως Editor: {creds.get('client_email','?')}")
    return True, f"OK — συνδέθηκε στο φύλλο «{sh.title}»."

@st.cache_data(ttl=20, show_spinner=False)
def _fetch_rows():
    """Διαβάζει τις εγγραφές από το Sheet. None => δεν υπάρχει σύνδεση."""
    ws = _get_sheet()
    if ws is None:
        return None
    try:
        return ws.get_all_records()
    except Exception:
        return None

def save_score(entry):
    ws = _get_sheet()
    if ws is None:
        st.session_state.leaderboard.append(entry)   # fallback: τοπικά
        return
    try:
        ws.append_row(
            [datetime.now().strftime("%Y-%m-%d %H:%M"),
             entry["Όνομα"], entry["Ομάδα"], entry["Αγ. Παίκτης"],
             int(entry["Σκορ"]), int(entry["Λάθη"])],
            value_input_option="USER_ENTERED",
        )
        _fetch_rows.clear()   # ακυρώνει την cache ώστε να φανεί η νέα εγγραφή
    except Exception:
        st.session_state.leaderboard.append(entry)

def leaderboard_is_shared():
    return _get_sheet() is not None

def render_leaderboard():
    rows = _fetch_rows()
    if rows is None:                       # χωρίς σύνδεση -> τοπικό
        rows = st.session_state.leaderboard
    if not rows:
        st.caption("Κανένα σκορ ακόμα — γίνε εσύ ο πρώτος! 🏀")
        return
    df = pd.DataFrame(rows)
    for col in ("Σκορ", "Λάθη"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Ομαδοποίηση: κάθε παίκτης εμφανίζεται μία φορά
    group_keys = [k for k in LEADERBOARD_GROUP if k in df.columns]
    if group_keys and "Σκορ" in df.columns:
        if LEADERBOARD_MODE == "total":
            agg = {"Σκορ": "sum"}
            if "Λάθη" in df.columns:
                agg["Λάθη"] = "sum"
            sums = df.groupby(group_keys, as_index=False).agg(agg)
            # Κράτα ενδεικτική Ομάδα/Αγ. Παίκτη από την καλύτερη παρτίδα του παίκτη
            extra = [c for c in ("Ομάδα", "Αγ. Παίκτης")
                     if c in df.columns and c not in group_keys]
            if extra:
                sb = ["Σκορ"] + (["Λάθη"] if "Λάθη" in df.columns else [])
                sa = [False] + ([True] if "Λάθη" in df.columns else [])
                rep = (df.sort_values(by=sb, ascending=sa)
                         .drop_duplicates(subset=group_keys, keep="first")[group_keys + extra])
                sums = sums.merge(rep, on=group_keys, how="left")
            df = sums
        else:  # "best": η καλύτερη παρτίδα κάθε παίκτη
            sort_by = ["Σκορ"] + (["Λάθη"] if "Λάθη" in df.columns else [])
            sort_asc = [False] + ([True] if "Λάθη" in df.columns else [])
            df = (df.sort_values(by=sort_by, ascending=sort_asc)
                    .drop_duplicates(subset=group_keys, keep="first"))

    if "Σκορ" in df.columns:
        by = ["Σκορ"] + (["Λάθη"] if "Λάθη" in df.columns else [])
        asc = [False] + ([True] if "Λάθη" in df.columns else [])
        df = df.sort_values(by=by, ascending=asc)
    cols = [c for c in ["Όνομα", "Ομάδα", "Αγ. Παίκτης", "Σκορ", "Λάθη"] if c in df.columns]
    df = df[cols].head(20).reset_index(drop=True)
    df.index = df.index + 1
    st.dataframe(df, use_container_width=True)

# Δείκτης κατάστασης στο sidebar (κοινό vs τοπικό leaderboard)
if leaderboard_is_shared():
    st.sidebar.success("🌐 Κοινό leaderboard ενεργό")
else:
    st.sidebar.caption("📋 Τοπικό leaderboard (δες οδηγίες για Google Sheets)")

# ============================================================
#  ΣΕΛΙΔΑ 1: LOGIN
# ============================================================
if st.session_state.page == "login":
    st.title("🏀 Καλώς ήρθες στο παρκέ!")
    st.markdown("Φτιάξε το προφίλ σου, διάλεξε δυσκολία και δείξε μας τι ξέρεις από μπάσκετ.")

    with st.form("login_form"):
        picked = st.selectbox("Το όνομά σου / Nickname:", names_list + [NAME_OTHER],
                              index=None, placeholder="Διάλεξε όνομα από τη λίστα…")
        custom_name = st.text_input("…ή γράψε νέο όνομα (αν δεν είσαι στη λίστα):")
        team = st.selectbox("Η αγαπημένη σου ομάδα:", TEAMS,
                            index=None, placeholder="Διάλεξε ομάδα…")
        player = st.text_input("Ο αγαπημένος σου παίκτης:")
        diff = st.radio("Επίπεδο δυσκολίας:",
                        ["Εύκολο", "Μέτριο", "Δύσκολο", "Τυχαίες (Mix)"],
                        index=3, horizontal=True)
        timer_on = st.toggle("⏱️ Χρονόμετρο (αντίστροφη μέτρηση & πόντοι ταχύτητας)", value=True)
        submitted = st.form_submit_button("🚀 Έναρξη παιχνιδιού!", type="primary", use_container_width=True)
        if submitted:
            # Αν γραφτεί νέο όνομα, αυτό υπερισχύει. Αλλιώς παίρνουμε τη λίστα.
            if custom_name.strip():
                name = custom_name.strip()
            elif picked and picked != NAME_OTHER:
                name = picked
            else:
                name = ""
            if not name:
                st.error("✋ Διάλεξε ένα όνομα από τη λίστα ή γράψε ένα νέο!")
            else:
                init_game(name, team or "Άλλη / Καμία", player.strip() or "Κανένας", diff, timer_on)
                st.rerun()

    st.markdown("---")
    st.subheader("🏆 Leaderboard (σημερινά αποτελέσματα)")
    render_leaderboard()
    st.markdown("<br><center><i>Ανάπτυξη & Σχεδιασμός: Γιάννης Παπαδόπουλος © 2026</i></center>", unsafe_allow_html=True)

# ============================================================
#  ΣΕΛΙΔΑ 2: ΚΟΥΙΖ
# ============================================================
elif st.session_state.page == "quiz":
    s = st.session_state
    st.title(f"🏀 {s.name} | 🛡️ {s.team} | ⭐ {s.player}")

    if s.cur is None:
        load_next()

    # --- σκορ-μπόρντ ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Σκορ", s.score)
    c2.metric("🔥 Σερί", s.streak)
    c3.metric("Ζωές", "❤️" * s.lives + "🤍" * max(0, START_LIVES - s.lives))

    # --- πρόοδος ---
    prog = s.done / s.total if s.total else 0
    st.progress(prog, text=f"Έχεις βρει {s.done} από {s.total} ερωτήσεις")

    # --- χρονόμετρο (μόνο αν είναι ενεργό) ---
    if s.get("timer_on", True):
        shot_clock()

    st.markdown("---")
    cur = s.cur

    badge = "" if cur.get("troll") else f"`{cur['diff']}` "
    repeat = "🔄 (Επανάληψη) " if cur.get("repeat") else ""
    st.subheader(f"❓ {badge}{repeat}{cur['q']}")

    # --- επιλογές (φιλτράρισμα για το 50:50) ---
    visible = [(LETTERS[i], opt) for i, opt in enumerate(cur["opts"]) if LETTERS[i] not in s.removed_opts]
    labels = [f"{ltr}) {txt}" for ltr, txt in visible]
    choice = st.radio("Επίλεξε την απάντησή σου:", labels, index=None,
                      key=f"radio_{s.q_serial}", disabled=s.answered)

    # --- βοήθειες (όχι στην παγίδα) ---
    if not cur.get("troll"):
        lc1, lc2 = st.columns(2)
        if lc1.button("✂️ 50:50", disabled=s.used_5050 or s.answered, use_container_width=True):
            s.used_5050 = True
            s.used_any_lifeline = True
            wrong_letters = [l for l in LETTERS if l != cur["ans"]]
            s.removed_opts = random.sample(wrong_letters, 2)
            st.rerun()
        if lc2.button("⏭️ Προσπέραση", disabled=s.used_skip or s.answered, use_container_width=True):
            s.used_skip = True
            s.used_any_lifeline = True
            rq = dict(cur)
            rq["repeat"] = True
            s.queue.append(rq)
            load_next()
            st.rerun()

    # --- υποβολή ---
    if st.button("🎯 Υποβολή απάντησης", type="primary", use_container_width=True, disabled=s.answered):
        if choice is None:
            st.warning("⚠️ Διάλεξε πρώτα μια απάντηση!")
        else:
            s.answered = True
            chosen_letter = choice[0]
            if s.get("timer_on", True):
                elapsed = time.time() - s.q_start
                s.time_left = max(0, TIME_LIMIT - int(elapsed))
            else:
                s.time_left = 0  # χωρίς χρονόμετρο δεν υπάρχει μπόνους ταχύτητας
            if s.get("timer_on", True) and s.time_left <= 0:
                register_wrong(by_time=True)
            elif chosen_letter == cur["ans"]:
                register_correct()
            else:
                register_wrong(by_time=False)
            st.rerun()

    # --- feedback ---
    if s.feedback:
        status, msg = s.feedback
        st.markdown(f"<div style='font-size:54px;text-align:center'>{s.emoji}</div>", unsafe_allow_html=True)
        (st.success if status == "ok" else st.error)(msg)
        if s.snd:
            play_sound(s.snd)
            s.snd = None  # να μην ξαναπαίξει
        if s.celebrate == "balloons":
            st.balloons()
            s.celebrate = None

        last = (len(s.queue) == 0) or (s.lives <= 0)
        btn_text = "🏆 Δες τα αποτελέσματα!" if last else "➡️ Επόμενη ερώτηση"
        if st.button(btn_text, type="primary", use_container_width=True):
            load_next()
            st.rerun()

# ============================================================
#  ΣΕΛΙΔΑ 3: ΑΠΟΤΕΛΕΣΜΑΤΑ
# ============================================================
elif st.session_state.page == "over":
    s = st.session_state
    answered = s.done + s.mistakes
    acc = round(s.done / answered * 100) if answered else 0

    if s.lives <= 0:
        st.title("🛑 Τέλος αγώνα!")
    elif acc >= 80:
        st.title("🏆 ΝΙΚΗΣΕΣ!")
    elif acc >= 50:
        st.title("👏 Καλό παιχνίδι!")
    else:
        st.title("🏀 Τέλος αγώνα!")

    st.markdown(f"Μπράβο **{s.name}**! Το σκορ σου μπήκε στο leaderboard.")
    st.markdown("---")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("✅ Σκορ", s.score)
    r2.metric("❌ Λάθη", s.mistakes)
    r3.metric("🔥 Καλύτερο σερί", s.best_streak)
    r4.metric("⚡ Ακρίβεια", f"{acc}%")

    st.markdown("### Αξιολόγηση εμφάνισης:")
    if s.lives <= 0:
        st.error("🛑 Έμεινες από ζωές! Καλή προσπάθεια — η ρεβάνς σε περιμένει.")
    elif acc >= 80:
        st.success(f"🔥 Είσαι MVP! Ο/η {s.player} θα ήταν περήφανος!")
        play_sound("win")
        st.balloons()
    elif acc >= 50:
        st.info("🏀 Τίμια εμφάνιση! Έχεις ταλέντο — λίγη ακόμα προπόνηση και πατάς κορυφή.")
    else:
        st.error("💪 Κάθε πρωταθλητής ξεκίνησε από κάπου. Ξαναπροσπάθησε — θα τα σπάσεις!")

    # --- παράσημα (badges) ---
    ach = []
    if s.best_streak >= 5:
        ach.append("🔥 Hot Streak ×5")
    elif s.best_streak >= 3:
        ach.append("🔥 Hot Streak")
    if s.mistakes == 0 and s.lives > 0:
        ach.append("💎 Τέλειο παιχνίδι")
    if not s.used_any_lifeline:
        ach.append("🧠 Χωρίς βοήθειες")
    if acc >= 80:
        ach.append("🎯 Σκοπευτής")
    if s.score >= 30:
        ach.append("⭐ 30+ πόντοι")
    if ach:
        st.markdown("### 🏅 Παράσημα")
        st.markdown("  ".join(f"`{a}`" for a in ach))

    st.markdown("---")
    b1, b2 = st.columns(2)
    if b1.button("🔁 Παίξε ξανά", type="primary", use_container_width=True):
        init_game(s.name, s.team, s.player, s.diff, s.get("timer_on", True))
        st.rerun()
    if b2.button("🏠 Αρχικό μενού", use_container_width=True):
        s.page = "login"
        st.rerun()

    st.markdown("---")
    st.subheader("🏆 Leaderboard")
    render_leaderboard()
    st.markdown("<br><center><i>Ανάπτυξη & Σχεδιασμός: Γιάννης Παπαδόπουλος © 2026</i></center>", unsafe_allow_html=True)
