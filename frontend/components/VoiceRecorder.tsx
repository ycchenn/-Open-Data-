"use client";

import { useRef, useState } from "react";

interface Props {
  onRecorded: (audio: Blob) => void;
  disabled?: boolean;
}

export default function VoiceRecorder({ onRecorded, disabled }: Props) {
  const [recording, setRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);

  async function start() {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      const chunks: Blob[] = [];
      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        onRecorded(new Blob(chunks, { type: "audio/webm" }));
      };
      recorder.start();
      recorderRef.current = recorder;
      setRecording(true);
    } catch {
      setError("無法使用麥克風，請確認瀏覽器權限，或改用下方文字輸入。");
    }
  }

  function stop() {
    recorderRef.current?.stop();
    recorderRef.current = null;
    setRecording(false);
  }

  return (
    <div className="stack" style={{ textAlign: "center" }}>
      <button
        className={`record-btn ${recording ? "recording" : ""}`}
        onClick={recording ? stop : start}
        disabled={disabled}
        aria-label={recording ? "停止錄音" : "開始錄音"}
      >
        {recording ? "⏹" : "🎙️"}
      </button>
      <div className="muted">{recording ? "錄音中，說完請再按一次" : "按下按鈕，說說今天做了什麼農事"}</div>
      {error && <div className="error">{error}</div>}
    </div>
  );
}
