"""AWS Transcribe（語音轉文字）與 AWS Polly（文字轉語音）。"""
import logging
import time
import uuid

import requests

logger = logging.getLogger(__name__)

TRANSCRIBE_LANGUAGE = "zh-TW"
POLL_INTERVAL_SEC = 2
POLL_TIMEOUT_SEC = 120


class SpeechNotConfigured(RuntimeError):
    pass


class SpeechService:
    def __init__(self, region: str, bucket: str, vocabulary: str, voice_id: str):
        self.region = region
        self.bucket = bucket
        self.vocabulary = vocabulary
        self.voice_id = voice_id

    def _has_aws_credentials(self) -> bool:
        import boto3

        return boto3.Session().get_credentials() is not None

    @property
    def transcribe_available(self) -> bool:
        return bool(self.bucket) and self._has_aws_credentials()

    @property
    def tts_available(self) -> bool:
        return self._has_aws_credentials()

    def transcribe(self, audio: bytes, media_format: str = "webm") -> str:
        if not self.transcribe_available:
            raise SpeechNotConfigured("尚未設定 AWS 憑證或 AWS_S3_BUCKET，請改用文字輸入")

        import boto3

        s3 = boto3.client("s3", region_name=self.region)
        transcribe = boto3.client("transcribe", region_name=self.region)

        job_name = f"nongqing-{uuid.uuid4().hex}"
        key = f"audio/{job_name}.{media_format}"
        s3.put_object(Bucket=self.bucket, Key=key, Body=audio)

        params = {
            "TranscriptionJobName": job_name,
            "LanguageCode": TRANSCRIBE_LANGUAGE,
            "MediaFormat": media_format,
            "Media": {"MediaFileUri": f"s3://{self.bucket}/{key}"},
        }
        if self.vocabulary:
            params["Settings"] = {"VocabularyName": self.vocabulary}
        transcribe.start_transcription_job(**params)

        try:
            deadline = time.monotonic() + POLL_TIMEOUT_SEC
            while time.monotonic() < deadline:
                job = transcribe.get_transcription_job(TranscriptionJobName=job_name)["TranscriptionJob"]
                status = job["TranscriptionJobStatus"]
                if status == "COMPLETED":
                    result = requests.get(job["Transcript"]["TranscriptFileUri"], timeout=10).json()
                    return result["results"]["transcripts"][0]["transcript"]
                if status == "FAILED":
                    raise RuntimeError(job.get("FailureReason", "Transcribe 轉錄失敗"))
                time.sleep(POLL_INTERVAL_SEC)
            raise TimeoutError("Transcribe 轉錄逾時")
        finally:
            s3.delete_object(Bucket=self.bucket, Key=key)

    def synthesize(self, text: str) -> bytes:
        if not self.tts_available:
            raise SpeechNotConfigured("尚未設定 AWS 憑證，無法使用語音播報")

        import boto3

        polly = boto3.client("polly", region_name=self.region)
        resp = polly.synthesize_speech(
            Text=text[:3000], OutputFormat="mp3", VoiceId=self.voice_id, Engine="neural"
        )
        return resp["AudioStream"].read()
