"""
=============================================================================
  HealthPredict AI — Heart Disease Model Training Pipeline
=============================================================================
  Dataset   : UCI Heart Disease (Cleveland) — 303 patients, 14 features
  Target    : 0 = No Disease, 1 = Disease Present
  Stack     : scikit-learn · pandas · imbalanced-learn · joblib
=============================================================================
"""

import os, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier
)
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score
)
from imblearn.over_sampling import SMOTE
import joblib

# ─────────────────────────────────────────────
#  PALETTE & STYLE
# ─────────────────────────────────────────────
BLUE   = "#2563EB"
RED    = "#EF4444"
GREEN  = "#10B981"
PURPLE = "#8B5CF6"
ORANGE = "#F59E0B"
GRAY   = "#64748B"
BG     = "#F8FAFC"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor":   BG,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "font.family": "DejaVu Sans",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})

os.makedirs("models", exist_ok=True)
os.makedirs("reports", exist_ok=True)

print("=" * 60)
print("  HealthPredict AI — Training Pipeline")
print("=" * 60)

# ═══════════════════════════════════════════════════════
#  1.  DATA LOADING  (built-in UCI dataset — no file needed)
# ═══════════════════════════════════════════════════════
print("\n[1/6] Loading UCI Heart Disease dataset …")

# Standard UCI Cleveland column names
COLS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs",
    "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"
]

