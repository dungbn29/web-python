from flask import Blueprint, render_template, request
import importlib.util
import sys
import os

spec = importlib.util.spec_from_file_location(
    "training_recommend", os.path.join(os.path.dirname(__file__), "..", "ai", "training-recommend.py")
)
training_recommend = importlib.util.module_from_spec(spec)
sys.modules["training_recommend"] = training_recommend
spec.loader.exec_module(training_recommend)
PhoneRecommendationSystem = training_recommend.PhoneRecommendationSystem

recommend_bp = Blueprint("recommend", __name__)

# Khởi tạo hệ thống AI recommendation (chỉ load 1 lần)
recommender = PhoneRecommendationSystem()
recommender.load_classifier(model_dir="phobert_model")

@recommend_bp.route("/recommend", methods=["GET", "POST"])
def recommend():
    results = []
    if request.method == "POST":
        query = request.form["query"]
        # Lấy gợi ý từ AI (PhoBERT + lọc logic)
        results = recommender.recommend_phones(query)
    return render_template("recommend.html", results=results)