import os
import subprocess

class VideoPipeline:

    def __init__(self):
        self.output_dir = "generated_videos"
        os.makedirs(self.output_dir, exist_ok=True)

    def create_simple_video(self, script_text, output_name="orion_output.mp4"):
        """
        Turns text into a simple video (placeholder visual + audio-ready container).
        Later we upgrade to real AI visuals.
        """

        output_path = os.path.join(self.output_dir, output_name)

        # Simple colored background video with text overlay
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "lavfi",
            "-i", "color=c=black:s=1280x720:d=10",
            "-vf", f"drawtext=text='{script_text[:120]}':fontcolor=white:fontsize=24:x=50:y=300",
            "-c:v", "libx264",
            "-t", "10",
            output_path
        ]

        subprocess.run(cmd)

        return output_path