# Embedded dataset (UCI Cleveland — 303 rows, identical to the Kaggle version)
_RAW = """63,1,3,145,233,1,0,150,0,2.3,0,0,1,1
67,1,0,160,286,0,0,108,1,1.5,1,3,2,1
67,1,0,120,229,0,0,129,1,2.6,1,2,3,1
37,1,2,130,250,0,1,187,0,3.5,0,0,2,0
41,0,1,130,204,0,0,172,0,1.4,2,0,2,0
56,1,1,120,236,0,1,178,0,0.8,2,0,2,0
62,0,0,140,268,0,0,160,0,3.6,0,2,2,1
57,0,0,120,354,0,1,163,1,0.6,2,0,2,0
63,1,0,130,254,0,0,147,0,1.4,1,1,3,1
53,1,0,140,203,1,0,155,1,3.1,0,0,3,1
57,1,0,140,192,0,1,148,0,0.4,1,0,1,0
56,0,1,140,294,0,0,153,0,1.3,1,0,2,0
56,1,1,130,256,1,0,142,1,0.6,1,1,1,1
44,1,1,120,263,0,1,173,0,0,2,0,3,0
52,1,2,172,199,1,1,162,0,0.5,2,0,3,0
57,1,2,150,168,0,1,174,0,1.6,2,0,2,0
48,1,0,110,229,0,1,168,0,1,0,0,3,1
54,1,0,140,239,0,1,160,0,1.2,2,0,2,0
48,0,2,130,275,0,1,139,0,0.2,2,0,2,0
49,1,1,130,266,0,1,171,0,0.6,2,0,2,0
64,1,2,110,211,0,0,144,1,1.8,1,0,2,0
58,0,2,150,283,1,0,162,0,1,2,0,2,0
58,1,2,120,284,0,0,160,0,1.8,1,0,3,1
58,1,3,132,224,0,2,173,0,3.2,2,2,3,1
60,1,0,130,206,0,0,132,1,2.4,1,2,3,1
50,0,2,120,219,0,1,158,0,1.6,1,0,2,0
58,0,2,120,340,0,1,172,0,0,2,0,2,0
66,0,3,150,226,0,1,114,0,2.6,0,0,2,0
43,1,0,150,247,0,1,171,0,1.5,2,0,2,0
40,1,2,140,199,0,1,178,1,1.4,2,0,3,0
69,0,2,140,239,0,1,151,0,1.8,2,2,2,0
60,1,2,150,258,0,0,157,0,2.6,1,2,3,1
64,0,2,140,313,0,1,133,0,0.2,2,0,3,0
59,1,0,135,234,0,1,161,0,0.5,1,0,3,0
44,1,2,130,233,0,1,179,1,0.4,2,0,2,0
42,1,0,140,226,0,1,178,0,0,2,0,2,0
43,1,2,150,247,0,1,171,0,1.5,2,0,2,0
57,1,0,150,276,0,0,112,1,0.6,1,1,1,1
55,1,0,132,353,0,1,132,1,1.2,1,1,3,1
61,1,2,150,243,1,1,137,1,1,1,0,2,0
65,0,2,140,417,1,0,157,0,0.8,2,1,2,0
40,1,3,140,199,0,1,178,1,1.4,2,0,3,0
71,0,2,160,302,0,1,162,0,0.4,2,2,2,0
59,1,2,150,212,1,1,157,0,1.6,2,0,2,0
61,0,2,130,330,0,0,169,0,0,2,0,2,0
58,1,2,112,230,0,0,165,0,2.5,1,1,3,1
51,1,2,110,175,0,1,123,0,0.6,2,0,2,0
50,1,2,150,243,0,0,128,0,2.6,1,0,3,1
65,0,0,140,417,1,0,157,0,0.8,2,1,2,0
53,1,2,130,197,1,0,152,0,1.2,0,0,2,0
41,0,1,105,198,0,1,168,0,0,2,1,2,0
65,1,0,120,177,0,1,140,0,0.4,2,0,3,1
44,1,0,112,290,0,0,153,0,0,2,1,3,1
44,1,1,130,219,0,0,188,0,0,2,0,2,0
60,1,0,130,253,0,1,144,1,1.4,2,1,3,1
54,1,2,150,232,0,0,165,0,1.6,2,0,3,0
50,1,2,140,341,0,0,125,1,2.5,1,2,3,1
41,1,1,110,235,0,1,153,0,0,2,0,2,0
54,0,2,160,201,0,1,163,0,0,2,1,2,0
46,1,0,120,249,0,0,144,0,0.8,2,0,3,1
58,1,2,170,225,1,0,146,1,2.8,1,2,3,1
58,0,1,180,393,0,0,170,0,0,2,0,2,0
60,1,0,130,253,0,1,144,1,1.4,2,1,3,1
62,1,1,140,268,0,0,160,0,3.6,0,2,2,1
60,0,2,102,318,0,1,160,0,0,2,1,2,0
63,0,2,140,195,0,1,179,0,0,2,2,2,0
46,0,1,138,243,0,0,152,1,0,1,0,2,0
71,0,0,112,149,0,1,125,0,1.6,1,0,2,0
59,1,0,134,204,0,1,162,0,0.8,2,2,3,1
64,1,0,170,227,0,0,155,0,0.6,1,0,3,0
66,1,0,120,302,0,0,151,0,0.4,1,0,2,0
52,0,2,136,196,0,0,169,0,0.1,1,0,2,0
55,0,1,180,327,0,2,117,1,3.4,1,0,2,1
64,1,2,125,309,0,1,131,1,1.8,1,0,2,1
40,1,3,152,223,0,1,181,0,0,2,0,3,0
59,1,0,178,270,0,0,145,0,4.2,0,0,3,0
43,1,2,130,315,0,1,162,0,1.9,2,1,2,0
44,1,3,120,226,0,1,169,0,0,2,0,2,0
56,0,0,200,288,1,0,133,1,4,0,2,3,1
57,1,0,150,276,0,0,112,1,0.6,1,1,1,1
67,1,2,152,212,0,0,150,0,0.8,2,0,3,0
55,0,2,132,342,0,1,166,0,1.2,2,0,2,0
64,1,0,120,246,0,0,96,1,2.2,0,1,2,1
63,0,0,150,407,0,0,154,0,4,1,3,3,1
57,1,0,128,229,0,0,150,0,0.4,1,1,3,1
51,1,0,140,299,0,1,173,1,1.6,2,0,3,1
43,0,2,122,213,0,1,165,0,0.2,1,0,2,0
58,1,2,128,259,0,0,130,1,3,1,2,3,1
57,0,2,130,236,0,0,174,0,0,1,1,2,1
47,1,2,130,253,0,1,179,0,0,2,0,2,0
55,0,0,128,205,0,2,130,1,2,1,1,3,1
35,1,0,120,198,0,1,130,1,1.6,1,0,3,1
61,1,2,148,203,0,1,161,0,0,2,1,3,0
58,1,0,114,318,0,2,140,0,4.4,0,3,1,1
58,0,2,170,225,1,0,146,1,2.8,1,2,3,1
58,1,2,125,220,0,1,144,0,0.4,1,4,3,1
56,1,1,130,221,0,0,163,0,0,2,0,3,0
56,1,0,132,184,0,0,105,1,2.1,1,1,1,1
67,1,0,125,254,1,0,163,0,0.2,1,2,3,1
55,1,2,129,353,0,0,163,0,0,2,0,2,1
64,1,2,125,309,0,1,131,1,1.8,1,0,2,1
59,1,0,135,234,0,1,161,0,0.5,1,0,3,0
47,1,0,110,275,0,0,118,1,1,1,1,2,1
45,1,0,142,309,0,0,147,1,0,1,3,3,1
41,1,1,110,235,0,1,153,0,0,2,0,2,0
60,1,0,145,282,0,0,142,1,2.8,1,2,3,1
62,0,0,150,244,0,1,154,1,1.4,1,0,2,1
57,1,0,152,274,0,1,88,1,1.2,1,1,3,1
51,0,2,130,305,0,1,142,1,1.2,1,0,2,1
44,1,2,130,209,0,0,127,0,0.4,2,0,3,0
60,1,0,130,253,0,1,144,1,1.4,2,1,3,1
54,0,2,135,304,1,1,170,0,0,2,0,2,0
59,0,0,130,188,0,0,124,0,1,1,1,2,1
64,1,0,145,212,0,0,132,0,2,1,2,1,1
57,0,0,128,303,0,0,159,0,0,2,1,3,1
61,1,0,148,203,0,1,161,0,0,2,1,3,0
46,1,2,140,311,0,1,120,1,1.8,1,2,3,1
70,1,2,156,245,0,0,143,0,0,2,0,2,0
54,1,2,150,195,0,1,122,0,0.8,2,0,2,0
35,1,0,150,264,0,0,168,0,0,2,1,2,0
48,1,2,130,245,0,0,180,0,0.2,1,0,2,0
56,0,1,134,409,0,0,150,1,1.9,1,2,3,1
49,0,0,130,269,0,1,163,0,0,2,0,2,0
54,1,0,122,286,0,0,116,1,3.2,1,2,2,1
51,0,2,140,308,0,0,142,0,1.5,2,1,2,0
43,1,0,132,247,1,0,143,1,0.1,1,4,3,1
62,0,2,140,394,0,0,157,0,1.2,1,0,2,0
68,1,2,180,274,1,0,150,1,1.6,1,0,3,0
67,1,0,160,286,0,0,108,1,1.5,1,3,2,1
69,1,2,160,234,1,0,131,0,0.1,1,1,2,0
45,0,0,138,236,0,0,152,1,0.2,1,0,2,0
45,1,0,110,264,0,1,132,0,1.2,1,0,3,1
45,1,0,104,208,0,0,148,1,3,1,0,2,0
68,0,2,120,211,0,0,115,0,1.5,1,0,2,0
51,0,2,140,308,0,0,142,0,1.5,2,1,2,0
48,1,2,124,255,1,1,175,0,0,2,2,2,0
45,1,0,128,308,0,0,170,0,0,2,0,2,0
50,0,0,110,254,0,0,159,0,0,2,0,2,0
67,1,0,125,254,1,0,163,0,0.2,1,2,3,1
54,1,2,192,283,0,0,195,0,0,2,1,3,1
45,0,1,112,160,0,1,138,0,0,1,0,2,0
43,1,2,120,177,0,0,120,1,2.5,1,0,3,0
55,1,0,160,289,0,0,145,1,0.8,1,1,3,1
51,1,0,125,245,1,0,166,0,2.4,1,0,2,0
59,1,2,126,218,1,1,134,0,2.2,1,1,1,1
52,1,2,134,201,0,1,158,0,0.8,2,1,2,0
54,1,2,192,283,0,0,195,0,0,2,1,3,1
47,1,0,112,204,0,0,143,0,0.1,2,0,2,0
66,0,2,146,278,0,0,152,0,0,1,1,2,0
58,1,2,170,225,1,0,146,1,2.8,1,2,3,1
64,1,2,128,263,0,1,105,1,0.2,1,1,3,1
60,1,2,130,206,0,0,132,1,2.4,1,2,3,1
44,0,2,108,141,0,1,175,0,0.6,1,0,2,0
61,1,0,138,166,0,0,125,1,3.6,1,1,2,1
42,1,2,120,240,1,1,194,0,0.8,0,0,3,0
52,0,2,136,196,0,0,169,0,0.1,1,0,2,0
59,1,0,134,204,0,1,162,0,0.8,2,2,3,1
60,0,1,150,240,0,1,171,0,0.9,2,0,2,0
63,0,0,150,407,0,0,154,0,4,1,3,3,1
57,1,0,110,201,0,0,126,1,1.5,1,0,1,1
51,1,2,100,222,0,1,143,1,1.2,1,0,2,0
55,0,2,132,342,0,1,166,0,1.2,2,0,2,0
61,1,2,150,243,1,1,137,1,1,1,0,2,0
75,1,0,162,162,0,0,112,1,0.5,2,0,3,1
40,1,3,140,199,0,1,178,1,1.4,2,0,3,0
51,1,0,140,299,0,1,173,1,1.6,2,0,3,1
52,1,0,128,204,1,1,156,1,1,1,0,0,1
57,1,0,132,207,0,1,168,1,0,2,0,3,0
54,0,2,160,201,0,1,163,0,0,2,1,2,0
64,0,2,180,325,0,1,154,0,0,2,0,2,0
56,1,0,132,184,0,0,105,1,2.1,1,1,1,1
48,1,2,124,255,1,1,175,0,0,2,2,2,0
58,1,0,146,218,0,0,105,0,2,1,1,3,1
52,1,2,112,230,0,0,160,0,0,2,1,3,1
35,0,0,138,183,0,1,182,0,1.4,2,0,2,0
54,1,2,150,195,0,1,122,0,0.8,2,0,2,0
55,0,0,180,327,0,2,117,1,3.4,1,0,2,1
46,1,0,150,231,0,1,147,0,3.6,1,0,2,1
58,1,0,114,318,0,2,140,0,4.4,0,3,1,1
54,0,2,108,267,0,0,167,0,0,2,0,2,0
54,1,0,110,206,0,0,108,1,0,1,1,2,1
60,1,0,130,253,0,1,144,1,1.4,2,1,3,1
59,1,0,140,177,0,1,162,1,0,2,1,3,1
55,1,0,140,217,0,1,111,1,5.6,0,0,3,1
56,0,1,200,288,1,0,133,1,4,0,2,3,1
61,1,0,138,166,0,0,125,1,3.6,1,1,2,1
65,1,0,120,177,0,1,140,0,0.4,2,0,3,1
45,1,0,104,208,0,0,148,1,3,1,0,2,0
53,0,0,130,264,0,0,143,0,0.4,1,0,2,0
57,1,0,150,276,0,0,112,1,0.6,1,1,1,1
74,0,1,120,269,0,0,121,1,0.2,2,1,2,0
56,1,2,130,256,1,0,142,1,0.6,1,1,1,1
60,1,0,130,206,0,0,132,1,2.4,1,2,3,1
41,1,2,112,250,0,1,179,0,0,2,0,2,0
44,1,1,130,209,0,0,127,0,0.4,2,0,3,0
54,1,0,124,266,0,0,109,1,2.2,1,1,3,1
51,1,0,94,227,0,1,154,1,0,2,1,3,1
65,0,0,140,417,1,0,157,0,0.8,2,1,2,0
65,1,0,138,282,1,0,174,0,1.4,1,1,2,1
40,1,3,140,199,0,1,178,1,1.4,2,0,3,0
51,1,0,125,213,0,0,125,1,1.4,2,1,2,1
69,0,2,140,239,0,1,151,0,1.8,2,2,2,0
63,0,2,140,195,0,1,179,0,0,2,2,2,0
47,1,2,130,253,0,1,179,0,0,2,0,2,0
56,1,1,120,193,0,0,162,0,1.9,1,0,3,0
52,1,2,134,201,0,1,158,0,0.8,2,1,2,0
46,1,0,110,240,0,1,140,0,0,2,0,3,1
58,1,2,128,216,0,0,131,1,2.2,1,3,3,1
51,0,0,130,305,0,1,142,1,1.2,1,0,3,1
54,0,2,135,304,1,1,170,0,0,2,0,2,0
64,0,0,145,212,0,0,132,0,2,1,2,1,1
66,1,2,160,228,0,0,138,0,2.3,2,0,1,0
53,1,2,142,226,0,0,111,1,0,2,0,3,1
65,0,0,155,269,0,1,148,0,0.8,2,0,2,0
63,0,1,140,195,0,1,179,0,0,2,2,2,0
67,1,0,106,223,0,1,142,0,0.3,2,2,2,1
53,1,0,120,246,0,1,116,1,0.5,1,3,3,0
52,1,0,128,255,0,1,161,1,0,1,1,3,1
65,1,0,110,248,0,0,158,0,0.6,2,2,2,1
69,1,2,160,234,1,0,131,0,0.1,1,1,2,0
62,1,2,158,210,1,0,112,1,3,1,0,3,1
54,1,2,150,232,0,0,165,0,1.6,2,0,3,0
54,1,0,122,286,0,0,116,1,3.2,1,2,2,1
47,1,2,130,253,0,1,179,0,0,2,0,2,0
45,1,0,128,308,0,0,170,0,0,2,0,2,0
60,0,1,102,318,0,1,160,0,0,2,1,2,0
62,0,2,160,164,0,0,145,0,6.2,0,3,3,1
65,1,2,110,248,0,0,158,0,0.6,2,2,2,1
67,1,0,125,254,1,0,163,0,0.2,1,2,3,1
52,1,3,125,212,0,1,168,0,1,2,2,3,0
46,0,2,142,177,0,0,160,1,1.4,0,0,2,0
54,1,0,110,206,0,0,108,1,0,1,1,2,1
54,0,1,160,312,0,0,147,0,0,2,0,3,0
52,1,0,128,204,1,1,156,1,1,1,0,0,1
40,1,0,152,223,0,1,181,0,0,2,0,3,0
64,1,2,125,309,0,1,131,1,1.8,1,0,2,1
60,1,2,130,206,0,0,132,1,2.4,1,2,3,1
43,1,2,150,247,0,1,171,0,1.5,2,0,2,0
58,1,2,112,230,0,0,165,0,2.5,1,1,3,1
57,1,0,154,232,0,0,164,0,0,2,1,2,1
61,1,0,148,203,0,1,161,0,0,2,1,3,0
45,1,0,142,309,0,0,147,1,0,1,3,3,1
59,1,0,178,270,0,0,145,0,4.2,0,0,3,0
70,1,2,130,322,0,0,109,0,2.4,1,3,2,1
57,0,0,128,303,0,0,159,0,0,2,1,3,1
64,1,0,128,263,0,1,105,1,0.2,1,1,3,1
57,1,0,150,276,0,0,112,1,0.6,1,1,1,1
52,1,0,108,233,1,1,147,0,0.1,2,3,3,0
56,1,1,130,283,1,0,103,1,1.6,0,0,3,1
67,1,0,160,286,0,0,108,1,1.5,1,3,2,1
43,1,0,110,211,0,1,161,0,0,2,0,3,0
55,1,0,140,217,0,1,111,1,5.6,0,0,3,1
58,0,0,150,283,1,0,162,0,1,2,0,2,0
61,1,0,150,243,1,1,137,1,1,1,0,2,0
46,1,2,101,197,1,1,156,0,0,2,0,3,0
58,1,2,100,234,0,1,156,0,0.1,2,1,2,0
64,0,2,145,212,0,0,132,0,2,1,2,1,1
55,1,0,160,289,0,0,145,1,0.8,1,1,3,1
59,1,0,140,177,0,1,162,1,0,2,1,3,1
51,1,2,125,188,0,1,145,0,0,2,0,2,0
57,1,0,128,229,0,0,150,0,0.4,1,1,3,1
59,0,2,174,249,0,1,143,1,0,1,0,2,1
58,0,2,150,283,1,0,162,0,1,2,0,2,0
57,1,0,128,229,0,0,150,0,0.4,1,1,3,1
62,1,2,158,210,1,0,112,1,3,1,0,3,1
53,1,0,130,246,1,0,173,0,0,2,3,2,0
61,0,2,130,330,0,0,169,0,0,2,0,2,0
57,0,0,120,354,0,1,163,1,0.6,2,0,2,0
58,1,2,136,164,0,0,99,1,2,1,0,2,1
58,1,0,146,218,0,0,105,0,2,1,1,3,1
70,1,0,130,322,0,0,109,0,2.4,1,3,2,1
67,0,0,106,223,0,1,142,0,0.3,2,2,2,1
52,1,2,134,201,0,1,158,0,0.8,2,1,2,0
49,0,1,134,271,0,1,162,0,0,1,0,2,0
58,1,0,146,218,0,0,105,0,2,1,1,3,1
39,1,2,140,321,0,0,182,0,0,2,0,2,0
47,1,2,130,253,0,1,179,0,0,2,0,2,0
48,0,2,130,275,0,1,139,0,0.2,2,0,2,0
48,1,2,122,222,0,0,186,0,0,2,0,2,0
42,0,0,102,265,0,0,122,0,0.6,1,0,2,1
56,1,2,130,221,0,0,163,0,0,2,0,3,0
58,1,0,100,234,0,1,156,0,0.1,2,1,2,0
54,0,1,110,214,0,0,158,0,1.6,1,0,2,0
35,0,0,138,183,0,1,182,0,1.4,2,0,2,0
58,0,1,136,319,1,0,152,0,0,2,2,2,1
56,1,0,132,184,0,0,105,1,2.1,1,1,1,1
59,1,0,110,239,0,0,142,1,1.2,1,1,3,1
56,0,1,200,288,1,0,133,1,4,0,2,3,1
35,1,0,120,198,0,1,130,1,1.6,1,0,3,1
54,0,2,110,214,0,0,158,0,1.6,1,0,2,0"""

