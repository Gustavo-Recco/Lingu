"""
Arquivo: Lingu.py

Lingu — Assistente Virtual de Estudos de Idiomas
Autor: Gustavo Fernandes Recco
Copyright (c) 2026 Gustavo Fernandes Recco
Bibliotecas: Matplotlib + NumPy + pyttsx3 + winsound
"""
import matplotlib
matplotlib.use("TkAgg")
matplotlib.rcParams["toolbar"] = "None"
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Button, TextBox
import numpy as np
import random, threading, json, os, queue

# Fila para comunicação thread → UI principal
_UI_QUEUE: queue.Queue = queue.Queue()

import urllib.request, urllib.parse

# Traduz via Google Translate grátis. Retorna string ou None.

def _gt_translate(text, src, tgt):

    try:
        q   = urllib.parse.quote(text)
        url = (f"https://translate.googleapis.com/translate_a/single"
               f"?client=gtx&sl={src}&tl={tgt}&dt=t&q={q}")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=6).read().decode("utf-8")
        data = json.loads(raw)
        return "".join(part[0] for part in data[0] if part[0])
    except Exception:
        return None

def _gt_exemplo(word, src):
    
# Busca frase de exemplo via Google Translate (dt=ex).
    
    import re

    for dt in ("ex", "e"):
        try:
            q   = urllib.parse.quote(word)
            url = (f"https://translate.googleapis.com/translate_a/single"
                   f"?client=gtx&sl={src}&tl=pt&dt=t&dt={dt}&q={q}")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            raw = urllib.request.urlopen(req, timeout=6).read().decode("utf-8")
            data = json.loads(raw)
            
            if len(data) > 3 and data[3]:
                bloco = data[3]
                
                for item in bloco:
                    if isinstance(item, list):
                        for sub in item:
                            if isinstance(sub, list) and sub and isinstance(sub[0], str):
                                frase = re.sub(r"<[^>]+>", "", sub[0]).strip()
                                if len(frase) > 5:
                                    return frase
        except Exception:
            pass
    return None

# Audio ══════════════════════════════════════════════
try:
    import pyttsx3
    TTS_OK = True
except:
    TTS_OK = False

try:
    import winsound
    WINSOUND_OK = True
except:
    WINSOUND_OK = False

_tts_lock  = threading.Lock()
_tts_stop  = threading.Event()   # Vaai sinalizar para a thread atual parar

def falar(texto, lang="en"):
    if not TTS_OK: return
# Cancela qualquer fala em andamento
    _tts_stop.set()
    def _run():

        acquired = _tts_lock.acquire(timeout=0.4)
        _tts_stop.clear()
        if not acquired:
            return
        try:
            e = pyttsx3.init()
            e.setProperty("rate", 145)
            for v in e.getProperty("voices"):
                vid = (v.id + v.name).lower()
                if lang == "es" and ("spanish" in vid or "es_" in vid):
                    e.setProperty("voice", v.id); break
                elif lang == "en" and ("english" in vid or "en_" in vid):
                    e.setProperty("voice", v.id); break
            if not _tts_stop.is_set():
                e.say(texto)
                e.runAndWait()
        except: pass
        finally:
            _tts_lock.release()
    threading.Thread(target=_run, daemon=True).start()

def som_acerto():
    if WINSOUND_OK: threading.Thread(target=lambda:[winsound.Beep(880,120),winsound.Beep(1100,150)],daemon=True).start()

def som_erro():
    if WINSOUND_OK: threading.Thread(target=lambda:[winsound.Beep(300,200),winsound.Beep(250,250)],daemon=True).start()

def som_nav():
    if WINSOUND_OK: threading.Thread(target=lambda:winsound.Beep(600,60),daemon=True).start()

