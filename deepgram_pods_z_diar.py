import os
from dotenv import load_dotenv
import json
from deep_translator import GoogleTranslator
import requests



from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

load_dotenv()

AUDIO_FILE = "lepsze_nagranie_burzy_mozgow.mp3"

API_KEY = '011a7fb2c1f33a7ff7337bb0ea33104d7424466d'

def translate(source_lang, target_lang, text):

    if len(text) < 5000:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)

    text_list = text.split('.')
    sep_text = ""
    translated_text = ""
    j = 0

    while True:
        while len(sep_text)<4000 and j < len(text_list):
            sep_text += text_list[j]
            j += 1
        translated_text += GoogleTranslator(source=source_lang, target=target_lang).translate(sep_text)
        if sep_text == "":
            return translated_text
        sep_text = ""


def main():
    try:

        deepgram = DeepgramClient(API_KEY)

        with open(AUDIO_FILE, "rb") as file:
            buffer_data = file.read()

        print(len(buffer_data))

        payload: FileSource = {
            "buffer": buffer_data,
            "mimetype": "audio/wav"
        }

        #Tworzenie transkrypcji z diaryzacją poprzez żądanie curl:

            #VIDEO_ID=eHJVOEIw7Jo; yt-dlp ${VIDEO_ID} --extract-audio --audio-format wav -o ${VIDEO_ID}.wav;  \
            #curl https://api.deepgram.com/v1/listen\?punctuate\=true\&language\=pl\&model\=nova\-2\&diarize\=true\&utterances\=true  \
            #-H "Authorization: Token 011a7fb2c1f33a7ff7337bb0ea33104d7424466d" -H "Content-Type: audio/wav" --data-binary @${VIDEO_ID}.wav  \
            #| jq -r ".results.utterances[] | \"[Speaker:\(.speaker)] \(.transcript)\"" > "$VIDEO_ID.txt"; rm "$VIDEO_ID.wav"

        #Tworzenie transkrypcji z diaryzacją poprzez skrypt pythonowy:

        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            language="pl",
            diarize=True,
            punctuate=True,
            utterances=True,
        )
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options, timeout=300)
        utterances = response['results']['utterances']

        transcript_parts = []

        for utterance in utterances:
            transcript_parts.append(f"[Speaker {utterance['speaker']}] {utterance['transcript']}")


        transcript = "\n".join(transcript_parts)
        print(transcript)

        translated = translate('auto', 'en', transcript)
        #print(translated)


        # Generowanie podsumowania:

            # Dane konfiguracyjne

        api_key = '011a7fb2c1f33a7ff7337bb0ea33104d7424466d'
        url = 'https://api.deepgram.com/v1/read?summarize=v2&language=en'
        headers = {
            'Authorization': 'Token ' + api_key,
            'Content-Type': 'application/json',
        }
        data = {
            'text': translated,
        }

            # Wykonanie żądania POST
        response = requests.post(url, headers=headers, data=json.dumps(data))

            # Sprawdzenie odpowiedzi
        if response.status_code == 200:
            response_json = response.json()
            print("Odpowiedź od API:", response_json)
            summary = response_json['results']['summary']['text']
            print(summary)
            translated = translate('auto', 'pl', summary)
            translated = translated.replace("Głośnik", "Mówca")
            print(translated)

        else:
            print("Błąd:", response.text)


    except Exception as e:
        print(f"Exception: {e}")



if __name__ == "__main__":
    main()