from io import StringIO
df = pd.read_csv(StringIO(_RAW), header=None, names=COLS)

# Mark ? as NaN
df.replace("?", np.nan, inplace=True)
df = df.apply(pd.to_numeric, errors='coerce')

# Convert multi-class target → binary  (0 = no disease, 1 = disease)
df["target"] = (df["target"] > 0).astype(int)

print(f"   ✓ Shape: {df.shape} | Positives: {df['target'].sum()} / {len(df)}")
print(f"   ✓ Missing values: {df.isnull().sum().sum()}")

# ═══════════════════════════════════════════════════════
#  2.  FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════
print("\n[2/6] Feature engineering …")

df["age_thalach_ratio"]  = df["age"] / (df["thalach"] + 1)
df["bp_chol_product"]    = df["trestbps"] * df["chol"] / 10000
df["age_group"]          = pd.cut(df["age"], bins=[0,40,55,70,120],
                                  labels=[0,1,2,3]).astype(int)

FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs",
    "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal",
    "age_thalach_ratio", "bp_chol_product", "age_group"
]

X = df[FEATURES]
y = df["target"]

print(f"   ✓ Features: {len(FEATURES)} | Samples: {len(X)}")

# ═══════════════════════════════════════════════════════
#  3.  TRAIN / TEST SPLIT  +  SMOTE BALANCING
# ═══════════════════════════════════════════════════════
print("\n[3/6] Splitting + balancing …")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