# Base de dados ══════════════════════════════════════════════
IDIOMAS = {
    "en": {
        "nome": "Inglês", "bandeira": "[EN]", "lang_code": "en",
        "vocabulario": [
            {"orig": "Multimedia", "pt": "Multimídia", "nivel": "Médio",   "frase": "Multimedia combines text, audio and images.",  "frase_pt": "Multimídia combina texto, áudio e imagens."},
            {"orig": "Compression","pt": "Compressão", "nivel": "Avançado","frase": "Video compression reduces file size.","frase_pt": "A compressao de video reduz o tamanho do arquivo."},
            {"orig": "Resolution", "pt": "Resolução",  "nivel": "Médio",   "frase": "Higher resolution means better image quality.","frase_pt": "Maior resolução significa melhor qualidade de imagem."},
        ],
        "frases": [
            {"frase": "The ___ encodes video into a smaller format.",  "resposta": "codec",      "opcoes": ["codec","player","screen","buffer"]},
            {"frase": "A higher ___ produces sharper images.",         "resposta": "resolution", "opcoes": ["resolution","volume","codec","frame"]},
            {"frase": "Audio and video must be ___ in a stream.",      "resposta": "synced",     "opcoes": ["synced","deleted","paused","encoded"]},
            {"frase": "JPEG is a ___ format for images.",              "resposta": "compressed", "opcoes": ["compressed","raw","animated","streamed"]},
            {"frase": "The ___ rate affects how smooth a video looks.","resposta": "frame",      "opcoes": ["frame","sample","bit","pixel"]},
        ],
        "correto_voz":  "Correct!",  "erro_voz": "Wrong. The answer is ",
    },
    "es": {
        "nome": "Espanhol", "bandeira": "[ES]", "lang_code": "es",
        "vocabulario": [
            {"orig": "Multimedia", "pt": "MultimÍdia", "nivel": "Médio",   "frase": "La multimedia combina texto, audio e imagenes.", "frase_pt": "A multimídia combina texto, áudio e imagens."},
            {"orig": "Compresion", "pt": "Compressão", "nivel": "Avançado","frase": "La compresion de video reduce el tamano del archivo.", "frase_pt": "A compressão de video reduz o tamanho do arquivo."},
            {"orig": "Resolucion", "pt": "Resolução",  "nivel": "Médio",   "frase": "Mayor resolucion significa mejor calidad de imagen.", "frase_pt": "Maior resolução significa melhor qualidade de imagem."},
        ],
        "frases": [
            {"frase": "El ___ convierte el video a un formato menor.",  "resposta": "codec",       "opcoes": ["codec","buffer","canal","pixel"]},
            {"frase": "Una mayor ___ produce imagenes mas nitidas.",    "resposta": "resolucion",  "opcoes": ["resolucion","muestra","volumen","cuadro"]},
            {"frase": "El audio y el video deben estar ___ en el flujo.","resposta": "sincronizados","opcoes": ["sincronizados","borrados","pausados","codificados"]},
            {"frase": "JPEG es un formato de imagen ___.",              "resposta": "comprimido",  "opcoes": ["comprimido","crudo","animado","transmitido"]},
            {"frase": "La tasa de ___ afecta la fluidez del video.",   "resposta": "cuadros",     "opcoes": ["cuadros","muestra","bits","pixeles"]},
        ],
        "correto_voz": "Correcto!", "erro_voz": "Incorrecto. La respuesta es ",
    },
}
# Estado ══════════════════════════════════════════
S = {
    "idioma": None, "acertos": 0, "erros": 0,
    "vistas": set(), "card_i": 0,
    "quiz_palavra": None, "quiz_opcoes": [], "quiz_resp": "", "quiz_sel": None,
    "frase_i": 0, "frase_sel": None,
}
# Cores
BG   = "#0f1923"; CARD = "#1a2a3a"; DEST = "#00c8ff"; BT ="#2c3e50"
VERD = "#2ecc71"; VERM = "#e74c3c"; TEXT = "#ecf0f1"
CINZ = "#7f8c8d"; AMAR = "#f1c40f"; AZUL = "#2980b9"; ESPA = "#c0392b"

def vocab(): return IDIOMAS[S["idioma"]]["vocabulario"]
def frases(): return IDIOMAS[S["idioma"]]["frases"]
def lang():   return IDIOMAS[S["idioma"]]["lang_code"]
def cor_id(): return AZUL if S["idioma"] == "en" else ESPA

# JSON persistencia ══════════════════════════════════════════════
JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocab_extra.json")

def carregar_extras():
    if not os.path.exists(JSON_FILE): return
    try:
        for item in json.load(open(JSON_FILE, encoding="utf-8")):
            idm = item.get("idioma")
            if idm in IDIOMAS:
                if item["orig"] not in [w["orig"] for w in IDIOMAS[idm]["vocabulario"]]:
                    item.setdefault("frase_pt", "")
                    IDIOMAS[idm]["vocabulario"].append({**item, "extra": True})
    except: pass

