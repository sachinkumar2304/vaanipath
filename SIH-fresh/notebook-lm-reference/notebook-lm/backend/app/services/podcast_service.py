import os
import json
import httpx
from pathlib import Path
from typing import Tuple, Optional
from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import speedup
import random
from google.cloud import texttospeech
AudioSegment.converter = r"C:\\ffmpeg\\ffmpeg-8.0.1-full_build\\bin\\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\\ffmpeg\\ffmpeg-8.0.1-full_build\\bin\\ffprobe.exe"


class PodcastService:
    """Service for generating podcast audio from document content"""

    def __init__(
        self,
        vector_store,
        audio_output_dir: Path,
        groq_api_key: str = None,
        elevenlabs_api_key: str = None,
        ollama_base_url: str = "http://localhost:11434",
        ollama_model: str = "llama3.2:latest",
        max_duration: int = 180,
    ):
        self.vector_store = vector_store
        self.audio_output_dir = audio_output_dir
        self.groq_api_key = groq_api_key
        self.elevenlabs_api_key = elevenlabs_api_key
        self.ollama_base_url = ollama_base_url
        self.ollama_model = ollama_model
        self.max_duration = max_duration

        # ElevenLabs voice IDs for different speakers
        # Alex: energetic male voice, Jordan: calm female voice
        self.voice_ids = {
            "Alex": "pNInz6obpgDQGcFmaJgB",      # Adam (free)
            "Jordan": "21m00Tcm4TlvDq8ikWAM"     # Rachel (free)
        }

        print("🎙️  Podcast Service initialized")
        print(f"   - Using {'ElevenLabs TTS' if elevenlabs_api_key else 'Google TTS (gTTS)'}")
        print(f"   - LLM: {'Groq API' if groq_api_key else 'Local Ollama'}")

    def _query_llm(self, prompt: str) -> str:
        """Query LLM (Groq or Ollama) - Groq is prioritized"""
        # Try Groq first if API key is available
        if self.groq_api_key:
            try:
                print("🤖 Using Groq API for dialogue generation...")
                with httpx.Client(timeout=120.0) as client:
                    response = client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.groq_api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": "llama-3.3-70b-versatile",
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.7,
                            "max_tokens": 2500,
                            "response_format": {"type": "json_object"},
                        },
                    )
                    if response.status_code == 200:
                        result = response.json()["choices"][0]["message"]["content"]
                        print("✅ Successfully received response from Groq API")
                        return result
                    else:
                        print(f"⚠️  Groq API returned status {response.status_code}: {response.text}")
            except Exception as e:
                print(f"❌ Groq API error: {e}, falling back to Ollama...")
        else:
            print("ℹ️  No Groq API key found, using Ollama...")

        # Fallback to Ollama
        try:
            print("🤖 Using local Ollama for dialogue generation...")
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                    },
                )
                if response.status_code == 200:
                    result = response.json()["response"]
                    print("✅ Successfully received response from Ollama")
                    return result
                else:
                    print(f"⚠️  Ollama returned status {response.status_code}")
                    return ""
        except Exception as e:
            print(f"❌ Error querying Ollama: {e}")
            return ""

    def generate_dialogue(self, document_id: str) -> list:
        """Generate podcast dialogue from document content"""
        chunks = self.vector_store.get_all_chunks(document_id)
        if not chunks:
            return []
        content = "\n".join(chunks[:10])[:6000]
        prompt = f"""Create a podcast script as a JSON array. Two hosts discuss a document naturally.

HOSTS:
- Alex: Enthusiastic, curious, asks questions
- Jordan: Knowledgeable, explains clearly

RULES:
1. NO page numbers, URLs, or citations
2. Use contractions and casual language
3. Natural reactions: \"Oh wow\", \"That's fascinating\"
4. Make 6-8 exchanges total

DOCUMENT:
{content}

OUTPUT FORMAT (JSON only, no other text):
{{
  \"dialogue\": [
    {{\"speaker\": \"Alex\", \"text\": \"Hey everyone! Welcome back...\"}},
    {{\"speaker\": \"Jordan\", \"text\": \"Thanks Alex! Today we're exploring...\"}}
  ]
}}"""
        response = self._query_llm(prompt)
        if not response:
            print("❌ No response from LLM")
            return self._get_fallback_dialogue()
        try:
            response = response.strip()
            if response.startswith("```"):
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1]) if len(lines) > 2 else response
            parsed = json.loads(response)
            if isinstance(parsed, dict) and "dialogue" in parsed:
                dialogue = parsed["dialogue"]
                print(f"✅ Generated {len(dialogue)} dialogue exchanges from structured JSON")
                return dialogue
            elif isinstance(parsed, list):
                print(f"✅ Generated {len(parsed)} dialogue exchanges from array JSON")
                return parsed
        except json.JSONDecodeError:
            # Try to extract JSON array manually
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end > start:
                try:
                    dialogue = json.loads(response[start:end])
                    print(f"✅ Generated {len(dialogue)} dialogue exchanges (extracted) ")
                    return dialogue
                except Exception:
                    pass
        except Exception as e:
            print(f"⚠️  Error parsing dialogue JSON: {e}")
        print("⚠️ Falling back to hard‑coded dialogue template")
        return self._get_fallback_dialogue()

    def _get_fallback_dialogue(self) -> list:
        """Return fallback dialogue template"""
        print("ℹ️  Using fallback dialogue template")
        return [
            {"speaker": "Alex", "text": "Hey everyone! Welcome back. Today we've got something really interesting to dive into, and I'm excited to unpack it with you, Jordan."},
            {"speaker": "Jordan", "text": "Thanks Alex! Yeah, this is fascinating stuff. So the main thing we're looking at here is really about understanding the core concepts and how they apply in real‑world scenarios."},
            {"speaker": "Alex", "text": "Oh that's interesting! Can you break that down a bit more? What makes this approach different?"},
            {"speaker": "Jordan", "text": "Great question! Think of it this way - instead of just throwing information at you, this really helps you connect the dots and see the bigger picture. It's about making those meaningful connections."},
            {"speaker": "Alex", "text": "I love that! And I bet our listeners are already thinking about how they could use this in their own projects or work."},
            {"speaker": "Jordan", "text": "Exactly! That's what makes it so practical. You can actually take these ideas and apply them right away, which is always the goal, right?"},
            {"speaker": "Alex", "text": "Absolutely! This has been such a great conversation. Any final thoughts you want to leave people with?"},
            {"speaker": "Jordan", "text": "Just remember - the key is to start small, experiment, and build from there. Don't be intimidated by the complexity. Take it step by step."},
            {"speaker": "Alex", "text": "Perfect advice! Thanks so much for breaking this down with me today, Jordan. And to everyone listening, we hope this sparked some ideas for you!"},
        ]

    def _elevenlabs_tts(self, text: str, voice_id: str) -> Optional[AudioSegment]:
        """Generate speech using ElevenLabs API"""
        if not self.elevenlabs_api_key:
            return None
        try:
            print("🎤 Attempting ElevenLabs TTS...")
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json",
                        "xi-api-key": self.elevenlabs_api_key,
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_multilingual_v1",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                            "style": 0.5,
                            "use_speaker_boost": True,
                        },
                    },
                )
                if response.status_code == 200:
                    temp_file = self.audio_output_dir / f"temp_elevenlabs_{random.randint(1000,9999)}.mp3"
                    with open(temp_file, "wb") as f:
                        f.write(response.content)
                    audio = AudioSegment.from_mp3(str(temp_file))
                    temp_file.unlink()
                    print("✅ ElevenLabs TTS successful")
                    return audio
                else:
                    print(f"❌ ElevenLabs API returned status {response.status_code}: {response.text[:100]}")
                    return None
        except Exception as e:
            print(f"❌ ElevenLabs error: {str(e)[:100]}")
            return None

    def _google_tts(self, text: str) -> Optional[AudioSegment]:
        """Generate speech using Google Cloud Text‑to‑Speech"""
        try:
            client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Wavenet-D",
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0,
            )
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            temp_file = self.audio_output_dir / f"temp_google_{random.randint(1000,9999)}.mp3"
            with open(temp_file, "wb") as out:
                out.write(response.audio_content)
            audio = AudioSegment.from_mp3(str(temp_file))
            temp_file.unlink()
            return audio
        except Exception as e:
            print(f"❌ Google TTS error: {str(e)[:100]}")
            return None

    def text_to_speech(self, text: str, speaker: str) -> AudioSegment:
        """Convert text to speech – prefer Google Cloud TTS, then ElevenLabs, then gTTS fallback."""
        # 1️⃣ Google Cloud TTS if credentials are set
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            audio = self._google_tts(text)
            if audio:
                print(f"✅ Generated speech for {speaker} using Google Cloud TTS")
                return audio
            else:
                print(f"⚠️ Google Cloud TTS failed for {speaker}, falling back to next option")
        # 2️⃣ ElevenLabs if API key is present
        if self.elevenlabs_api_key:
            if speaker in self.voice_ids:
                audio = self._elevenlabs_tts(text, self.voice_ids[speaker])
                if audio:
                    print(f"✅ Generated speech for {speaker} using ElevenLabs")
                    return audio
                else:
                    print(f"⚠️ ElevenLabs failed for {speaker}, falling back to gTTS")
            else:
                print(f"⚠️ No voice ID for {speaker}, skipping ElevenLabs")
        # 3️⃣ Fallback: gTTS
        print(f"🎤 Generating speech for {speaker} using gTTS (fallback)")
        tts = gTTS(text=text, lang='en', slow=False)
        temp_file = self.audio_output_dir / f"temp_{speaker}_{random.randint(1000,9999)}.mp3"
        tts.save(str(temp_file))
        audio = AudioSegment.from_mp3(str(temp_file))
        # Apply speaker‑specific tweaks
        if speaker == "Jordan":
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 0.95)})
            audio = audio.set_frame_rate(44100)
        else:
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 1.05)})
            audio = audio.set_frame_rate(44100)
        temp_file.unlink()
        return audio

    def create_podcast(
        self,
        document_id: str,
        target_duration: Optional[int] = None,
    ) -> Tuple[str, float, str]:
        """Create podcast audio from document.
        Returns (audio_file_path, duration, transcript)."""
        if target_duration is None:
            target_duration = self.max_duration
        dialogue = self.generate_dialogue(document_id)
        podcast_audio = AudioSegment.silent(duration=500)  # start with half‑second silence
        transcript_parts = []
        for item in dialogue:
            speaker = item.get("speaker", "Alex")
            text = item.get("text", "")
            if not text:
                continue
            transcript_parts.append(f"{speaker}: {text}")
            speech_audio = self.text_to_speech(text, speaker)
            podcast_audio += speech_audio + AudioSegment.silent(duration=800)
        podcast_audio += AudioSegment.silent(duration=500)
        current_duration = len(podcast_audio) / 1000
        if current_duration > target_duration:
            speed_factor = min(current_duration / target_duration, 1.3)
            podcast_audio = speedup(podcast_audio, playback_speed=speed_factor)
        output_filename = f"podcast_{document_id}.mp3"
        output_path = self.audio_output_dir / output_filename
        podcast_audio.export(str(output_path), format="mp3", bitrate="192k")
        final_duration = len(podcast_audio) / 1000
        transcript = "\n\n".join(transcript_parts)
        return str(output_path), final_duration, transcript
