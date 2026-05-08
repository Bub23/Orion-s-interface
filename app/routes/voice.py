import os
import uuid
import logging
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.services.rvc_wrapper import rvc_engine
from app.services.audio_utils import convert_to_wav, normalize_audio, enhance_audio, extract_audio_from_video

voice_bp = Blueprint("voice", __name__)
logger = logging.getLogger(__name__)

UPLOAD_DIR = "storage/uploads"
JOB_DIR = "storage/jobs"
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'ogg', 'mp4', 'mov', 'avi', 'mkv'}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(JOB_DIR, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@voice_bp.route("/transform", methods=["POST"])
def transform_voice():
    """Main voice transformation endpoint"""
    
    if "audio_file" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    file = request.files["audio_file"]
    
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file format"}), 400
    
    job_id = str(uuid.uuid4())
    job_path = os.path.join(JOB_DIR, job_id)
    os.makedirs(job_path, exist_ok=True)
    
    filename = secure_filename(file.filename)
    input_path = os.path.join(job_path, filename)
    file.save(input_path)
    
    try:
        # Extract audio if video
        if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            extracted_audio = extract_audio_from_video(input_path, job_path)
            if not extracted_audio:
                return jsonify({"error": "Failed to extract audio from video"}), 500
            input_path = extracted_audio
        
        # Step 1: Convert to WAV
        wav_path = convert_to_wav(input_path, job_path)
        if not os.path.exists(wav_path):
            return jsonify({"error": "Failed to convert to WAV"}), 500
        
        # Step 2: Normalize
        clean_path = normalize_audio(wav_path, job_path)
        if not os.path.exists(clean_path):
            return jsonify({"error": "Failed to normalize audio"}), 500
        
        # Step 3: Separate stems (vocals/instrumental)
        vocals_path, instrumental_path = rvc_engine.separate_stems(clean_path)
        if not vocals_path or not instrumental_path:
            logger.warning("Stem separation failed, using clean audio as vocals")
            vocals_path = clean_path
            instrumental_path = clean_path
        
        # Step 4: Voice conversion on vocals (brand-voice-1)
        converted_voice_1 = rvc_engine.voice_convert(
            vocals_path,
            speaker_id=0,
            pitch_shift=0,
            index_rate=0.75
        )
        
        # Step 5: Voice conversion on vocals (brand-voice-2)
        converted_voice_2 = rvc_engine.voice_convert(
            vocals_path,
            speaker_id=1,
            pitch_shift=0,
            index_rate=0.75
        )
        
        # Step 6: Master instrumental
        instrumental_mastered = enhance_audio(instrumental_path, job_path)
        
        # Rename outputs to match spec
        outputs = {}
        if os.path.exists(vocals_path):
            os.rename(vocals_path, os.path.join(job_path, "clean_vocals.wav"))
            outputs["clean_vocals"] = f"/static/jobs/{job_id}/clean_vocals.wav"
        
        if os.path.exists(instrumental_path):
            os.rename(instrumental_path, os.path.join(job_path, "clean_instrumental.wav"))
            outputs["clean_instrumental"] = f"/static/jobs/{job_id}/clean_instrumental.wav"
        
        if os.path.exists(instrumental_mastered):
            os.rename(instrumental_mastered, os.path.join(job_path, "clean_instrumental_mastered.wav"))
            outputs["clean_instrumental_mastered"] = f"/static/jobs/{job_id}/clean_instrumental_mastered.wav"
        
        if converted_voice_1 and os.path.exists(converted_voice_1):
            os.rename(converted_voice_1, os.path.join(job_path, "trained_voice_1.wav"))
            outputs["trained_voice_1"] = f"/static/jobs/{job_id}/trained_voice_1.wav"
        
        if converted_voice_2 and os.path.exists(converted_voice_2):
            os.rename(converted_voice_2, os.path.join(job_path, "trained_voice_2.wav"))
            outputs["trained_voice_2"] = f"/static/jobs/{job_id}/trained_voice_2.wav"
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "outputs": outputs
        }), 200
    
    except Exception as e:
        logger.exception(f"Transform failed: {e}")
        return jsonify({"error": str(e)}), 500


@voice_bp.route("/status/<job_id>", methods=["GET"])
def get_status(job_id):
    """Check job status"""
    job_path = os.path.join(JOB_DIR, job_id)
    
    if not os.path.exists(job_path):
        return jsonify({"error": "Job not found"}), 404
    
    files = os.listdir(job_path)
    return jsonify({
        "job_id": job_id,
        "files": files,
        "ready": len(files) > 1
    }), 200
