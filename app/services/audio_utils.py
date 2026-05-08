import os
import subprocess
import logging

logger = logging.getLogger(__name__)


def run_cmd(cmd):
    """Safe subprocess execution"""
    try:
        logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            logger.error(result.stderr)
            raise RuntimeError(f"Command failed: {result.stderr}")
        
        return True
    except Exception as e:
        logger.exception("Command failed")
        raise e


def extract_audio_from_video(video_path, output_dir):
    """Extract audio from video file"""
    audio_path = os.path.join(output_dir, "extracted_audio.wav")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        audio_path
    ]
    
    try:
        run_cmd(cmd)
        return audio_path if os.path.exists(audio_path) else None
    except Exception as e:
        logger.error(f"Audio extraction failed: {e}")
        return None


def convert_to_wav(input_path, output_dir):
    """Convert audio to WAV format"""
    output = os.path.join(output_dir, "input.wav")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "44100",
        "-ac", "1",
        output
    ]
    
    try:
        run_cmd(cmd)
        return output
    except Exception as e:
        logger.error(f"WAV conversion failed: {e}")
        return None


def normalize_audio(input_path, output_dir):
    """Normalize audio levels"""
    output = os.path.join(output_dir, "clean.wav")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", "loudnorm",
        output
    ]
    
    try:
        run_cmd(cmd)
        return output
    except Exception as e:
        logger.error(f"Normalization failed: {e}")
        return None


def enhance_audio(input_path, output_dir):
    """Master/enhance audio"""
    output = os.path.join(output_dir, "clean_instrumental_mastered.wav")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", "highpass=f=80,lowpass=f=16000,dynaudnorm=f=250:r=3:n=1:p=0.5",
        output
    ]
    
    try:
        run_cmd(cmd)
        return output
    except Exception as e:
        logger.error(f"Enhancement failed: {e}")
        return None