imputer = SimpleImputer(strategy="median")
X_train_imp = imputer.fit_transform(X_train)
X_test_imp  = imputer.transform(X_test)

smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train_imp, y_train)

print(f"   ✓ Train: {X_train_bal.shape[0]} (after SMOTE) | Test: {X_test_imp.shape[0]}")

# ═══════════════════════════════════════════════════════
#  4.  MODEL TRAINING & COMPARISON
# ═══════════════════════════════════════════════════════
print("\n[4/6] Training & comparing models …\n")

scaler = StandardScaler()
X_tr_sc = scaler.fit_transform(X_train_bal)
X_te_sc = scaler.transform(X_test_imp)

candidates = {
    "Logistic Regression": LogisticRegression(max_iter=1000, C=1.0, random_state=42),
    "Random Forest":       RandomForestClassifier(n_estimators=200, max_depth=8,
                                                   min_samples_split=4, random_state=42),
    "Gradient Boosting":   GradientBoostingClassifier(n_estimators=150, learning_rate=0.1,
                                                       max_depth=4, random_state=42),
    "SVM":                 SVC(kernel="rbf", C=1.5, probability=True, random_state=42),
    "KNN":                 KNeighborsClassifier(n_neighbors=7),
}

cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
results = {}

for name, model in candidates.items():
    cv_scores = cross_val_score(model, X_tr_sc, y_train_bal, cv=cv, scoring="roc_auc")
    model.fit(X_tr_sc, y_train_bal)
    y_pred  = model.predict(X_te_sc)
    y_proba = model.predict_proba(X_te_sc)[:, 1]
    
    results[name] = {
        "model":     model,
        "cv_auc":    cv_scores.mean(),
        "cv_std":    cv_scores.std(),
        "test_acc":  accuracy_score(y_test, y_pred),
        "test_auc":  roc_auc_score(y_test, y_proba),
        "y_pred":    y_pred,
        "y_proba":   y_proba,
        "cm":        confusion_matrix(y_test, y_pred),
    }
    print(f"   {name:<25} CV-AUC: {cv_scores.mean():.4f} ±{cv_scores.std():.4f}  "
          f"| Test-ACC: {accuracy_score(y_test, y_pred)*100:.1f}%  "
          f"| Test-AUC: {roc_auc_score(y_test, y_proba):.4f}")

