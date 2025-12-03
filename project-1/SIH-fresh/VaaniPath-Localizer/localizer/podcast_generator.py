import os
import json
import random
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import httpx
from pydub import AudioSegment

# Set ffmpeg path for pydub (Windows default installation path)
AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"

# Optional Groq import
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

class PodcastGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # API Keys
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        
        # Initialize Groq client if available and key exists
        if GROQ_AVAILABLE and self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
        else:
            self.groq_client = None
        
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
        5. Return ONLY valid JSON array format: [{{ "speaker": "Alex", "text": "..." }}, {{ "speaker": "Jordan", "text": "..." }}]
        
        TEXT:
        {text[:4000]}
        """

        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional podcast script writer."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = chat_completion.choices[0].message.content
            # Handle potential JSON wrapping
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            script = json.loads(content)
            # Ensure it's a list
            if isinstance(script, dict) and "dialogue" in script:
                return script["dialogue"]
            elif isinstance(script, list):
                return script
            else:
                print("❌ Unexpected JSON format from Groq. Using Mock.")
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
                {"speaker": "Alex", "text": "Sahi kaha Jordan. To chaliye bina kisi deri ke shuru karte hain aur gehraai mein jaante hain."},
                {"speaker": "Jordan", "text": "Haan, aur mujhe lagta hai ki iske practical applications bhi kaafi wide hain."},
                {"speaker": "Alex", "text": "Exactly! To doston, dhyaan se suniye aur apne sawaal humein bhejna na bhoolein."}
            ]
        
        return [
            {"speaker": "Alex", "text": "Hey everyone! Welcome back to the show. Today we have a fascinating topic to discuss."},
            {"speaker": "Jordan", "text": "That's right, Alex! I've been reading through this material and it's really mind-blowing."},
            {"speaker": "Alex", "text": "I know, right? The way it breaks down complex concepts into simple ideas is just brilliant."},
            {"speaker": "Jordan", "text": "Absolutely. And I think our listeners are going to find the practical applications really useful."},
            {"speaker": "Alex", "text": "For sure. So let's dive right in and explore the key takeaways!"}
        ]

    async def _generate_audio_segment(self, text: str, speaker: str) -> str:
        """Generate audio for a single segment using ElevenLabs or gTTS."""
        voice_config = self.voices.get(speaker, self.voices["Alex"])
        temp_file = self.output_dir / f"temp_{random.randint(1000, 9999)}.mp3"
        
        # 1. Try ElevenLabs
        if self.elevenlabs_api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_config['elevenlabs_id']}",
                        headers={
                            "xi-api-key": self.elevenlabs_api_key,
                            "Content-Type": "application/json"
                        },
                        json={
                            "text": text,
                            "model_id": "eleven_multilingual_v2",
                            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
                        },
                        timeout=30.0
                    )
                    if response.status_code == 200:
                        with open(temp_file, "wb") as f:
                            f.write(response.content)
                        print(f"✅ Generated audio with ElevenLabs for {speaker}")
                        return str(temp_file)
                    else:
                        print(f"⚠️ ElevenLabs Error ({response.status_code}): {response.text}")
            except Exception as e:
                print(f"⚠️ ElevenLabs Exception: {e}")

        # 2. Fallback to gTTS (Google Text-to-Speech - simpler, no ffmpeg needed)
        try:
            from gtts import gTTS
            # Use different speech rates for different speakers
            slow = (speaker == "Jordan")  # Jordan speaks slightly slower
            tts = gTTS(text=text, lang='en', slow=slow)
            tts.save(str(temp_file))
            print(f"✅ Generated audio with gTTS for {speaker}")
            return str(temp_file)
        except Exception as e:
            print(f"❌ gTTS Error: {e}")
            return None

    async def create_podcast(self, text: str, language: str = "english") -> str:
        """Main method to generate the full podcast."""
        print(f"🎙️ Starting podcast generation for language: {language}")
        
        # 1. Generate Script
        script = await self.generate_script(text, language)
        print(f"📝 Generated script with {len(script)} exchanges")
        
        # 2. Generate Audio Segments
        audio_files = []
        for i, line in enumerate(script):
            print(f"🎤 Generating audio {i+1}/{len(script)}: {line['speaker']}")
            audio_file = await self._generate_audio_segment(line["text"], line["speaker"])
            if audio_file and os.path.exists(audio_file):
                audio_files.append(audio_file)
                print(f"✅ Audio file created: {audio_file}")

        if not audio_files:
            raise Exception("Failed to generate any audio segments")
        
        # 3. Simple solution: Just use the longest audio file for now
        # TODO: Proper merging requires ffmpeg in PATH (restart terminal after installation)
        print(f"📦 Using first audio segment (ffmpeg needed for full merge)")
        
        output_filename = f"podcast_{random.randint(10000, 99999)}.mp3"
        output_path = self.output_dir / output_filename
        
        # Copy the first/longest file
        import shutil
        shutil.copy(audio_files[0], output_path)
        
        # Cleanup temp files
        for f in audio_files:
            try:
                os.remove(f)
            except:
                pass
        
        print(f"✅ Podcast generated: {output_path}")
        return str(output_path)
