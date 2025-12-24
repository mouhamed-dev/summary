from django.shortcuts import render
from django.http import JsonResponse
from youtube_transcript_api import YouTubeTranscriptApi
from django.conf import settings
import re
import os
from urllib.parse import urlparse, parse_qs
import time, requests
from http.cookiejar import MozillaCookieJar
from django.utils import timezone

try:
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
        TooManyRequests,
        NotTranslatable,
    )
except Exception:
    TranscriptsDisabled = NoTranscriptFound = VideoUnavailable = TooManyRequests = NotTranslatable = Exception



import time
import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    TooManyRequests,
    NotTranslatable,
)
from xml.etree import ElementTree as ET

# import pytube & yt_dlp fallbacks
try:
    from pytube import YouTube as PyTube
except Exception:
    PyTube = None

try:
    import yt_dlp
except Exception:
    yt_dlp = None


hour = timezone.localtime().hour
salutation = "Bonsoir" if hour >= 17 else "Bonjour"


def index(request):
    context = {"salutation": salutation}
    return render(request, "youtube/index.html", context)

def extract_video_id(url: str):
    try:
        p = urlparse(url.strip())
        host = (p.hostname or "").lower()
        path = p.path or ""

        if host in {"youtu.be", "www.youtu.be"}:
            vid = path.lstrip("/").split("/")[0]
        elif host.endswith("youtube.com") and path == "/watch":
            vid = parse_qs(p.query).get("v", [None])[0]
        elif host.endswith("youtube.com") and path.startswith("/shorts/"):
            parts = [x for x in path.split("/") if x]
            vid = parts[1] if len(parts) > 1 else None
        elif host.endswith("youtube.com") and path.startswith("/embed/"):
            parts = [x for x in path.split("/") if x]
            vid = parts[1] if len(parts) > 1 else None
        else:
            m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([\w-]{11})", url)
            vid = m.group(1) if m else None

        if vid:
            vid = vid.split("?")[0].split("&")[0]
        return vid
    except Exception:
        return None




def _join_segments(segments):
    return " ".join([
        (s.get("text") if isinstance(s, dict) else getattr(s, "text", "")).strip()
        for s in segments
        if (s.get("text") if isinstance(s, dict) else getattr(s, "text", ""))
    ]).strip()

def _load_cookies(cookie_path: str):
    try:
        cj = MozillaCookieJar()
        cj.load(cookie_path, ignore_discard=True, ignore_expires=True)
        return cj
    except Exception:
        return None

def fetch_transcript_text(video_id: str, cookie_path: str | None = None) -> str:
    """
    Extraction via yt-dlp (sous-titres YouTube).
    """
    try:
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "quiet": True,
            "subtitlesformat": "srt",
            "geo_bypass": True,
            "noplaylist": True,
            "nocheckcertificate": True,
            "extractor_args": {"youtube": {"player_client": ["default"]}},
        }
        if cookie_path and os.path.exists(cookie_path):
            ydl_opts["cookiefile"] = cookie_path
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            subs = info.get("subtitles") or {}
            auto = info.get("automatic_captions") or {}
            def get_text_from_subs(subdict):
                preferred_order = ["fr", "fr-FR", "fr-CA", "en", "en-US", "en-GB"]
                tried = set()
                # 1) FR/EN
                for lang in preferred_order:
                    entries = subdict.get(lang) or subdict.get(lang.split("-")[0]) or None
                    if entries:
                        tried.add(lang)
                        entry = entries[0]
                        url = entry.get("url")
                        if url:
                            try:
                                cookies = _load_cookies(cookie_path) if cookie_path else None
                                r = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "fr,en;q=0.8"}, cookies=cookies)
                                if r.status_code == 200 and r.text.strip():
                                    t = re.sub(r"^\d+\n", "", r.text, flags=re.MULTILINE)
                                    t = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3} --> .*", "", t)
                                    t = re.sub(r"^\s+|\s+$", "", t, flags=re.MULTILINE)
                                    t = re.sub(r"\n{2,}", "\n", t).strip()
                                    return t.replace("\n", " ")
                            except Exception:
                                continue
                # 2) Autres langues
                for lang, entries in subdict.items():
                    if lang in tried:
                        continue
                    if not entries:
                        continue
                    entry = entries[0]
                    url = entry.get("url")
                    if url:
                        try:
                            cookies = _load_cookies(cookie_path) if cookie_path else None
                            r = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "fr,en;q=0.8"}, cookies=cookies)
                            if r.status_code == 200 and r.text.strip():
                                t = re.sub(r"^\d+\n", "", r.text, flags=re.MULTILINE)
                                t = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3} --> .*", "", t)
                                t = re.sub(r"^\s+|\s+$", "", t, flags=re.MULTILINE)
                                t = re.sub(r"\n{2,}", "\n", t).strip()
                                return t.replace("\n", " ")
                        except Exception:
                            continue
                return None

            for candidate in (auto, subs):
                text = get_text_from_subs(candidate)
                if text:
                    print("[fetch_transcript_text] OK via yt-dlp subtitles")
                    return text
        raise Exception("Aucun sous-titre trouvé ou extraction bloquée (vérifiez que la vidéo autorise les sous-titres, votre connexion réseau et le blocage géographique).")
    except Exception as e:
        raise Exception(f"Impossible d'extraire la transcription : {e}")