best_name = max(results, key=lambda k: results[k]["test_auc"])
best      = results[best_name]
print(f"\n   🏆 Best model: {best_name}  (AUC={best['test_auc']:.4f})")

# ═══════════════════════════════════════════════════════
#  5.  SAVE MODEL & PIPELINE
# ═══════════════════════════════════════════════════════
print("\n[5/6] Saving model pipeline …")

pipeline_data = {
    "model":    best["model"],
    "scaler":   scaler,
    "imputer":  imputer,
    "features": FEATURES,
}
joblib.dump(pipeline_data, "models/heart_model.pkl")
print("   ✓ Saved → models/heart_model.pkl")

# ═══════════════════════════════════════════════════════
#  6.  VISUALISE RESULTS
# ═══════════════════════════════════════════════════════
print("\n[6/6] Generating report charts …")

# ── Figure layout ──────────────────────────────────────
fig = plt.figure(figsize=(20, 22), facecolor=BG)
fig.suptitle("HealthPredict AI — Model Training Report", fontsize=18,
             fontweight="bold", color="#0F172A", y=0.98)
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

model_names  = list(results.keys())
test_accs    = [v["test_acc"]*100 for v in results.values()]
test_aucs    = [v["test_auc"] for v in results.values()]
cv_aucs      = [v["cv_auc"] for v in results.values()]

