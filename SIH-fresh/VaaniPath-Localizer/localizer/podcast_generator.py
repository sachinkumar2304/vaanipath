import logging
import json
import base64
import os
import shutil
import random
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import httpx
from pydub import AudioSegment
from elevenlabs.client import ElevenLabs
import groq
import static_ffmpeg
static_ffmpeg.add_paths()

# Removed hardcoded ffmpeg paths allow static_ffmpeg or system path to work
# Constants
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_4aedf5b40a578f6d98e20586d6636d83495580123206dcaf")

class PodcastGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Groq Client
        self.groq_client = None
        if GROQ_API_KEY:
            try:
                self.groq_client = groq.Groq(api_key=GROQ_API_KEY)
            except Exception as e:
                print(f"❌ Failed to initialize Groq: {e}")

        # Initialize ElevenLabs Client
        self.elevenlabs_client = None
        if ELEVENLABS_API_KEY:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            except Exception as e:
                print(f"❌ Failed to initialize ElevenLabs: {e}")

        # Voice Configuration
        self.voices = {
            "Alex": {
                "gender": "male",
                "elevenlabs_id": "pNInz6obpgDQGcFmaJgB", # Adam
                "edge_voice": "en-US-GuyNeural"
            },
            "Jordan": {
                "gender": "female",
                "elevenlabs_id": "21m00Tcm4TlvDq8ikWAM", # Rachel
                "edge_voice": "en-US-JennyNeural"
            }
        }

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extracts text from a PDF file."""
        import PyPDF2
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"❌ Failed to extract text from PDF: {e}")
            return ""

    async def generate_script(self, text: str, language: str) -> List[Dict[str, str]]:
        """Generate a podcast script from text using Groq or Mock fallback."""
        if not self.groq_client:
            print("⚠️ No GROQ_API_KEY found. Using Mock Script.")
            return self._get_mock_script(language)

        prompt = f"""Create a podcast script between two hosts, Alex (Male) and Jordan (Female), based on the following text.
        The podcast should be in {language} language.
        
        RULES:
        1. Natural, conversational tone.
        2. No "Host 1" or "Host 2" labels in text, just the dialogue.
        3. Make it engaging and easy to understand.
        4. Length: 4-6 exchanges.
        5. Return ONLY valid JSON object with a "dialogue" key containing the array: {{ "dialogue": [{{ "speaker": "Alex", "text": "..." }}, {{ "speaker": "Jordan", "text": "..." }}] }}
        
        TEXT:
        {text[:4000]}
        """

        try:
            # Replaced deprecated llama3-8b-8192 with llama-3.3-70b-versatile
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional podcast script writer."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile", 
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = chat_completion.choices[0].message.content
            # Handle potential JSON wrapping
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            print(f"📊 Groq Response Content: {content[:200]}...") # Debug log
            script = json.loads(content)
            
            # Normalize to list
            if isinstance(script, dict):
                # Look for common keys
                if "dialogue" in script:
                    return script["dialogue"]
                elif "script" in script:
                    return script["script"]
                elif "conversation" in script:
                    return script["conversation"]
                # If just random keys, maybe values are the list?
                for key, value in script.items():
                    if isinstance(value, list):
                        return value
            
            if isinstance(script, list):
                return script
                
            print(f"❌ Unexpected JSON structure: {type(script)}. Using Mock.")
            return self._get_mock_script(language)
                
        except Exception as e:
            print(f"❌ Groq Error: {e}. Using Mock.")
            return self._get_mock_script(language)

    def _get_mock_script(self, language: str) -> List[Dict[str, str]]:
        """Return a mock script for testing without API keys."""
        if language.lower() == "hindi":
             return [
                {"speaker": "Alex", "text": "Namaste doston! Aaj hum ek bahut hi dilchasp topic par baat karne wale hain."},
                {"speaker": "Jordan", "text": "Bilkul Alex! Yeh topic sach mein kaafi interesting hai aur hamare listeners ko zaroor pasand aayega."},
                {"speaker": "Alex", "text": "Sahi kaha tumne. Chaliye shuru karte hain aur dekhte hain isme kya khaas hai."},
                {"speaker": "Jordan", "text": "Haan, mujhe yakeen hai ki yeh charcha bahut gyaanvardhak hogi."}
            ]
        else:
            return [
                {"speaker": "Alex", "text": "Hello everyone! Today we are going to discuss a very interesting topic."},
                {"speaker": "Jordan", "text": "Absolutely Alex! This topic is really fascinating and I'm sure our listeners will love it."},
                {"speaker": "Alex", "text": "You're right. Let's dive in and explore what makes it so special."},
                {"speaker": "Jordan", "text": "Yes, I'm confident this discussion will be very enlightening."}
            ]

    async def generate_audio(self, script: List[Dict[str, str]]) -> str:
        """Generate audio for the script using ElevenLabs with gTTS fallback."""
        audio_segments = []
        
        for i, line in enumerate(script):
            speaker = line["speaker"]
            text = line["text"]
            filename = f"segment_{i}_{speaker}.mp3"
            filepath = self.output_dir / filename
            
            # Try ElevenLabs first
            if self.elevenlabs_client:
                try:
                    voice_id = self.voices.get(speaker, {}).get("elevenlabs_id")
                    if voice_id:
                        # Updated code for ElevenLabs v1.0+ SDK
                        audio = self.elevenlabs_client.text_to_speech.convert(
                            text=text,
                            voice_id=voice_id,
                            model_id="eleven_multilingual_v2"
                        )
                        # Save audio
                        with open(filepath, "wb") as f:
                            for chunk in audio:
                                f.write(chunk)
                        audio_segments.append(filepath)
                        continue
                except Exception as e:
                    print(f"⚠️ ElevenLabs failed for {speaker}: {e}. Falling back to gTTS.")

            # Fallback to gTTS
            try:
                from gtts import gTTS
                tts = gTTS(text=text, lang='en', tld='co.in') 
                tts.save(str(filepath))
                audio_segments.append(filepath)
            except Exception as e:
                print(f"❌ gTTS failed for {speaker}: {e}")

        if not audio_segments:
            raise Exception("Failed to generate any audio segments")

        output_filename = f"podcast_final_{random.randint(1000, 9999)}.mp3"
        output_path = self.output_dir / output_filename

        # Try merging with Pydub (requires ffmpeg)
        try:
            combined = AudioSegment.empty()
            silence = AudioSegment.silent(duration=500) 
            for seg_path in audio_segments:
                segment = AudioSegment.from_mp3(str(seg_path))
                combined += segment + silence
            combined.export(str(output_path), format="mp3")
            print("✅ Audio merged using Pydub/FFmpeg")
        except Exception as e:
            print(f"⚠️ Pydub merge failed (likely ffmpeg missing): {e}")
            print("🔄 Falling back to simple file concatenation")
            # Fallback: Simple binary concatenation (works for many MP3 players)
            with open(output_path, 'wb') as outfile:
                for seg_path in audio_segments:
                    with open(seg_path, 'rb') as infile:
                        outfile.write(infile.read())
        
        # Cleanup segments
        for seg_path in audio_segments:
            try:
                os.remove(seg_path)
            except:
                pass
                
        return str(output_path)

    async def create_podcast(self, text: str, language: str) -> str:
        """Orchestrate the podcast creation process."""
        print(f"🎙️ Generating script for language: {language}...")
        script = await self.generate_script(text, language)
        
        print(f"🔊 Synthesizing audio for {len(script)} dialogue lines...")
        audio_path = await self.generate_audio(script)
        
        return audio_path