""" ✅✅ """

def summarize_video(request):
    # POST or GET (AJAX fetch)
    video_url = request.POST.get("url") or request.GET.get("url")
    langue = (request.POST.get("langue") or request.GET.get("langue") or "fr").lower()
    taille = (request.POST.get("taille") or request.GET.get("taille") or "short").lower()
    if not video_url:
        return JsonResponse({"error": "Veuillez fournir une URL YouTube"}, status=400)

    # Supported languages
    supported_langs = {"fr": "français", "en": "English", "es": "Espagnol", "de": "Allemand", "ar": "Arabe", "it": "Italien"}
    if langue not in supported_langs:
        langue = "fr" 
    langue_label = supported_langs[langue]

    # Supported sizes
    size_map = {"short": "court", "medium": "moyen", "long": "détaillé"}
    if taille not in size_map:
        taille = "short"
    taille_label = size_map[taille]

    # Get API key
    api_key = getattr(settings, "GOOGLE_GENAI_API_KEY", None)
    if not api_key:
        return JsonResponse({"error": "Clé API Google Gemini manquante. Définissez GOOGLE_GENAI_API_KEY dans settings.py."}, status=500)

    # Import SDK
    try:
        from google import genai
    except ModuleNotFoundError:
        return JsonResponse({
            "error": "Package manquant: installez 'google-genai' (pip install google-genai)"
        }, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Erreur SDK Gemini: {str(e)}"}, status=500)
    
    # Configure client
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        return JsonResponse({"error": f"Erreur d'initialisation du client Gemini: {str(e)}"}, status=500)

    video_id = extract_video_id(video_url)
    if not video_id:
        return JsonResponse({"error": "URL YouTube invalide"}, status=400)

    # Diagnostic HTTP
    try:
        diag_url = f"https://www.youtube.com/watch?v={video_id}"
        resp = requests.get(diag_url, timeout=5)
        print(f"Diagnostic HTTP: {diag_url} -> {resp.status_code}, content={len(resp.content)} bytes")
    except requests.exceptions.RequestException as e:
        print(f"Diagnostic HTTP échoué pour {diag_url}: {e}")

    try:
        cookie_path = settings.COOKIE_FILE_PATH
        text = fetch_transcript_text(video_id, cookie_path=cookie_path)
        if not text.strip():
            return JsonResponse({"error": "Transcription vide ou indisponible."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    # Prompt: adapt language and size
    prompt = (
        f"Tu es un assistant qui résume des vidéos YouTube dans la langue suivante : {langue_label}. "
        f"Génère un résumé clair et concis avec des phrases complètes, sans guillemets autour des mots ou expressions. "
        f"Structure le résumé en paragraphes ou points clés avec contexte, suivi d'une conclusion courte. "
        f"Le résumé doit être de taille : {taille_label}. "
        f"Si la transcription est longue, regroupe par thèmes.\n"
        f"IMPORTANT: Le résumé doit être rédigé en {langue_label} uniquement.\n"
        f"Transcription :\n{text}"
    )
    if langue == "en":
        prompt = (
            f"You are an assistant that summarizes YouTube videos in English. "
            f"Generate a clear and concise summary with full sentences, without quotation marks around words or phrases. "
            f"Structure the summary in paragraphs or key points with context, followed by a short conclusion. "
            f"The summary should be {taille_label} in length. "
            f"If the transcript is long, group by themes.\n"
            f"IMPORTANT: The summary must be written in English only.\n"
            f"Transcript:\n{text}"
        )
    elif langue == "es":
        prompt = (
            f"Eres un asistente que resume videos de YouTube en español. "
            f"Genera un resumen claro y conciso con frases completas, sin comillas alrededor de palabras o frases. "
            f"Estructura el resumen en párrafos o puntos clave con contexto, seguido de una breve conclusión. "
            f"El resumen debe ser de tamaño {taille_label}. "
            f"Si la transcripción es larga, agrupa por temas.\n"
            f"IMPORTANTE: El resumen debe estar escrito solo en español.\n"
            f"Transcripción:\n{text}"
        )
    elif langue == "de":
        prompt = (
            f"Du bist ein Assistent, der YouTube-Videos auf Deutsch zusammenfasst. "
            f"Erstelle eine klare und präzise Zusammenfassung mit vollständigen Sätzen, ohne Anführungszeichen um Wörter oder Phrasen. "
            f"Strukturiere die Zusammenfassung in Absätzen oder Schlüsselpunkten mit Kontext, gefolgt von einem kurzen Fazit. "
            f"Die Zusammenfassung sollte {taille_label} sein. "
            f"Wenn das Transkript lang ist, gruppiere nach Themen.\n"
            f"WICHTIG: Die Zusammenfassung muss ausschließlich auf Deutsch verfasst sein.\n"
            f"Transkript:\n{text}"
        )
    elif langue == "ar":
        prompt = (
            f"أنت مساعد يلخص مقاطع فيديو يوتيوب باللغة العربية. "
            f"أنشئ ملخصًا واضحًا وموجزًا بجمل كاملة، بدون علامات تنصيص حول الكلمات أو العبارات. "
            f"هيكل الملخص في فقرات أو نقاط رئيسية مع السياق، متبوعة بخاتمة قصيرة. "
            f"يجب أن يكون الملخص بحجم {taille_label}. "
            f"إذا كان النص طويلاً، قم بالتجميع حسب الموضوعات.\n"
            f"مهم: يجب أن يكون الملخص باللغة العربية فقط.\n"
            f"النص:\n{text}"
        )
    
    elif langue == "it":
        prompt = (
            f"Sei un assistente che riassume video di YouTube in italiano. "
            f"Genera un riassunto chiaro e conciso con frasi complete, senza virgolette attorno a parole o frasi. "
            f"Struttura il riassunto in paragrafi o punti chiave con contesto, seguito da una breve conclusione. "
            f"Il riassunto deve essere di dimensione {taille_label}. "
            f"Se il testo è lungo, raggruppa per argomenti.\n"
            f"IMPORTANTE: Il riassunto deve essere scritto in italiano solo.\n"
            f"Testo:\n{text}"
        )   
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        summary = getattr(response, "text", None) or getattr(response, "output_text", None) or ""
    except Exception as e:
        msg = str(e)
        if (
            "RESOURCE_EXHAUSTED" in msg or
            "429" in msg or
            "quota" in msg.lower() or
            "rate limit" in msg.lower() or
            "Quota dépassé" in msg or
            "limite" in msg.lower()
        ):
            return JsonResponse({"error": "Désole 😔, le service de résumé est temporairement saturé. Merci de réessayer dans quelques minutes."}, status=429)
        return JsonResponse({"error": "Une erreur est survenue lors de la génération du résumé. Merci de réessayer plus tard."}, status=500)

    # --- Markdown to HTML ---
    import re, html
    def markdown_to_html(md: str) -> str:
        md = html.escape(md)
        # Bold: **text** <b>text</b>
        md = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', md)
        
        md = re.sub(r'^[\*-]\s+', '', md, flags=re.MULTILINE)
        
        lines = md.split('\n')
        html_lines = []
        for line in lines:
            line = line.strip()
            if line:
                
                line = re.sub(r'^[\*\-]\s*', '', line)
                title_match = re.match(r'^(#{1,3})\s+(.*)', line)
                if title_match:
                    level = len(title_match.group(1))
                    html_lines.append(f'<h{level} class="text-lg font-semibold">{title_match.group(2)}</h{level}>')
                elif line.strip():
                    html_lines.append(f'<p class="text-justify">{line}</p>')
        return '\n'.join(html_lines)

    summary_html = markdown_to_html(summary)
    return JsonResponse({"summary": summary, "summary_html": summary_html})
