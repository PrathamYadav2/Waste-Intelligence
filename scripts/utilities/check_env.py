"""Reports which dataset env vars are set (path presence only). Does NOT list, open or scan any directory."""
import os
for k in ["DATA_ROOT","REALWASTE_PATH","TRASHNET_PATH","TACO_PATH","REGIONAL_DATA_PATH","RECOVERY_GUIDANCE_PATH"]:
    print(f"{k}: {'set' if os.getenv(k) else 'NOT SET'}")