def salvar_palavra(idioma, orig, pt, nivel, frase, frase_pt=""):
    extras = []
    if os.path.exists(JSON_FILE):
        try: extras = json.load(open(JSON_FILE, encoding="utf-8"))
        except: pass
    nova = {"idioma": idioma, "orig": orig, "pt": pt, "nivel": nivel, "frase": frase, "frase_pt": frase_pt}
    extras.append(nova)
    json.dump(extras, open(JSON_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    IDIOMAS[idioma]["vocabulario"].append({**nova, "extra": True})

# App ══════════════════════════════════════════════
class LinguApp:
    def __init__(self):
        self.fig = plt.figure(figsize=(13, 8), facecolor=BG)
        self.fig.canvas.manager.set_window_title("Lingu — Aprenda novos idiomas")
        self.ax   = self.fig.add_axes([0.02, 0.15, 0.96, 0.82])
        self.axst = self.fig.add_axes([0.02, 0.02, 0.96, 0.10])
        self.btns = {}
        self.axst.set_facecolor(CARD); self.axst.axis("off")
        self._st = self.axst.text(0.5, 0.5, "✦ Lingu | Escolha um Idioma",
            transform=self.axst.transAxes, ha="center", va="center",
            fontsize=11, color=DEST, fontweight="bold")
        carregar_extras()
        self._poll_ui()          # inicia polling da fila de callbacks
        self.tela_idioma()

    def _poll_ui(self):
        #Verifica a fila a cada 100 ms e executa callbacks na thread principal (Tk).
        try:
            while True:
                fn = _UI_QUEUE.get_nowait()
                fn()
        except queue.Empty:
            pass
        
        self.fig.canvas.get_tk_widget().after(100, self._poll_ui)

    def status(self, msg):
        pre = f"[{IDIOMAS[S['idioma']]['nome']}] | " if S["idioma"] else ""
        self._st.set_text(f"✦ Lingu | {pre}{msg} | ✔ Acertos: {S['acertos']}  ✘ Erros: {S['erros']}  Palavras: {len(S['vistas'])}")
        self.fig.canvas.draw_idle()

    def limpar(self):
        self.ax.cla(); self.ax.set_facecolor(BG); self.ax.axis("off")
        
        for txt in getattr(self, "_add_labels", []):
            try: txt.remove()
            except: pass
        self._add_labels = []
        # Remove todos os eixos/botões registrados
        for b in list(self.btns.values()):
            try: b.ax.remove()   # Button
            except:
                try: b.remove()  # Axes direto
                except: pass
        self.btns.clear()

    def btn(self, label, rect, cb, cor=None, fs=10):
        cor = cor or "#16a085"
        ab = self.fig.add_axes(rect)
        b  = Button(ab, label, color=cor, hovercolor=DEST)
        b.label.set_color("white"); b.label.set_fontsize(fs); b.label.set_fontweight("bold")
        b.on_clicked(cb)
        # Chave única por eixo para evitar colisão de labels repetidos entre telas
        key = f"_btn_{id(ab)}"
        self.btns[key] = b

    def card_bg(self, x, y, w, h, cor):
        self.ax.add_patch(mpatches.FancyBboxPatch((x,y), w, h,
            boxstyle="round,pad=0.02", linewidth=2,
            edgecolor=cor, facecolor=CARD, transform=self.ax.transAxes))

    def txt(self, x, y, s, cor=TEXT, fs=12, bold=False, italic=False):
        self.ax.text(x, y, s, ha="center", va="center", fontsize=fs,
            color=cor, fontweight="bold" if bold else "normal",
            style="italic" if italic else "normal", transform=self.ax.transAxes)

    # Seleção de idioma ══════════════════════════════════════════════
    def tela_idioma(self, _=None):
        S["idioma"] = None
        self.limpar()

        self.txt(0.49, 0.88, "✦ Lingu", cor=DEST, fs=34, bold=True)
        self.txt(0.5, 0.78, "Aprenda novos idiomas", cor=TEXT, fs=14)
        self.txt(0.5, 0.68, "Escolha o idioma:", cor=CINZ, fs=12)
        self.card_bg(0.08, 0.22, 0.36, 0.36, AZUL)
        self.txt(0.26, 0.48, "US", cor=AZUL, fs=30, bold=True)
        self.txt(0.26, 0.38, "Inglês", cor=TEXT, fs=18, bold=True)
        self.txt(0.26, 0.30, "English", cor=CINZ, fs=12)
        self.card_bg(0.56, 0.22, 0.36, 0.36, ESPA)
        self.txt(0.74, 0.48, "ES", cor=ESPA, fs=30, bold=True)
        self.txt(0.74, 0.38, "Espanhol", cor=TEXT, fs=18, bold=True)
        self.txt(0.74, 0.30, "Espanol", cor=CINZ, fs=12)
        self.btn("Estudar Inglês",   [0.12, 0.14, 0.32, 0.10], lambda e: self._sel("en"), cor=AZUL, fs=12)
        self.btn("Estudar Espanhol", [0.56, 0.14, 0.32, 0.10], lambda e: self._sel("es"), cor=ESPA, fs=12)
        self.status("Selecione um idioma")
        self.fig.canvas.draw_idle()

    def _sel(self, idm):
        S.update({"idioma": idm, "acertos": 0, "erros": 0, "vistas": set(), "card_i": 0})
        som_nav()
        falar("Welcome to English study mode" if idm=="en" else "Bienvenido al modo de estudio de Español", lang=idm)
        self.tela_menu()

    # Menu ══════════════════════════════════════════════
    def tela_menu(self, _=None):
        self.limpar()
        self.ax.set_xlim(0,1); self.ax.set_ylim(0,1)
        d = IDIOMAS[S["idioma"]]

        self.txt(0.5, 0.90, f"{d['nome']} — ✦ Lingu", cor=cor_id(), fs=22, bold=True)
        self.txt(0.5, 0.81, "Selecione uma atividade:", cor=CINZ, fs=12)
        for x, val, lbl, cor in [
            (0.14, S["acertos"],     "✔ Acertos", VERD),
            (0.38, S["erros"],       "✘  Erros",   VERM),
            (0.62, len(S["vistas"]), "Palavras Vistas",  DEST),
            (0.86, len(vocab()),     "Total",   AMAR),
        ]:
            self.card_bg(x-0.08, 0.57, 0.16, 0.12, cor)
            self.txt(x, 0.66, str(val), cor=cor, fs=18, bold=True)
            self.txt(x, 0.59, lbl, cor=TEXT, fs=9)
        self.btn("🃏 Flashcards",     [0.15, 0.35, 0.19, 0.10], self.tela_flashcard, cor=cor_id())
        self.btn("░  Quiz",           [0.40, 0.35, 0.19, 0.10], self.tela_quiz,      cor=cor_id())
        self.btn("✍ Complete Frase", [0.65, 0.35, 0.19, 0.10], self.tela_frase,     cor=cor_id())
        self.btn("Progresso",      [0.15, 0.20, 0.19, 0.09], self.tela_progresso, cor=BT)
        self.btn("Add Palavra",    [0.40, 0.20, 0.19, 0.09], self.tela_add,       cor="#6c3483")
        self.btn("Trocar Idioma",  [0.65, 0.20, 0.19, 0.09], self.tela_idioma,    cor=BT)
        self.status("Menu Principal")
        self.fig.canvas.draw_idle()

    # Flashcards ══════════════════════════════════════════════
    def tela_flashcard(self, _=None):
        idx  = S["card_i"] % len(vocab())
        card = vocab()[idx]
        S["vistas"].add(card["orig"])
        som_nav()
        self.limpar()
        self.ax.set_xlim(0,1); self.ax.set_ylim(0,1)

        self.card_bg(0.10, 0.24, 0.80, 0.62, cor_id())
        self.txt(0.5, 0.91, f"🃏 Flashcard {idx+1}/{len(vocab())}", cor=CINZ, fs=12)
        self.txt(0.5, 0.80, card["orig"].upper(), cor=cor_id(), fs=30, bold=True)
        self.txt(0.5, 0.70, card["pt"], cor=TEXT, fs=22)

        self.txt(0.5, 0.58, f'"{card["frase"]}"', cor=CINZ, fs=11, italic=True)

        frase_pt = card.get("frase_pt", "")
        if frase_pt:
            self.txt(0.5, 0.48, f'({frase_pt})', cor=AMAR, fs=10, italic=True)

        ncor = {"Básico": VERD, "Médio": AMAR, "Avançado": VERM}.get(card["nivel"], CINZ)
        self.ax.add_patch(mpatches.FancyBboxPatch((0.42,0.33),0.16,0.06,
            boxstyle="round,pad=0.01", linewidth=1, edgecolor=ncor, facecolor=BG,
            transform=self.ax.transAxes))
        self.txt(0.5, 0.36, f"Nivel: {card['nivel']}", cor=ncor, fs=12, bold=True)

        self.btn("◀  Anterior",   [0.05, 0.15, 0.16, 0.09], self._fc_ant)
        self.btn("▶  Proximo",    [0.23, 0.15, 0.16, 0.09], self._fc_prox)
        self.btn("♫  Ouvir",      [0.41, 0.15, 0.16, 0.09], lambda e: falar(card["orig"], lang()), cor=BT)
        self.btn("♫  Ouvir Frase",[0.59, 0.15, 0.16, 0.09], lambda e: falar(card["frase"], lang()), cor=BT)
        self.btn("Menu",       [0.77, 0.15, 0.16, 0.09], self.tela_menu, cor=BT)
        self.status(f"🃏 Flashcard")
        self.fig.canvas.draw_idle()
        falar(card["orig"], lang())  

    def _fc_prox(self, _=None): S["card_i"] += 1; self.tela_flashcard()
    def _fc_ant(self,  _=None): S["card_i"] = max(0, S["card_i"]-1); self.tela_flashcard()

    # Quiz ══════════════════════════════════════════════
    def tela_quiz(self, _=None):
        p = random.choice(vocab())
        erradas = random.sample([w for w in vocab() if w["orig"] != p["orig"]], min(3, len(vocab())-1))
        opcoes = [p["pt"]] + [w["pt"] for w in erradas]
        random.shuffle(opcoes)
        S.update({"quiz_palavra": p, "quiz_opcoes": opcoes, "quiz_resp": p["pt"], "quiz_sel": None})
        S["vistas"].add(p["orig"])
        self._draw_quiz()
        falar(p["orig"], lang())  

    def _draw_quiz(self, res=None):
        self.limpar()
        self.ax.set_xlim(0,1); self.ax.set_ylim(0,1)
        p = S["quiz_palavra"]
        self.txt(0.5, 0.91, "░ Quiz de Vocabulário", cor=cor_id(), fs=20, bold=True)
        self.txt(0.5, 0.85, "Qual e a tradução da palavra?", cor=CINZ, fs=13)
        self.card_bg(0.08, 0.64, 0.76, 0.13, cor_id())
        self.txt(0.50, 0.71, p["orig"].upper(), cor=TEXT, fs=26, bold=True)

        self.btn("♫ Ouvir", [0.88, 0.68, 0.09, 0.09], lambda e: falar(p["orig"], lang()), cor=BT)

        pos = [(0.08,0.50),(0.53,0.50),(0.08,0.35),(0.53,0.35)]
        for opt, (ox,oy) in zip(S["quiz_opcoes"], pos):
            if res is not None and S["quiz_sel"] == opt:
                cor = VERD if opt == S["quiz_resp"] else VERM
            elif res is not None and opt == S["quiz_resp"]:
                cor = VERD
            else:
                cor =BT
            self.btn(opt, [ox, oy, 0.38, 0.10], lambda e,o=opt: self._resp_quiz(o), cor=cor)

        if res == "ok":
            self.txt(0.5, 0.14, "✔  Correto!", cor=VERD, fs=18, bold=True)
            self.btn("▶ Proxima", [0.25, 0.13, 0.24, 0.09], self.tela_quiz)
            self.btn("Menu",    [0.52, 0.13, 0.24, 0.09], self.tela_menu, cor=BT)
        elif res == "err":
            self.txt(0.5, 0.17, f"✘  Errado!", cor=VERM, fs=13, bold=True)
            self.txt(0.5, 0.13, f"Resposta: {S['quiz_resp']}", cor=VERM, fs=13, bold=True)
            self.btn("Proxima", [0.25, 0.13, 0.24, 0.09], self.tela_quiz)
            self.btn("Menu",    [0.52, 0.13, 0.24, 0.09], self.tela_menu, cor=BT)
        self.status("Quiz de Vocabulario")
        self.fig.canvas.draw_idle()

    def _resp_quiz(self, opt):
        S["quiz_sel"] = opt
        d = IDIOMAS[S["idioma"]]
        if opt == S["quiz_resp"]:
            S["acertos"] += 1; som_acerto(); falar(d["correto_voz"], lang()); self._draw_quiz("ok")
        else:
            S["erros"] += 1; som_erro(); falar(d["erro_voz"]+S["quiz_resp"], lang()); self._draw_quiz("err")

    # Complete a frase ══════════════════════════════════════════════
    def tela_frase(self, _=None):
        S["frase_i"] = random.randint(0, len(frases())-1)
        S["frase_sel"] = None
        self._draw_frase()
       
        ex = frases()[S["frase_i"]]
        falar(ex["frase"].replace("___", "blank"), lang())

    def _draw_frase(self, res=None):
        self.limpar()
        self.ax.set_xlim(0,1); self.ax.set_ylim(0,1)
        ex = frases()[S["frase_i"]]
        self.txt(0.5, 0.91, "✍ Complete a Frase", cor=cor_id(), fs=20, bold=True)
        self.txt(0.5, 0.83, "Escolha a palavra correta:", cor=CINZ, fs=12)
        self.card_bg(0.10, 0.64, 0.76, 0.13, AMAR)
        self.txt(0.50, 0.70, ex["frase"], cor=TEXT, fs=15, bold=True)

        self.btn("♫ Ouvir", [0.88, 0.68, 0.09, 0.09],
            lambda e: falar(ex["frase"].replace("___","blank"), lang()), cor="#2c3e50")

        pos = [(0.08,0.50),(0.53,0.50),(0.08,0.35),(0.53,0.35)]
        opcoes = ex.get("opcoes") or ex.get("opçoes") or []
        for opt, (ox,oy) in zip(opcoes, pos):
            if res is not None and S["frase_sel"] == opt:
                cor = VERD if opt == ex["resposta"] else VERM
            elif res is not None and opt == ex["resposta"]:
                cor = VERD
            else:
                cor = BT
            self.btn(opt, [ox, oy, 0.38, 0.10], lambda e,o=opt: self._resp_frase(o), cor=cor)

        if res == "ok":
            self.txt(0.5, 0.14, "Correto!", cor=VERD, fs=16, bold=True)
            self.txt(0.5, 0.19, ex["frase"].replace("___", ex["resposta"]), cor=CINZ, fs=12, italic=True)
            self.btn("Proxima", [0.25, 0.12, 0.24, 0.09], self.tela_frase)
            self.btn("Menu",    [0.52, 0.12, 0.24, 0.09], self.tela_menu, cor=BT)
        elif res == "err":
            self.txt(0.5, 0.17, f'✘ Errado!"', cor=VERM, fs=13, bold=True)
            self.txt(0.5, 0.13, f'Resposta: "{ex["resposta"]}"', cor=VERM, fs=13, bold=True)
            self.btn("Proxima", [0.25, 0.12, 0.24, 0.09], self.tela_frase)
            self.btn("Menu",    [0.52, 0.12, 0.24, 0.09], self.tela_menu, cor=BT)
        self.status("Complete a Frase")
        self.fig.canvas.draw_idle()

    def _resp_frase(self, opt):
        S["frase_sel"] = opt
        ex = frases()[S["frase_i"]]
        d  = IDIOMAS[S["idioma"]]
        if opt == ex["resposta"]:
            S["acertos"] += 1; som_acerto()
            falar(d["correto_voz"]+" "+ex["frase"].replace("___",ex["resposta"]), lang())
            self._draw_frase("ok")
        else:
            S["erros"] += 1; som_erro()
            falar(d["erro_voz"]+ex["resposta"], lang())
            self._draw_frase("err")

    # Progresso ══════════════════════════════════════════════
    def tela_progresso(self, _=None):
        self.limpar()
        self.ax.set_facecolor(BG); self.ax.axis("off")
        total = S["acertos"] + S["erros"]
        d = IDIOMAS[S["idioma"]]
        self.ax.text(0.5, 0.95, f"{d['nome']} — Progresso", ha="center", va="center",
            fontsize=18, color=cor_id(), fontweight="bold", transform=self.ax.transAxes)

        ax_pie = self.fig.add_axes([0.05, 0.35, 0.38, 0.48])
        self.btns["_pie"] = ax_pie
        ax_pie.set_facecolor(BG)
        if total > 0:
            ax_pie.pie([S["acertos"], S["erros"]],
                labels=[f'Acertos\n{S["acertos"]}', f'Erros\n{S["erros"]}'],
                colors=[VERD, VERM], autopct="%1.0f%%", startangle=90,
                textprops={"color": TEXT, "fontsize": 10})
        else:
            ax_pie.text(0.5, 0.5, "Sem dados", ha="center", va="center", fontsize=12, color=CINZ)
        ax_pie.set_title("Resultado", color=TEXT, fontsize=11, fontweight="bold")

        ax_bar = self.fig.add_axes([0.52, 0.35, 0.44, 0.48])
        self.btns["_bar"] = ax_bar
        ax_bar.set_facecolor(CARD)
        niveis = ["Básico", "Médio", "Avançado"]
        tn = {n: sum(1 for w in vocab() if w["nivel"]==n) for n in niveis}
        vn = {n: sum(1 for w in vocab() if w["nivel"]==n and w["orig"] in S["vistas"]) for n in niveis}
        x = np.arange(len(niveis))
        ax_bar.bar(x, [tn[n] for n in niveis], width=0.6, color=BT, label="Total")
        ax_bar.bar(x, [vn[n] for n in niveis], width=0.6, color=cor_id(), alpha=0.9, label="Estudadas")
        ax_bar.set_xticks(x); ax_bar.set_xticklabels(niveis, color=TEXT, fontsize=10)
        ax_bar.set_title("Por Nível", color=TEXT, fontsize=11, fontweight="bold")
        ax_bar.tick_params(colors=CINZ, labelsize=9)
        ax_bar.legend(facecolor=BG, labelcolor=TEXT, fontsize=8)
        for sp in ax_bar.spines.values(): sp.set_color(CINZ)

        pct = round(S["acertos"]/total*100) if total > 0 else 0
        self.ax.text(0.5, 0.15,
            f"Respostas: {total}  |  Acerto: {pct}%  |  Palavras: {len(S['vistas'])}/{len(vocab())}",
            ha="center", va="center", fontsize=11, color=TEXT, transform=self.ax.transAxes)

        def voltar(e):
            for k in ["_pie","_bar"]:
                if k in self.btns: self.btns.pop(k).remove()
            self.tela_menu()
        self.btn("Voltar ao Menu", [0.38, 0.13, 0.24, 0.09], voltar, cor="#2c3e50")
        self.status("Progresso")
        self.fig.canvas.draw_idle()

#  Adicionar palavra  (PT → idioma alvo via Google Translate)
  
    def tela_add(self, _=None, msg="", _prefill=None):
        self.limpar()
        self.ax.set_xlim(0,1); self.ax.set_ylim(0,1)
        d = IDIOMAS[S["idioma"]]
        src = lang()  # "en" ou "es"

      
        self.txt(0.5, 0.96, f"Adicionar Palavra — {d['nome']}", cor=cor_id(), fs=16, bold=True)

       
        for txt in getattr(self, "_add_labels", []):
            try: txt.remove()
            except: pass
        self._add_labels = []

        def figlabel(fx, fy, s, cor=TEXT):
            t = self.fig.text(fx, fy, s, fontsize=10, color=cor,
                              fontweight="bold", va="bottom")
            self._add_labels.append(t)

        # Palavra em PT e botão para traduzir o idioma 
        figlabel(0.13, 0.895, "Palavra em Português:")
        figlabel(0.73, 0.895, f"→  {d['nome']}:", cor=cor_id())
        ax_pt  = self.fig.add_axes([0.13, 0.830, 0.38, 0.052])   
        ax_orig = self.fig.add_axes([0.57, 0.830, 0.30, 0.052])  

        # Frase em PT e botão para traduzir a frase 
        figlabel(0.13, 0.700, "Frase em Português:")
        figlabel(0.73, 0.700, f"→  Frase em {d['nome']}:", cor=cor_id())
        ax_fpt = self.fig.add_axes([0.13, 0.635, 0.38, 0.052])   
        ax_f   = self.fig.add_axes([0.57, 0.635, 0.30, 0.052])   

        tb_pt   = TextBox(ax_pt,   "", color=CARD, hovercolor="#1e3a5f")
        tb_orig = TextBox(ax_orig, "", color="#0d2035", hovercolor="#1e3a5f")
        tb_fpt  = TextBox(ax_fpt,  "", color=CARD, hovercolor="#1e3a5f")
        tb_f    = TextBox(ax_f,    "", color="#0d2035", hovercolor="#1e3a5f")

        for tb in [tb_pt, tb_orig, tb_fpt, tb_f]:
            tb.text_disp.set_color(TEXT); tb.text_disp.set_fontsize(10)

        
        tb_orig.text_disp.set_color(cor_id())
        tb_f.text_disp.set_color(cor_id())

        
        if _prefill:
            tb_pt.set_val(  _prefill.get("pt",       ""))
            tb_orig.set_val(_prefill.get("orig",      ""))
            tb_fpt.set_val( _prefill.get("frase_pt",  ""))
            tb_f.set_val(   _prefill.get("frase",     ""))

        for k, v in [("_ao",ax_orig),("_ap",ax_pt),("_af",ax_f),("_ag",ax_fpt),
                     ("_to",tb_orig),("_tp",tb_pt),("_tf",tb_f),("_tg",tb_fpt)]:
            self.btns[k] = v

        # ── Botão Traduzir Palavra ─────────────────────────────────────
        def _traduzir_palavra(e):
            palavra_pt = self.btns["_tp"].text.strip()
            if not palavra_pt:
                self._fechar_add(); self.tela_add(msg="Digite a palavra em português!")
                return
            self._st.set_text("✦ Lingu | Traduzindo palavra... aguarde")
            self.fig.canvas.draw_idle()
            frase_pt_salva = self.btns["_tg"].text.strip()
            frase_id_salva = self.btns["_tf"].text.strip()

            def _buscar():
                orig = _gt_translate(palavra_pt, "pt", src) or ""
                prefill = {"pt": palavra_pt, "orig": orig,
                           "frase_pt": frase_pt_salva, "frase": frase_id_salva}
                def _cb():
                    self._fechar_add()
                    m = f'"{palavra_pt}" → "{orig}"' if orig else "Sem conexão."
                    self.tela_add(msg=m, _prefill=prefill)
                _UI_QUEUE.put(_cb)
            threading.Thread(target=_buscar, daemon=True).start()

        ax_trp = self.fig.add_axes([0.52, 0.830, 0.04, 0.052])
        b_trp  = Button(ax_trp, "▶", color="#16a085", hovercolor=DEST)
        b_trp.label.set_color("white"); b_trp.label.set_fontsize(13); b_trp.label.set_fontweight("bold")
        b_trp.on_clicked(_traduzir_palavra)
        self.btns["_atrp"] = ax_trp
        self.btns["_bt_trp"] = b_trp

        # ── Botão Traduzir Frase ───────────────────────────────────────
        def _traduzir_frase(e):
            frase_pt = self.btns["_tg"].text.strip()
            if not frase_pt:
                self._fechar_add()
                self.tela_add(msg="Digite a frase em português!",
                              _prefill={"pt": self.btns["_tp"].text.strip(),
                                        "orig": self.btns["_to"].text.strip(),
                                        "frase": self.btns["_tf"].text.strip(),
                                        "frase_pt": ""})
                return
            self._st.set_text("✦ Lingu | Traduzindo frase... aguarde")
            self.fig.canvas.draw_idle()
            pt_salvo   = self.btns["_tp"].text.strip()
            orig_salvo = self.btns["_to"].text.strip()

            def _buscar():
                frase_id = _gt_translate(frase_pt, "pt", src) or ""
                prefill  = {"pt": pt_salvo, "orig": orig_salvo,
                            "frase_pt": frase_pt, "frase": frase_id}
                def _cb():
                    self._fechar_add()
                    m = "OK! Frase traduzida!" if frase_id else "Sem conexão."
                    self.tela_add(msg=m, _prefill=prefill)
                _UI_QUEUE.put(_cb)
            threading.Thread(target=_buscar, daemon=True).start()

        ax_trf = self.fig.add_axes([0.52, 0.635, 0.04, 0.052])
        b_trf  = Button(ax_trf, "▶", color=AZUL, hovercolor=DEST)
        b_trf.label.set_color("white"); b_trf.label.set_fontsize(13); b_trf.label.set_fontweight("bold")
        b_trf.on_clicked(_traduzir_frase)
        self.btns["_atrf"] = ax_trf
        self.btns["_bt_trf"] = b_trf

        # ── Nível ──────────────────────────────────────────────────────
        self._nivel = "Básico"
        figlabel(0.13, 0.505, "Nível:")
        for nivel, cor, xb in [("Básico",VERD,0.28),("Médio",AMAR,0.44),("Avançado",VERM,0.60)]:
            self.btn(nivel, [xb, 0.400, 0.12, 0.065],
                     lambda e,n=nivel: setattr(self,"_nivel",n), cor=cor)

        # ── Feedback ──────────────────────────────────────────────────
        if msg:
            self.txt(0.5, 0.51, msg, cor=VERD if "OK" in msg else VERM, fs=11, bold=True)

        # ── Salvar / Cancelar ──────────────────────────────────────────
        def salvar(e):
            orig  = self.btns["_to"].text.strip()   # palavra no idioma
            pt    = self.btns["_tp"].text.strip()   # palavra em PT
            frase = self.btns["_tf"].text.strip()   # frase no idioma
            fp    = self.btns["_tg"].text.strip()   # frase em PT
            if not orig or not pt:
                self._fechar_add(); self.tela_add(msg="Preencha a palavra nos dois idiomas!")
                return
            salvar_palavra(S["idioma"], orig, pt, self._nivel, frase, fp)
            som_acerto(); falar(orig, lang())
            self._fechar_add(); self.tela_add(msg=f'OK! "{orig}" ({pt}) adicionada!')

        self.btn("💾 Salvar",   [0.20, 0.285, 0.26, 0.070], salvar, cor="#6c3483")
        self.btn("Cancelar", [0.54, 0.285, 0.26, 0.070], self._voltar_add, cor=BT)
        self.status(f"Adicionar — {d['nome']}")
        self.fig.canvas.draw_idle()


    def _fechar_add(self):
        
        for k in ["_ao","_ap","_af","_ag","_atrp","_atrf"]:
            if k in self.btns:
                try: self.btns.pop(k).remove()
                except: pass
        for k in ["_to","_tp","_tf","_tg","_bt_trp","_bt_trf"]:
            self.btns.pop(k, None)
        # Vai remover todos os botões de nível, Salvar, Cancelar que sobrarem
        for k in list(self.btns.keys()):
            if k.startswith("_btn_"):
                try: self.btns.pop(k).ax.remove()
                except: pass
        
        for txt in getattr(self, "_add_labels", []):
            try: txt.remove()
            except: pass
        self._add_labels = []

    def _voltar_add(self, _=None):
        self._fechar_add(); self.tela_menu()

    def run(self): plt.show()

if __name__ == "__main__":
    print("=" * 55)
    print("Lingu — Aprenda novos idiomas")
    print(f"  pyttsx3 (voz TTS): {'OK' if TTS_OK else 'NAO ENCONTRADO'}")
    print(f"  winsound (sons):   {'OK' if WINSOUND_OK else 'NAO ENCONTRADO'}")
    print(f"  matplotlib:        OK")
    print(f"  numpy:             OK")
    print("=" * 55)
    LinguApp().run()