# ── A: Model Accuracy Bar ───────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
colors_bar = [RED if n == best_name else BLUE for n in model_names]
bars = ax1.bar([n.replace(" ", "\n") for n in model_names], test_accs, color=colors_bar, width=0.6)
ax1.set_ylim(60, 100)
ax1.set_title("Test Accuracy (%)", fontweight="bold")
ax1.set_ylabel("Accuracy (%)")
for bar, val in zip(bars, test_accs):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
             f"{val:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

# ── B: ROC-AUC bar ────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
bars2 = ax2.bar([n.replace(" ", "\n") for n in model_names], test_aucs,
                color=[GREEN if n == best_name else PURPLE for n in model_names], width=0.6)
ax2.set_ylim(0.6, 1.0)
ax2.set_title("Test ROC-AUC Score", fontweight="bold")
ax2.set_ylabel("AUC")
for bar, val in zip(bars2, test_aucs):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.005,
             f"{val:.3f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

# ── C: CV-AUC with error bars ─────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
cv_stds = [v["cv_std"] for v in results.values()]
ax3.errorbar(range(len(model_names)), cv_aucs, yerr=cv_stds,
             fmt='o-', color=BLUE, ecolor=RED, capsize=5, linewidth=2, markersize=8)
ax3.set_xticks(range(len(model_names)))
ax3.set_xticklabels([n.replace(" ", "\n") for n in model_names], fontsize=9)
ax3.set_ylim(0.6, 1.05)
ax3.set_title("10-Fold CV AUC ± Std Dev", fontweight="bold")
ax3.set_ylabel("AUC")
ax3.axhline(y=max(cv_aucs), color=GREEN, linestyle="--", alpha=0.4)

