import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
INDEX_DIR = os.path.join(PROJECT_ROOT, "hr_faiss_index")

HR_POLICY_FILE_1 = os.path.join(DATA_DIR, "HR_Policy_Dataset1.txt")
HR_POLICY_FILE_2 = os.path.join(DATA_DIR, "HR_Policy_Dataset2.txt")

APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")
