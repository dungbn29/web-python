import re
import json
import torch
import joblib
import pandas as pd
from transformers import (
    AutoTokenizer,
    AutoModel,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
import numpy as np

class PhoneRecommendationSystem:
    def __init__(self):
        # Initialize models and data
        self.features_keywords = [
            "camera", "pin", "chơi game", "mượt", "nhỏ gọn", "sạc nhanh",
            "chụp ảnh", "màn hình", "hiệu năng", "thiết kế", "bền bỉ",
            "selfie", "zoom", "chống nước", "âm thanh", "gaming", "flagship"
        ]
        
        # Load phone data
        with open('ai/data/phones_data.json', 'r', encoding='utf-8') as f:
            self.phones_data = json.load(f)
        
        # Initialize PhoBERT components
        self.tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")
        self.model = None
        self.label_encoder = None
    
    def extract_user_query(self, text):
        """Extract budget and features from user query"""
        tokens = text.lower()
        budget = None
        features = []
        
        # Extract budget (e.g., "10 triệu", "5tr", "15-20 triệu")
        money_matches = re.finditer(r"(\d{1,3})(?:\s?-\s?(\d{1,3}))?\s?(?:triệu|tr)", tokens)
        for match in money_matches:
            if match.group(2):  # Range (e.g., 15-20 triệu)
                budget = (int(match.group(1)) * 1_000_000, int(match.group(2)) * 1_000_000)
            else:  # Single value (e.g., 10 triệu)
                budget_val = int(match.group(1)) * 1_000_000
                budget = (budget_val * 0.8, budget_val * 1.2)  # Add some flexibility
        
        # Extract features
        for feat in self.features_keywords:
            if feat in tokens:
                features.append(feat)
        
        # Extract brand preferences
        brands = []
        for phone in self.phones_data:
            brand_lower = phone['brand'].lower()
            if brand_lower in tokens and brand_lower not in brands:
                brands.append(brand_lower)
        
        return budget, features, brands
    
    def train_classifier(self, train_csv_path="ai/data/train_queries_label.csv", model_dir="phobert_model"):
        """Train the PhoBERT classifier on custom data"""
    # 1. Load CSV
        df = pd.read_csv(train_csv_path)
        df = df.dropna()
        texts = df['query'].tolist()
        labels = df['label'].tolist()

    # 2. Encode labels
        self.label_encoder = LabelEncoder()
        encoded_labels = self.label_encoder.fit_transform(labels)
        num_labels = len(self.label_encoder.classes_)
        print("Labels:", self.label_encoder.classes_)

        # 3. Prepare dataset
        class QueryDataset(Dataset):
            def __init__(self, texts, labels, tokenizer, max_length=128):
                self.texts = texts
                self.labels = labels
                self.tokenizer = tokenizer
                self.max_length = max_length
                self.encodings = self.tokenizer(texts, 
                                              padding='max_length', 
                                              truncation=True, 
                                              max_length=self.max_length, 
                                              return_tensors="pt")

            def __getitem__(self, idx):
                item = {key: val[idx] for key, val in self.encodings.items()}
                item['labels'] = torch.tensor(self.labels[idx])
                return item
                
            def __len__(self):
                return len(self.labels)

        # 4. Split dataset
        X_train, X_val, y_train, y_val = train_test_split(texts, encoded_labels, test_size=0.2, random_state=42)

        # Initialize tokenizer with max length
        tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")

        train_dataset = QueryDataset(X_train, y_train, tokenizer)
        val_dataset = QueryDataset(X_val, y_val, tokenizer)

        # 5. Load model
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "vinai/phobert-base", 
            num_labels=num_labels
        )

        # 6. Training setup - fully compatible with transformers 4.51.3
        training_args = TrainingArguments(
            output_dir=model_dir,
            num_train_epochs=5,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            warmup_steps=10,
            weight_decay=0.01,
            logging_dir='./logs',
            save_total_limit=1,
            # load_best_model_at_end=True,  # <-- Bỏ dòng này đi!
            metric_for_best_model="eval_loss",
            logging_steps=10,
            save_steps=500,
            eval_steps=500
)   

        # 7. Metrics
        def compute_metrics(p):
            preds = np.argmax(p.predictions, axis=1)
            acc = (preds == p.label_ids).mean()
            return {"accuracy": acc}

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_metrics
        )

        # 8. Train
        trainer.train()

        # 9. Save
        self.model.save_pretrained(model_dir)
        self.tokenizer.save_pretrained(model_dir)
        joblib.dump(self.label_encoder, f"{model_dir}/label_encoder.pkl")
        print(f"Model trained and saved to {model_dir}")
    
    def load_classifier(self, model_dir="phobert_model"):
        """Load trained classifier"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.label_encoder = joblib.load(f"{model_dir}/label_encoder.pkl")
        print("Classifier loaded successfully")
    
    def predict_phones_from_query(self, query):
        """Predict phones from natural language query using fine-tuned PhoBERT"""
        if not self.model or not self.label_encoder:
            raise ValueError("Classifier not loaded. Please train or load the classifier first.")
        
        # Tokenize input
        inputs = self.tokenizer([query], padding=True, truncation=True, return_tensors="pt")
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            pred = torch.argmax(logits, dim=1).cpu().numpy()[0]
        
        # Get predicted phones
        label = self.label_encoder.inverse_transform([pred])[0]
        phone_names = [x.strip() for x in label.split(",") if x.strip()]
        
        return phone_names
    
    def filter_phones(self, budget=None, features=None, brands=None):
        """Filter phones based on budget and features"""
        filtered_phones = []
        
        for phone in self.phones_data:
            # Check budget
            if budget:
                min_budget, max_budget = budget
                if not (min_budget <= phone['price'] <= max_budget):
                    continue
            
            # Check brand
            if brands:
                if phone['brand'].lower() not in brands:
                    continue
            
            # Check features
            if features:
                match = False
                phone_features = phone['features']
                
                for feat in features:
                    if feat in ["camera", "chụp ảnh"]:
                        if phone_features['camera'] in ["good", "excellent"]:
                            match = True
                            break
                    elif feat in ["pin", "pin trâu"]:
                        if phone_features['battery'] in ["good", "excellent"]:
                            match = True
                            break
                    elif feat in ["chơi game", "gaming"]:
                        if phone_features['performance'] in ["good", "excellent"]:
                            match = True
                            break
                    elif feat == "sạc nhanh":
                        if "sạc nhanh" in phone['description'].lower():
                            match = True
                            break
                    elif feat == "nhỏ gọn":
                        if "nhỏ gọn" in phone['description'].lower() or "mỏng nhẹ" in phone['description'].lower():
                            match = True
                            break
                
                if not match and features:
                    continue
            
            filtered_phones.append(phone)
        
        return filtered_phones
    
    def recommend_phones(self, query):
        """Main recommendation function"""
        # Extract user requirements
        budget, features, brands = self.extract_user_query(query)
        
        # Get predicted phones from classifier
        predicted_phones = self.predict_phones_from_query(query)
        
        # Filter phones based on budget and features
        filtered_phones = self.filter_phones(budget, features, brands)
        
        # Prioritize phones that appear in both predicted and filtered lists
        final_recommendations = []
        other_recommendations = []
        
        for phone in filtered_phones:
            # Check if phone name (lowercase) is in predicted phones (also lowercase)
            phone_name_lower = phone['name'].lower().replace(" ", "")
            predicted_lower = [p.lower().replace(" ", "") for p in predicted_phones]
            
            if any(pred in phone_name_lower for pred in predicted_lower):
                final_recommendations.append(phone)
            else:
                other_recommendations.append(phone)
        
        # Combine results (prioritized first)
        return final_recommendations + other_recommendations
    
    def print_recommendations(self, recommendations, max_results=5):
        """Print recommendations in a user-friendly format"""
        if not recommendations:
            print("Không tìm thấy điện thoại phù hợp với yêu cầu của bạn.")
            return
        
        print(f"\nGợi ý {min(len(recommendations), max_results)} điện thoại phù hợp nhất:")
        for i, phone in enumerate(recommendations[:max_results]):
            print(f"\n{i+1}. {phone['brand']} {phone['name']}")
            print(f"   - Giá: {phone['price']:,.0f} VND")
            print(f"   - Đặc điểm: {phone['description']}")
            
            # Highlight features
            features = []
            if phone['features']['camera'] == "excellent":
                features.append("Camera xuất sắc")
            if phone['features']['battery'] == "excellent":
                features.append("Pin trâu")
            if phone['features']['performance'] == "excellent":
                features.append("Hiệu năng mạnh")
            if features:
                print(f"   - Nổi bật: {', '.join(features)}")


# Example usage
if __name__ == "__main__":
    recommender = PhoneRecommendationSystem()
    
    # Train the classifier (only needed once)
    recommender.train_classifier()
    
    # Load pre-trained classifier
    recommender.load_classifier()
    
    # Get user query
    query = input("Nhập nhu cầu của bạn về điện thoại (ví dụ: 'Tôi cần điện thoại chụp ảnh đẹp giá khoảng 15 triệu'): ")
    
    # Get recommendations
    recommendations = recommender.recommend_phones(query)
    
    # Print results
    recommender.print_recommendations(recommendations)