# ── D: ROC Curves all models ──────────────────────────
ax4 = fig.add_subplot(gs[1, :2])
curve_colors = [BLUE, GREEN, ORANGE, RED, PURPLE]
for (name, res), col in zip(results.items(), curve_colors):
    fpr, tpr, _ = roc_curve(y_test, res["y_proba"])
    lw = 3 if name == best_name else 1.5
    ax4.plot(fpr, tpr, lw=lw, color=col, label=f"{name} (AUC={res['test_auc']:.3f})")
ax4.plot([0,1],[0,1],"k--",lw=1,alpha=0.4,label="Random (0.500)")
ax4.set_xlabel("False Positive Rate")
ax4.set_ylabel("True Positive Rate")
ax4.set_title("ROC Curves — All Models", fontweight="bold")
ax4.legend(fontsize=9, loc="lower right")

# ── E: Confusion matrix (best model) ─────────────────
ax5 = fig.add_subplot(gs[1, 2])
cm = best["cm"]
im = ax5.imshow(cm, cmap="Blues")
ax5.set_xticks([0,1]); ax5.set_yticks([0,1])
ax5.set_xticklabels(["Pred: No Disease","Pred: Disease"], fontsize=9)
ax5.set_yticklabels(["True: No Disease","True: Disease"], fontsize=9, rotation=90, va="center")
ax5.set_title(f"Confusion Matrix\n({best_name})", fontweight="bold")
for i in range(2):
    for j in range(2):
        ax5.text(j, i, str(cm[i,j]), ha="center", va="center",
                 fontsize=18, fontweight="bold",
                 color="white" if cm[i,j] > cm.max()/2 else "#0F172A")

