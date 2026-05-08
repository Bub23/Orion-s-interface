import os
import sys
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Add RVC to path
rvc_path = os.path.join(os.path.dirname(__file__), "../../rvc")
if os.path.exists(rvc_path):
    sys.path.insert(0, rvc_path)

try:
    from infer.modules.vc.modules import VC
    from infer.modules.uvr5.modules import uvr
    from configs.config import Config
    RVC_AVAILABLE = True
except ImportError as e:
    logger.warning(f"RVC not available: {e}")
    RVC_AVAILABLE = False


class RVCEngine:
    """Wrapper around RVC voice conversion engine"""
    
    def __init__(self):
        self.vc = None
        self.config = None
        self.uvr_available = False
        
        if RVC_AVAILABLE:
            try:
                self.config = Config()
                self.vc = VC(self.config)
                self.uvr_available = True
                logger.info("RVC engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize RVC: {e}")
    
    def is_ready(self):
        return self.vc is not None and self.uvr_available
    
    def separate_stems(self, input_audio, model_name="HP2", agg=10):
        """
        Separate vocals and instrumental using UVR5
        Returns: (vocals_path, instrumental_path)
        """
        if not self.uvr_available:
            logger.error("UVR5 not available")
            return None, None
        
        try:
            # Create temp output directories
            output_dir = os.path.join("storage/temp", "stem_separation")
            os.makedirs(output_dir, exist_ok=True)
            
            # Run UVR5 separation
            result = uvr(
                model_name=model_name,
                inp=input_audio,
                outp=output_dir,
                agg=agg,
                format0="wav"
            )
            
            # Expected outputs
            vocals_path = os.path.join(output_dir, f"{Path(input_audio).stem}_Vocals.wav")
            instrumental_path = os.path.join(output_dir, f"{Path(input_audio).stem}_Instrumental.wav")
            
            if os.path.exists(vocals_path) and os.path.exists(instrumental_path):
                return vocals_path, instrumental_path
            
            logger.warning("Stem separation output files not found")
            return None, None
            
        except Exception as e:
            logger.error(f"Stem separation failed: {e}")
            return None, None
    
    def voice_convert(self, input_audio, speaker_id=0, f0_method="rmvpe", 
                     pitch_shift=0, index_rate=0.75, filter_radius=3, 
                     resample_sr=0, rms_mix_rate=1, protect=0.33):
        """
        Convert voice using RVC
        Returns: output_audio_path
        """
        if not self.is_ready():
            logger.error("RVC not ready")
            return None
        
        try:
            output_dir = os.path.join("storage/temp", "voice_convert")
            os.makedirs(output_dir, exist_ok=True)
            
            # Get index file
            index_root = os.getenv("index_root", "assets/indices")
            index_files = []
            if os.path.exists(index_root):
                for root, dirs, files in os.walk(index_root):
                    for f in files:
                        if f.endswith(".index"):
                            index_files.append(os.path.join(root, f))
            
            index_file = index_files[0] if index_files else ""
            
            # Run voice conversion
            info, converted_audio = self.vc.vc_single(
                sid=speaker_id,
                input_audio_path=input_audio,
                f0_up_key=pitch_shift,
                f0_method=f0_method,
                file_index=index_file,
                file_big_npy="",
                index_rate=index_rate,
                filter_radius=filter_radius,
                resample_sr=resample_sr,
                rms_mix_rate=rms_mix_rate,
                protect=protect
            )
            
            if converted_audio is not None:
                output_path = os.path.join(output_dir, f"converted_{speaker_id}.wav")
                # Save converted audio
                import soundfile as sf
                sf.write(output_path, converted_audio[1], converted_audio[0])
                return output_path
            
            logger.error(f"Voice conversion failed: {info}")
            return None
            
        except Exception as e:
            logger.error(f"Voice conversion error: {e}")
            return None
    
    def get_trained_voices(self):
        """Get available trained voices"""
        trained_dir = os.getenv("weight_root", "assets/weights")
        voices = []
        
        if os.path.exists(trained_dir):
            for f in os.listdir(trained_dir):
                if f.endswith(".pth"):
                    voices.append(f.replace(".pth", ""))
        
        return voices


# Global instance
rvc_engine = RVCEngine()
