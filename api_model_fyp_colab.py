
#setting access to google cloud
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'fyp-api-key.json'

#importing libraries
import moviepy.editor as mp
from google.cloud import storage
from google.cloud import speech
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip


#EXRTRACTING AUDIO FROM INPUT VIDEO
#vid_name = "./static/files/input/tiny.mp4"

def ApiDubVideo(vid_name):
    input_vid = mp.VideoFileClip(vid_name)

    storage_client = storage.Client('fyp-api-key.json')
    my_bucket_name = 'fyp-speech-to-text-files'
    output_aud = 'extractedAudio.mp3'
    output_aud_path = "./static/files/output/"
    input_vid.audio.write_audiofile(output_aud_path+output_aud) 

    #pushing onto bucket
    def upload_to_bucket(file_name,bucket_name):
        upload_file = os.path.join('./static/files/output/', file_name)
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)
        print(blob)
        blob.upload_from_filename(upload_file)

    upload_to_bucket(output_aud, my_bucket_name)
    print('Audio Extracted & Uploaded')

    #RETRIEVING AUDIO FROM BUCKET AND TRANSCRIBING IT
    def get_uri(file_name, bucket_name):
        storage_client = storage.Client()
        blob_name = file_name
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        # print('blob', blob)
        link = blob.path_helper(bucket_name, blob_name)
        # print('link', link)
        #link = blob.path_helper(bucket_name, 'whatever')
        link = link.replace('/o', '')
        return 'gs://' + link

    def transcribe_audio(aud_file,bucket_name):
        media_uri = get_uri(aud_file,bucket_name)

        long_aud_wav = speech.RecognitionAudio(uri = media_uri)

        config_wav_enhanced = speech.RecognitionConfig(
            sample_rate_hertz=48000,
            enable_automatic_punctuation=True,
            use_enhanced=True,
            model='video',
            language_code='en-US'
        )

        speech_client = speech.SpeechClient()

        operation = speech_client.long_running_recognize(
            config = config_wav_enhanced,
            audio=long_aud_wav
        )

        response = operation.result(timeout=90)
        return response

    transcription_list = []
    confidence_list = []
    transcriptions = ''

    response = transcribe_audio(output_aud, my_bucket_name)

    for result in response.results:
        trans = result.alternatives[0].transcript
        transcription_list.append(trans)

    if trans!=None:
        transcriptions += trans

    conf_val = result.alternatives[0].confidence
    confidence_list.append(conf_val)

    #print(transcriptions)
    print('Transcription Done')

    #TEXT TRANSLATION
    def translate_text(target, text):
        import six
        from google.cloud import translate_v2 as translate

        translate_client = translate.Client()

        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")

        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        result = translate_client.translate(text, target_language=target)
        return result["translatedText"]
    
    translated_text = translate_text('ur', transcriptions)
    #print(translated_text)
    print('Translation Done!')

    #TEXT-TO-SPEECH
    dub_audio = gTTS(text=translated_text, lang='ur', slow=False)
    dub_audio.save("./static/files/output/dubAudio.mp3")
    print('Audio Dubbed!')

    #ADDNG DUB AUDIO TO VIDEO
    def addDubAudio(video_file, audio_file):
        video_clip = VideoFileClip(video_file)
        audio_clip = AudioFileClip(audio_file)
        end = video_clip.end
        final_video = video_clip.set_audio(audio_clip)
        final_video.write_videofile("./static/files/results/resultVid.mp4")
        return final_video

    #print(vid_name)
    aud_dub = './static/files/output/dubAudio.mp3'
    addDubAudio(vid_name,aud_dub)
    print('YOUR VIDEO IS READY FOR VIEWING')

#ApiDubVideo(vid_name)