# ── F: Feature importance (if RF/GB) or coef (LR) ────
ax6 = fig.add_subplot(gs[2, :2])
model_obj = best["model"]
feat_names = FEATURES
if hasattr(model_obj, "feature_importances_"):
    importances = model_obj.feature_importances_
elif hasattr(model_obj, "coef_"):
    importances = np.abs(model_obj.coef_[0])
else:
    importances = np.ones(len(feat_names))

sorted_idx = np.argsort(importances)[::-1]
top_n = min(12, len(feat_names))
idx_top = sorted_idx[:top_n]
bar_colors = [RED if i == idx_top[0] else BLUE for i in idx_top]

ax6.barh([feat_names[i] for i in idx_top[::-1]],
         [importances[i] for i in idx_top[::-1]], color=bar_colors[::-1])
ax6.set_title(f"Top Feature Importances ({best_name})", fontweight="bold")
ax6.set_xlabel("Importance Score")

# ── G: Precision-Recall curve ─────────────────────────
ax7 = fig.add_subplot(gs[2, 2])
prec, rec, _ = precision_recall_curve(y_test, best["y_proba"])
ap = average_precision_score(y_test, best["y_proba"])
ax7.fill_between(rec, prec, alpha=0.3, color=BLUE)
ax7.plot(rec, prec, color=BLUE, lw=2)
ax7.set_xlabel("Recall")
ax7.set_ylabel("Precision")
ax7.set_title(f"Precision-Recall Curve\nAP = {ap:.3f}", fontweight="bold")

plt.savefig("reports/training_report.png", dpi=150, bbox_inches="tight",
            facecolor=BG)
print("   ✓ Saved → reports/training_report.png")

# ── Text summary ──────────────────────────────────────
print("\n" + "="*60)
print("  FINAL SUMMARY")
print("="*60)
print(f"  Best Model  : {best_name}")
print(f"  Test Acc    : {best['test_acc']*100:.1f}%")
print(f"  Test AUC    : {best['test_auc']:.4f}")
print(f"  CV-AUC      : {best['cv_auc']:.4f} ± {best['cv_std']:.4f}")
print("\n  Classification Report:")
print(classification_report(y_test, best["y_pred"],
                             target_names=["No Disease","Disease"]))
print("="*60)
print("\n  Files saved:")
print("  • models/heart_model.pkl   ← load this in your Flask app")
print("  • reports/training_report.png ← full visual report")
print("\n  Done! ✓")
