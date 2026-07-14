"""
modal_explained.py — annotated version, covering the Modal options
most relevant to your pipeline (TimberVision + CountGD + ArUco,
two-script architecture: extraction -> calculation).

Deploy:   modal deploy modal_explained.py
Test locally without deploying: modal run modal_explained.py
"""

import modal

# =============================================================================
# 1. IMAGE — the container your code runs in (like a Dockerfile, in Python)
# =============================================================================

image = (
    modal.Image.debian_slim(python_version="3.11")

    # apt_install: system packages. opencv needs these or it crashes on import.
    .apt_install("libgl1", "libglib2.0-0")

    # pip_install: same as requirements.txt
    .pip_install(
        "numpy>=1.24.4",
        "scipy>=1.13.0",
        "shapely>=2.0.4",
        "torch==2.3.0",
        "torchvision==0.18.0",
        "ultralytics==8.2.22",
        "opencv-python>=4.9.0",
        "motmetrics>=1.4.0",
        "fastapi[standard]",
        # add CountGD's deps here too
    )

    # run_commands: arbitrary shell, runs once at image build time (cached).
    # good for cloning repos, compiling, or pulling small files.
    .run_commands(
        "git clone https://github.com/timbervision/timbervision.git /opt/timbervision",
    )

    # add_local_dir / add_local_file: pull files from YOUR laptop/repo into
    # the image at build time. Use this for your own extraction/calculation
    # scripts instead of copy-pasting code into this file.
    # .add_local_dir("./pipeline", remote_path="/app/pipeline")
    # .add_local_file("./detect_px_per_mm.py", remote_path="/app/detect_px_per_mm.py")

    # env: set environment variables baked into the image
    # .env({"MODEL_DIR": "/models"})
)

app = modal.App("wood-log-pipeline", image=image)


# =============================================================================
# 2. VOLUME — persistent storage across runs (for model weights / ArUco calib data)
# =============================================================================
# Unlike the image (rebuilt when you change deploy code), a Volume persists
# independently. Good for large checkpoints you don't want re-baked into the
# image every deploy, or for caching downloaded weights on first run.

weights_vol = modal.Volume.from_name("wood-log-weights", create_if_missing=True)
MODEL_DIR = "/models"


# =============================================================================
# 3. SECRETS — API keys / tokens, kept out of your code
# =============================================================================
# Create once via: modal secret create huggingface-token HF_TOKEN=hf_xxx
# Then reference it in a function's `secrets=[...]` — see below.


# =============================================================================
# 4. CLASS-BASED FUNCTION — load the model ONCE, reuse across requests
# =============================================================================
# This matters for you: TimberVision + CountGD are heavy to load. A plain
# @app.function reloads them on every cold start. A class with @modal.enter
# loads them once when the container boots, then every request reuses it —
# much faster for repeated calls while the container stays warm.

@app.cls(
    gpu="T4",                          # match your Kaggle T4 — cheapest GPU tier
    volumes={MODEL_DIR: weights_vol},  # mount the volume at /models
    timeout=120,                       # max seconds per request before it's killed
    scaledown_window=300,              # keep container warm 5 min after last request
                                        # (avoids cold start on back-to-back calls;
                                        # costs a little idle time, worth it if your
                                        # PWA users test repeatedly in a session)
    # secrets=[modal.Secret.from_name("huggingface-token")],
)
class WoodLogPipeline:

    @modal.enter()
    def load_models(self):
        # runs once per container start, NOT per request
        # self.timbervision_model = load_timbervision(f"{MODEL_DIR}/timbervision.pt")
        # self.countgd_model = load_countgd(f"{MODEL_DIR}/countgd.pt")
        pass

    # --- endpoint 1: your extraction script ---
    @modal.fastapi_endpoint(method="POST")
    def extract(self, image_bytes: bytes):
        import cv2
        import numpy as np

        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        # segments = self.timbervision_model(img)
        # count = self.countgd_model(img)
        # px_per_mm = detect_px_per_mm(img)   # your multi-marker update

        return {"segments": [], "count": 0, "px_per_mm": 0.0}

    # --- endpoint 2: your calculation/visualization script ---
    @modal.fastapi_endpoint(method="POST")
    def calculate(self, payload: dict):
        segments = payload.get("segments", [])
        px_per_mm = payload.get("px_per_mm", 0.0)

        # volume_m3 = compute_volume(segments, px_per_mm)
        # mass_kg = volume_m3 * density

        return {"volume_m3": 0.0, "mass_kg": 0.0}


# =============================================================================
# 5. LOCAL ENTRYPOINT — test on Modal's GPU from your terminal, no deploy needed
# =============================================================================
# Run with: modal run modal_explained.py
# Great for iterating on detect_px_per_mm() against a real T4 without
# committing to a full `modal deploy` each time.

@app.local_entrypoint()
def main():
    with open("test_image.jpg", "rb") as f:
        image_bytes = f.read()

    pipeline = WoodLogPipeline()
    result = pipeline.extract.remote(image_bytes)
    print(result)


# =============================================================================
# OTHER OPTIONS YOU MIGHT WANT LATER (not wired in above, for reference)
# =============================================================================
#
# retries=3                    -> auto-retry a failed request (flaky download, etc.)
# concurrency_limit=1          -> cap simultaneous requests per container
#                                  (useful if your GPU can't handle parallel inference)
# min_containers=1             -> keep 1 container always warm, zero cold starts,
#                                  but you pay for idle time — usually not worth it
#                                  for a low-traffic demo
# schedule=modal.Period(...)   -> run a function on a cron schedule
#                                  (e.g. periodic cache warmup)