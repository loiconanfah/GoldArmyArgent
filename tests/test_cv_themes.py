import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.cv_pdf_generator import generate_cv_pdf, THEMES
import json

sample_cv_data = {
    "full_name": "Antigravity AI",
    "title": "Senior Solutions Architect",
    "email": "antigravity@google.com",
    "phone": "+1 555-0199",
    "location": "Mountain View, CA",
    "linkedin": "linkedin.com/in/antigravity",
    "github": "github.com/google/antigravity",
    "optimization_summary": "Optimized for semantic search using high-density LSI keywords. Reformatted for modern ATS readability.",
    "summary": "Expert AI architect with a track record of implementing high-performance agentic systems. Specialized in neural architecture search and large-scale model orchestration.",
    "experiences": [
        {
            "title": "Lead Agentic Architect",
            "company": "DeepMind",
            "location": "London, UK",
            "start_date": "2023-01",
            "end_date": "Present",
            "bullets": [
                "Led the development of a novel agent orchestration layer boosting task success rate by 45%.",
                "Reduced inference latency by 30% through advanced quantization and model pruning techniques.",
                "Orchestrated cross-functional teams of 20+ researchers and engineers."
            ]
        }
    ],
    "skills": {
        "AI/ML": ["PyTorch", "TensorFlow", "Transformers", "LLMs"],
        "Cloud": ["GCP", "AWS", "Kubernetes", "Docker"]
    },
    "education": [
        {
            "degree": "Ph.D. in Artificial Intelligence",
            "institution": "Stanford University",
            "location": "Stanford, CA",
            "year": "2022"
        }
    ],
    "certifications": ["Google Professional Machine Learning Engineer"],
    "languages": ["English (Native)", "French (Fluent)"]
}

def test_all_themes():
    os.makedirs("test_outputs", exist_ok=True)
    for theme_id in THEMES:
        print(f"Testing theme: {theme_id}...")
        try:
            pdf_bytes = generate_cv_pdf(sample_cv_data, theme_id=theme_id)
            with open(f"test_outputs/cv_{theme_id}.pdf", "wb") as f:
                f.write(pdf_bytes)
            print(f"  Success: Generated test_outputs/cv_{theme_id}.pdf")
        except Exception as e:
            print(f"  Error: Failed to generate theme {theme_id}: {e}")

if __name__ == "__main__":
    test_all_themes()
