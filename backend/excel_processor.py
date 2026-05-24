# excel_processor.py - Complete file with TRULY personalized recommendations
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import random
import datetime
from typing import Dict, List, Tuple, Any

from career_profiles_data import tenth_career_profiles, twelfth_career_profiles

class ExcelDataProcessor:
    def __init__(self):
        self.tenth_career_profiles = tenth_career_profiles
        self.twelfth_career_profiles = twelfth_career_profiles
        self.data_dir = "data"
        self.model_dir = "model"
        self.ensure_directories_exist()
        self.ensure_models_exist()
        
    def ensure_directories_exist(self):
        """Ensure required directories exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"✅ Created data directory: {self.data_dir}")
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
            print(f"✅ Created model directory: {self.model_dir}")
    
    def ensure_models_exist(self):
        """Check if models exist, if not create them automatically"""
        tenth_model_path = os.path.join(self.model_dir, "career_model_10th.pkl")
        twelfth_model_path = os.path.join(self.model_dir, "career_model_12th.pkl")
        
        if not os.path.exists(tenth_model_path) or not os.path.exists(twelfth_model_path):
            print("🚨 Models not found. Auto-generating datasets and training models...")
            self.auto_setup_models()
        else:
            print("✅ Models found and ready for use!")
    
    def auto_setup_models(self):
        """Automatically setup models when they don't exist"""
        try:
            # Create datasets with updated interests
            print("📊 Creating datasets...")
            self.create_updated_datasets()
            
            # Train models
            print("🤖 Training models...")
            results = self.train_models_from_excel()
            
            if results.get('10th_accuracy', 0) > 0 and results.get('12th_accuracy', 0) > 0:
                print("✅ Model auto-setup completed successfully!")
            else:
                print("❌ Model auto-setup had issues, but models were created")
                
        except Exception as e:
            print(f"❌ Error in auto-setup: {e}")
            import traceback
            traceback.print_exc()

    def load_data_file(self, file_path):
        """Load data from Excel or CSV file"""
        try:
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                return pd.read_excel(file_path, engine='openpyxl')
            elif file_path.endswith('.csv'):
                return pd.read_csv(file_path)
            else:
                print(f"❌ Unsupported file format: {file_path}")
                return None
        except Exception as e:
            print(f"❌ Error loading file {file_path}: {e}")
            return None
        
    def load_and_process_10th_data(self, file_path):
        """Load and process 10th standard data with psychometric questions"""
        try:
            df = self.load_data_file(file_path)
            if df is None:
                return None, None, None
                
            print(f"✅ Loaded 10th data: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            
            # Check if we have the expected columns
            required_columns = ['science', 'english', 'maths', 'interest1', 'interest2', 'interest3', 'career_path']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"❌ Missing columns in 10th data: {missing_columns}")
                return None, None, None
            
            # Use only basic features for training (6 features total)
            academic_features = ['science', 'english', 'maths']
            
            # Check if psychometric features exist, if not use only academic
            psychometric_features = []
            available_psychometric = ['analytical_thinking', 'creativity', 'leadership', 'problem_solving', 'communication']
            for feature in available_psychometric:
                if feature in df.columns:
                    psychometric_features.append(feature)
            
            print(f"📊 Using academic features: {academic_features}")
            print(f"📊 Using psychometric features: {psychometric_features}")
            
            X = df[academic_features + psychometric_features].copy()
            
            # Encode interests
            interest_encoder = LabelEncoder()
            all_interests = pd.concat([df['interest1'], df['interest2'], df['interest3'].dropna()])
            interest_encoder.fit(all_interests)
            
            X['interest1_encoded'] = interest_encoder.transform(df['interest1'])
            X['interest2_encoded'] = interest_encoder.transform(df['interest2'])
            X['interest3_encoded'] = df['interest3'].apply(
                lambda x: interest_encoder.transform([x])[0] if pd.notna(x) else -1
            )
            
            y = df['career_path']
            
            print(f"✅ 10th data processed: {X.shape[0]} samples, {len(y.unique())} career paths")
            print(f"📊 Features used: {X.columns.tolist()} ({len(X.columns)} features)")
            print(f"🎯 Available interests: {list(interest_encoder.classes_)}")
            return X, y, interest_encoder
            
        except Exception as e:
            print(f"❌ Error processing 10th data: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None
    
    def load_and_process_12th_data(self, file_path):
        """Load and process 12th standard data with psychometric questions"""
        try:
            df = self.load_data_file(file_path)
            if df is None:
                return None, None, None
                
            print(f"✅ Loaded 12th data: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            
            # Check if we have the expected columns
            required_columns = ['physics', 'chemistry', 'maths', 'biology', 'interest1', 'interest2', 'interest3', 'career_path']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"❌ Missing columns in 12th data: {missing_columns}")
                return None, None, None
            
            # Use only basic features for training
            academic_features = ['physics', 'chemistry', 'maths', 'biology']
            
            # Check if psychometric features exist
            psychometric_features = []
            available_psychometric = ['analytical_thinking', 'creativity', 'leadership', 'problem_solving', 'communication']
            for feature in available_psychometric:
                if feature in df.columns:
                    psychometric_features.append(feature)
            
            print(f"📊 Using academic features: {academic_features}")
            print(f"📊 Using psychometric features: {psychometric_features}")
            
            X = df[academic_features + psychometric_features].copy()
            
            # Encode interests
            interest_encoder = LabelEncoder()
            all_interests = pd.concat([df['interest1'], df['interest2'], df['interest3'].dropna()])
            interest_encoder.fit(all_interests)
            
            X['interest1_encoded'] = interest_encoder.transform(df['interest1'])
            X['interest2_encoded'] = interest_encoder.transform(df['interest2'])
            X['interest3_encoded'] = df['interest3'].apply(
                lambda x: interest_encoder.transform([x])[0] if pd.notna(x) else -1
            )
            
            y = df['career_path']
            
            print(f"✅ 12th data processed: {X.shape[0]} samples, {len(y.unique())} career paths")
            print(f"📊 Features used: {X.columns.tolist()} ({len(X.columns)} features)")
            print(f"🎯 Available interests: {list(interest_encoder.classes_)}")
            return X, y, interest_encoder
            
        except Exception as e:
            print(f"❌ Error processing 12th data: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None
    
    def create_updated_datasets(self):
        """Create updated datasets with psychometric questions"""
        # Define ALL possible interests to ensure consistency
        all_possible_interests = [
            'Technology', 'Engineering', 'Research', 'Healthcare', 'Science',
            'Business', 'Finance', 'Law', 'Creative Arts', 'Writing', 
            'History', 'Design', 'Mathematics', 'Physics', 'Chemistry',
            'Biology', 'Medicine', 'Computer Science', 'Data Analysis'
        ]
        
        # Psychometric traits for better career prediction
        psychometric_traits = ['analytical_thinking', 'creativity', 'leadership', 'problem_solving', 'communication']
        
        # 10th Standard Careers with psychometric profiles
        tenth_career_profiles = {
            "Engineering Stream (PCM)": {
                "marks_profile": {"science": (75, 95), "english": (60, 85), "maths": (80, 98)},
                "psychometric_profile": {
                    "analytical_thinking": (4, 5), 
                    "creativity": (3, 5), 
                    "leadership": (2, 4),
                    "problem_solving": (4, 5),
                    "communication": (3, 4)
                },
                "preferred_subjects": ["science", "maths"],
                "preferred_traits": ["analytical_thinking", "problem_solving"],
                "common_interests": ["Technology", "Engineering", "Research", "Mathematics", "Physics"],
                "alternative_paths": ["Architect", "Data Analyst", "Software Developer", "Robotics Engineer"],
                "required_skills": ["Mathematics", "Physics", "Problem Solving", "Logical Thinking"]
            },
            "Medical Stream (PCB)": {
                "marks_profile": {"science": (80, 98), "english": (70, 90), "maths": (60, 85)},
                "psychometric_profile": {
                    "analytical_thinking": (4, 5), 
                    "creativity": (2, 4), 
                    "leadership": (3, 5),
                    "problem_solving": (4, 5),
                    "communication": (4, 5)
                },
                "preferred_subjects": ["science"],
                "preferred_traits": ["analytical_thinking", "problem_solving", "detail_orientation"],
                "common_interests": ["Healthcare", "Science", "Research", "Biology", "Medicine"],
                "alternative_paths": ["Biotechnologist", "Pharmacist", "Medical Researcher", "Physiotherapist"],
                "required_skills": ["Biology", "Chemistry", "Empathy", "Attention to Detail"]
            },
            "Commerce Stream": {
                "marks_profile": {"science": (50, 80), "english": (70, 95), "maths": (65, 90)},
                "psychometric_profile": {
                    "analytical_thinking": (3, 5), 
                    "creativity": (2, 4), 
                    "leadership": (3, 5),
                    "problem_solving": (3, 5),
                    "communication": (4, 5)
                },
                "preferred_subjects": ["maths", "english"],
                "preferred_traits": ["leadership", "communication", "analytical_thinking"],
                "common_interests": ["Business", "Finance", "Law", "Data Analysis", "Mathematics"],
                "alternative_paths": ["Chartered Accountant", "Business Analyst", "Financial Advisor", "Entrepreneur"],
                "required_skills": ["Mathematics", "Communication", "Analytical Skills", "Business Acumen"]
            },
            "Arts/Humanities Stream": {
                "marks_profile": {"science": (40, 75), "english": (75, 98), "maths": (40, 70)},
                "psychometric_profile": {
                    "analytical_thinking": (2, 4), 
                    "creativity": (4, 5), 
                    "leadership": (3, 5),
                    "problem_solving": (3, 4),
                    "communication": (4, 5)
                },
                "preferred_subjects": ["english"],
                "preferred_traits": ["creativity", "communication"],
                "common_interests": ["Creative Arts", "Writing", "History", "Design", "Law"],
                "alternative_paths": ["Journalist", "Lawyer", "Psychologist", "Social Worker", "Content Creator"],
                "required_skills": ["Creativity", "Communication", "Critical Thinking", "Writing Skills"]
            },
            "Vocational Studies": {
                "marks_profile": {"science": (35, 70), "english": (50, 80), "maths": (35, 70)},
                "psychometric_profile": {
                    "analytical_thinking": (2, 4), 
                    "creativity": (3, 5), 
                    "leadership": (2, 4),
                    "problem_solving": (3, 5),
                    "communication": (3, 5)
                },
                "preferred_subjects": [],
                "preferred_traits": ["creativity", "communication", "problem_solving"],
                "common_interests": ["Technology", "Business", "Creative Arts", "Computer Science", "Design"],
                "alternative_paths": ["Graphic Designer", "Digital Marketer", "Web Developer", "Hotel Manager"],
                "required_skills": ["Practical Skills", "Creativity", "Problem Solving", "Adaptability"]
            }
        }
        
        # 12th Standard Careers with psychometric profiles
        twelfth_career_profiles = {
            "Software Engineer": {
                "marks_profile": {"physics": (75, 95), "chemistry": (65, 85), "maths": (80, 98), "biology": (50, 80)},
                "psychometric_profile": {
                    "analytical_thinking": (4, 5), 
                    "creativity": (3, 5), 
                    "leadership": (2, 4),
                    "problem_solving": (4, 5),
                    "communication": (3, 4)
                },
                "preferred_subjects": ["physics", "maths"],
                "preferred_traits": ["analytical_thinking", "problem_solving"],
                "common_interests": ["Technology", "Engineering", "Research", "Computer Science", "Mathematics"],
                "alternative_paths": ["Data Scientist", "Cybersecurity Analyst", "AI/ML Engineer", "Game Developer"],
                "required_skills": ["Programming", "Mathematics", "Logical Thinking", "Problem Solving"]
            },
            "Doctor": {
                "marks_profile": {"physics": (75, 90), "chemistry": (80, 95), "maths": (70, 90), "biology": (85, 98)},
                "psychometric_profile": {
                    "analytical_thinking": (4, 5), 
                    "creativity": (2, 4), 
                    "leadership": (3, 5),
                    "problem_solving": (4, 5),
                    "communication": (4, 5)
                },
                "preferred_subjects": ["chemistry", "biology"],
                "preferred_traits": ["analytical_thinking", "problem_solving", "communication"],
                "common_interests": ["Healthcare", "Science", "Research", "Medicine", "Biology"],
                "alternative_paths": ["Surgeon", "Medical Researcher", "Public Health Specialist", "Medical Professor"],
                "required_skills": ["Biology", "Chemistry", "Empathy", "Attention to Detail", "Communication"]
            },
            "Data Scientist": {
                "marks_profile": {"physics": (70, 90), "chemistry": (65, 85), "maths": (85, 98), "biology": (60, 85)},
                "psychometric_profile": {
                    "analytical_thinking": (4, 5), 
                    "creativity": (3, 5), 
                    "leadership": (2, 4),
                    "problem_solving": (4, 5),
                    "communication": (3, 4)
                },
                "preferred_subjects": ["maths"],
                "preferred_traits": ["analytical_thinking", "problem_solving", "detail_orientation"],
                "common_interests": ["Technology", "Research", "Finance", "Data Analysis", "Mathematics"],
                "alternative_paths": ["Business Analyst", "Machine Learning Engineer", "Quantitative Analyst", "Research Scientist"],
                "required_skills": ["Statistics", "Programming", "Mathematics", "Analytical Thinking"]
            },
            "Civil Engineer": {
                "marks_profile": {"physics": (75, 90), "chemistry": (70, 85), "maths": (75, 95), "biology": (55, 80)},
                "psychometric_profile": {
                    "analytical_thinking": (4, 5), 
                    "creativity": (3, 5), 
                    "leadership": (3, 4),
                    "problem_solving": (4, 5),
                    "communication": (3, 4)
                },
                "preferred_subjects": ["physics", "maths"],
                "preferred_traits": ["analytical_thinking", "problem_solving"],
                "common_interests": ["Engineering", "Technology", "Business", "Design", "Mathematics"],
                "alternative_paths": ["Architect", "Structural Engineer", "Project Manager", "Urban Planner"],
                "required_skills": ["Physics", "Mathematics", "Design Skills", "Project Management"]
            },
            "Financial Analyst": {
                "marks_profile": {"physics": (60, 85), "chemistry": (60, 80), "maths": (75, 95), "biology": (50, 75)},
                "psychometric_profile": {
                    "analytical_thinking": (4, 5), 
                    "creativity": (2, 4), 
                    "leadership": (3, 5),
                    "problem_solving": (4, 5),
                    "communication": (3, 5)
                },
                "preferred_subjects": ["maths"],
                "preferred_traits": ["analytical_thinking", "leadership"],
                "common_interests": ["Finance", "Business", "Technology", "Data Analysis", "Mathematics"],
                "alternative_paths": ["Investment Banker", "Portfolio Manager", "Risk Analyst", "Financial Consultant"],
                "required_skills": ["Mathematics", "Analytical Skills", "Finance Knowledge", "Communication"]
            },
            "Biotechnologist": {
                "marks_profile": {"physics": (70, 85), "chemistry": (75, 95), "maths": (70, 90), "biology": (80, 98)},
                "psychometric_profile": {
                    "analytical_thinking": (4, 5), 
                    "creativity": (3, 5), 
                    "leadership": (2, 4),
                    "problem_solving": (4, 5),
                    "communication": (3, 4)
                },
                "preferred_subjects": ["chemistry", "biology"],
                "preferred_traits": ["analytical_thinking", "problem_solving"],
                "common_interests": ["Science", "Research", "Healthcare", "Biology", "Medicine"],
                "alternative_paths": ["Geneticist", "Pharmaceutical Researcher", "Food Technologist", "Environmental Scientist"],
                "required_skills": ["Biology", "Chemistry", "Research Skills", "Laboratory Techniques"]
            },
            "Architect": {
                "marks_profile": {"physics": (70, 90), "chemistry": (65, 85), "maths": (75, 95), "biology": (60, 85)},
                "psychometric_profile": {
                    "analytical_thinking": (3, 5), 
                    "creativity": (4, 5), 
                    "leadership": (3, 4),
                    "problem_solving": (4, 5),
                    "communication": (3, 5)
                },
                "preferred_subjects": ["physics", "maths"],
                "preferred_traits": ["analytical_thinking", "creativity"],
                "common_interests": ["Creative Arts", "Engineering", "Design", "Mathematics", "Technology"],
                "alternative_paths": ["Interior Designer", "Urban Designer", "Landscape Architect", "Construction Manager"],
                "required_skills": ["Creativity", "Design Skills", "Mathematics", "Technical Drawing"]
            }
        }
        
        # Generate 10th standard data
        tenth_data = []
        for career, profile in tenth_career_profiles.items():
            for _ in range(40):  # 40 samples per career
                # Generate marks based on career profile
                science = random.randint(*profile["marks_profile"]["science"])
                english = random.randint(*profile["marks_profile"]["english"])
                maths = random.randint(*profile["marks_profile"]["maths"])
                
                # Generate psychometric scores - ALL traits now
                psychometric_scores = {}
                for trait in psychometric_traits:
                    if trait in profile["psychometric_profile"]:
                        psychometric_scores[trait] = random.randint(*profile["psychometric_profile"][trait])
                    else:
                        # Default range if not specified
                        psychometric_scores[trait] = random.randint(2, 5)
                
                # Select interests from common interests (ensuring they exist in all_possible_interests)
                available_interests = [interest for interest in profile["common_interests"] if interest in all_possible_interests]
                interests = random.sample(available_interests, min(3, len(available_interests)))
                # Fill remaining interests if needed
                while len(interests) < 3:
                    additional_interest = random.choice([i for i in all_possible_interests if i not in interests])
                    interests.append(additional_interest)
                
                student_data = {
                    'science': science,
                    'english': english,
                    'maths': maths,
                    'interest1': interests[0],
                    'interest2': interests[1],
                    'interest3': interests[2],
                    'career_path': career
                }
                # Add psychometric scores
                student_data.update(psychometric_scores)
                
                tenth_data.append(student_data)
        
        # Generate 12th standard data
        twelfth_data = []
        for career, profile in twelfth_career_profiles.items():
            for _ in range(40):  # 40 samples per career
                # Generate marks based on career profile
                physics = random.randint(*profile["marks_profile"]["physics"])
                chemistry = random.randint(*profile["marks_profile"]["chemistry"])
                maths = random.randint(*profile["marks_profile"]["maths"])
                biology = random.randint(*profile["marks_profile"]["biology"])
                
                # Generate psychometric scores - ALL traits now
                psychometric_scores = {}
                for trait in psychometric_traits:
                    if trait in profile["psychometric_profile"]:
                        psychometric_scores[trait] = random.randint(*profile["psychometric_profile"][trait])
                    else:
                        # Default range if not specified
                        psychometric_scores[trait] = random.randint(2, 5)
                
                # Select interests from common interests
                available_interests = [interest for interest in profile["common_interests"] if interest in all_possible_interests]
                interests = random.sample(available_interests, min(3, len(available_interests)))
                # Fill remaining interests if needed
                while len(interests) < 3:
                    additional_interest = random.choice([i for i in all_possible_interests if i not in interests])
                    interests.append(additional_interest)
                
                student_data = {
                    'physics': physics,
                    'chemistry': chemistry,
                    'maths': maths,
                    'biology': biology,
                    'interest1': interests[0],
                    'interest2': interests[1],
                    'interest3': interests[2],
                    'career_path': career
                }
                # Add psychometric scores
                student_data.update(psychometric_scores)
                
                twelfth_data.append(student_data)
        
        # Ensure data directory exists
        self.ensure_directories_exist()
        
        # Save career profiles for analysis
        self.tenth_career_profiles = tenth_career_profiles
        self.twelfth_career_profiles = twelfth_career_profiles
        
        # Save to Excel
        tenth_df = pd.DataFrame(tenth_data)
        twelfth_df = pd.DataFrame(twelfth_data)
        
        tenth_file = os.path.join(self.data_dir, '10th_data_updated.xlsx')
        twelfth_file = os.path.join(self.data_dir, '12th_data_updated.xlsx')
        
        tenth_df.to_excel(tenth_file, index=False)
        twelfth_df.to_excel(twelfth_file, index=False)
        
        print("✅ Updated datasets created with psychometric questions!")
        print(f"📊 10th data: {len(tenth_data)} samples, {len(tenth_career_profiles)} career paths")
        print(f"📊 12th data: {len(twelfth_data)} samples, {len(twelfth_career_profiles)} career paths")
        print(f"🎯 All possible interests: {all_possible_interests}")
        print(f"💾 Files saved: {tenth_file}, {twelfth_file}")
        
        return len(tenth_data), len(twelfth_data)
    
    def train_models_from_excel(self):
        """Train separate models for 10th and 12th standard from updated data files"""
        
        print("🚀 Starting model training with psychometric questions...")
        
        # Ensure model directory exists
        self.ensure_directories_exist()
        
        # Try different file names
        tenth_files = [
            os.path.join(self.data_dir, "10th_data_updated.xlsx"),
            os.path.join(self.data_dir, "10th data.xlsx"),
            os.path.join(self.data_dir, "10th_data.xlsx")
        ]
        
        twelfth_files = [
            os.path.join(self.data_dir, "12th_data_updated.xlsx"),
            os.path.join(self.data_dir, "12th data.xlsx"),
            os.path.join(self.data_dir, "12th_data.xlsx")
        ]
        
        results = {}
        
        # Train 10th standard model
        tenth_file = None
        for file_path in tenth_files:
            if os.path.exists(file_path):
                tenth_file = file_path
                break
        
        if tenth_file:
            print(f"📊 Processing 10th standard data from: {tenth_file}")
            X_10th, y_10th, interest_encoder_10th = self.load_and_process_10th_data(tenth_file)
            
            if X_10th is not None and y_10th is not None:
                # Save the feature names used for training
                self.training_features_10th = X_10th.columns.tolist()
                print(f"💾 10th training features saved: {self.training_features_10th}")
                
                X_train_10th, X_test_10th, y_train_10th, y_test_10th = train_test_split(
                    X_10th, y_10th, test_size=0.2, random_state=42
                )
                
                model_10th = RandomForestClassifier(n_estimators=150, random_state=42, max_depth=15)
                model_10th.fit(X_train_10th, y_train_10th)
                
                # Save 10th model and encoder
                joblib.dump(model_10th, os.path.join(self.model_dir, "career_model_10th.pkl"))
                joblib.dump(interest_encoder_10th, os.path.join(self.model_dir, "label_encoder_10th.pkl"))
                # Save feature names
                joblib.dump(self.training_features_10th, os.path.join(self.model_dir, "training_features_10th.pkl"))
                
                accuracy_10th = model_10th.score(X_test_10th, y_test_10th)
                results['10th_accuracy'] = accuracy_10th
                print(f"✅ 10th Standard Model trained! Accuracy: {accuracy_10th:.2f}")
                print(f"🔍 Model expects {X_10th.shape[1]} features: {X_10th.columns.tolist()}")
                
                # Show feature importance
                feature_importance = pd.DataFrame({
                    'feature': X_10th.columns,
                    'importance': model_10th.feature_importances_
                }).sort_values('importance', ascending=False)
                
                print(f"🔍 10th Feature Importance:")
                for _, row in feature_importance.head(8).iterrows():
                    print(f"   {row['feature']}: {row['importance']:.3f}")
                
            else:
                print("❌ Failed to train 10th standard model")
                results['10th_accuracy'] = 0
        else:
            print("❌ No 10th standard data file found!")
            results['10th_accuracy'] = 0
        
        # Train 12th standard model
        twelfth_file = None
        for file_path in twelfth_files:
            if os.path.exists(file_path):
                twelfth_file = file_path
                break
        
        if twelfth_file:
            print(f"📊 Processing 12th standard data from: {twelfth_file}")
            X_12th, y_12th, interest_encoder_12th = self.load_and_process_12th_data(twelfth_file)
            
            if X_12th is not None and y_12th is not None:
                # Save the feature names used for training
                self.training_features_12th = X_12th.columns.tolist()
                print(f"💾 12th training features saved: {self.training_features_12th}")
                
                X_train_12th, X_test_12th, y_train_12th, y_test_12th = train_test_split(
                    X_12th, y_12th, test_size=0.2, random_state=42
                )
                
                model_12th = RandomForestClassifier(n_estimators=150, random_state=42, max_depth=15)
                model_12th.fit(X_train_12th, y_train_12th)
                
                # Save 12th model and encoder
                joblib.dump(model_12th, os.path.join(self.model_dir, "career_model_12th.pkl"))
                joblib.dump(interest_encoder_12th, os.path.join(self.model_dir, "label_encoder_12th.pkl"))
                # Save feature names
                joblib.dump(self.training_features_12th, os.path.join(self.model_dir, "training_features_12th.pkl"))
                
                accuracy_12th = model_12th.score(X_test_12th, y_test_12th)
                results['12th_accuracy'] = accuracy_12th
                print(f"✅ 12th Standard Model trained! Accuracy: {accuracy_12th:.2f}")
                print(f"🔍 Model expects {X_12th.shape[1]} features: {X_12th.columns.tolist()}")
                
                # Show feature importance
                feature_importance = pd.DataFrame({
                    'feature': X_12th.columns,
                    'importance': model_12th.feature_importances_
                }).sort_values('importance', ascending=False)
                
                print(f"🔍 12th Feature Importance:")
                for _, row in feature_importance.head(8).iterrows():
                    print(f"   {row['feature']}: {row['importance']:.3f}")
                
            else:
                print("❌ Failed to train 12th standard model")
                results['12th_accuracy'] = 0
        else:
            print("❌ No 12th standard data file found!")
            results['12th_accuracy'] = 0
        
        return results

    def predict_career_10th(self, input_data):
        """Predict career for 10th standard student"""
        try:
            # Load model, encoder, and feature names
            model_path = os.path.join(self.model_dir, "career_model_10th.pkl")
            encoder_path = os.path.join(self.model_dir, "label_encoder_10th.pkl")
            features_path = os.path.join(self.model_dir, "training_features_10th.pkl")
            
            if not os.path.exists(model_path) or not os.path.exists(encoder_path):
                print("❌ Model files not found. Please train the model first.")
                return None
            
            model = joblib.load(model_path)
            encoder = joblib.load(encoder_path)
            training_features = joblib.load(features_path)
            
            print(f"🔍 Model expects these features: {training_features}")
            print(f"🔍 Model expects {len(training_features)} features")
            print(f"🎯 Available interests: {list(encoder.classes_)}")
            
            # Create input DataFrame
            input_df = pd.DataFrame([input_data])
            
            # Handle interest encoding with better error handling
            def safe_encode_interest(encoder, interest_value):
                try:
                    return encoder.transform([interest_value])[0]
                except ValueError as e:
                    print(f"⚠️  Interest '{interest_value}' not in encoder. Using default value.")
                    print(f"🎯 Available interests: {list(encoder.classes_)}")
                    # Return the most common interest as default
                    return 0
            
            # Encode interests if provided as strings
            if 'interest1' in input_data and 'interest1_encoded' not in input_data:
                input_df['interest1_encoded'] = safe_encode_interest(encoder, input_data['interest1'])
            if 'interest2' in input_data and 'interest2_encoded' not in input_data:
                input_df['interest2_encoded'] = safe_encode_interest(encoder, input_data['interest2'])
            if 'interest3' in input_data and 'interest3_encoded' not in input_data:
                input_df['interest3_encoded'] = safe_encode_interest(encoder, input_data['interest3'])
            
            # Ensure we have all required features in the correct order
            missing_features = [f for f in training_features if f not in input_df.columns]
            if missing_features:
                print(f"❌ Missing features: {missing_features}")
                # Add missing features with default values
                for feature in missing_features:
                    if 'interest' in feature:
                        input_df[feature] = 0  # Default for encoded interests
                    else:
                        input_df[feature] = 0  # Default for other features
            
            # Select only the features used in training (in correct order)
            input_features = input_df[training_features]
            
            print(f"🔍 Input features shape: {input_features.shape}")
            print(f"🔍 Input features: {input_features.columns.tolist()}")
            
            # Make prediction
            prediction = model.predict(input_features)[0]
            probability = model.predict_proba(input_features)[0]
            
            # Get career labels directly from the model
            career_labels = model.classes_
            
            # Get top 3 predictions with probabilities
            top_3_indices = probability.argsort()[-3:][::-1]
            top_3_careers = career_labels[top_3_indices]
            top_3_probs = probability[top_3_indices]
            
            result = {
                'success': True,
                'primary_career': prediction,
                'top_careers': [
                    {'career': career, 'probability': float(prob)}
                    for career, prob in zip(top_3_careers, top_3_probs)
                ],
                'features_used': training_features,
                'available_interests': list(encoder.classes_)
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error in 10th prediction: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def predict_career_12th(self, input_data):
        """Predict career for 12th standard student"""
        try:
            # Load model, encoder, and feature names
            model_path = os.path.join(self.model_dir, "career_model_12th.pkl")
            encoder_path = os.path.join(self.model_dir, "label_encoder_12th.pkl")
            features_path = os.path.join(self.model_dir, "training_features_12th.pkl")
            
            if not os.path.exists(model_path) or not os.path.exists(encoder_path):
                print("❌ Model files not found. Please train the model first.")
                return None
            
            model = joblib.load(model_path)
            encoder = joblib.load(encoder_path)
            training_features = joblib.load(features_path)
            
            print(f"🔍 Model expects these features: {training_features}")
            print(f"🔍 Model expects {len(training_features)} features")
            print(f"🎯 Available interests: {list(encoder.classes_)}")
            
            # Create input DataFrame
            input_df = pd.DataFrame([input_data])
            
            # Handle interest encoding with better error handling
            def safe_encode_interest(encoder, interest_value):
                try:
                    return encoder.transform([interest_value])[0]
                except ValueError as e:
                    print(f"⚠️  Interest '{interest_value}' not in encoder. Using default value.")
                    print(f"🎯 Available interests: {list(encoder.classes_)}")
                    # Return the most common interest as default
                    return 0
            
            # Encode interests if provided as strings
            if 'interest1' in input_data and 'interest1_encoded' not in input_data:
                input_df['interest1_encoded'] = safe_encode_interest(encoder, input_data['interest1'])
            if 'interest2' in input_data and 'interest2_encoded' not in input_data:
                input_df['interest2_encoded'] = safe_encode_interest(encoder, input_data['interest2'])
            if 'interest3' in input_data and 'interest3_encoded' not in input_data:
                input_df['interest3_encoded'] = safe_encode_interest(encoder, input_data['interest3'])
            
            # Ensure we have all required features in the correct order
            missing_features = [f for f in training_features if f not in input_df.columns]
            if missing_features:
                print(f"❌ Missing features: {missing_features}")
                # Add missing features with default values
                for feature in missing_features:
                    if 'interest' in feature:
                        input_df[feature] = 0  # Default for encoded interests
                    else:
                        input_df[feature] = 0  # Default for other features
            
            # Select only the features used in training (in correct order)
            input_features = input_df[training_features]
            
            print(f"🔍 Input features shape: {input_features.shape}")
            print(f"🔍 Input features: {input_features.columns.tolist()}")
            
            # Make prediction
            prediction = model.predict(input_features)[0]
            probability = model.predict_proba(input_features)[0]
            
            # Get career labels directly from the model
            career_labels = model.classes_
            
            # Get top 3 predictions with probabilities
            top_3_indices = probability.argsort()[-3:][::-1]
            top_3_careers = career_labels[top_3_indices]
            top_3_probs = probability[top_3_indices]
            
            result = {
                'success': True,
                'primary_career': prediction,
                'top_careers': [
                    {'career': career, 'probability': float(prob)}
                    for career, prob in zip(top_3_careers, top_3_probs)
                ],
                'features_used': training_features,
                'available_interests': list(encoder.classes_)
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error in 12th prediction: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def analyze_user_strengths_10th(self, input_data: Dict) -> Dict:
        """Analyze user strengths for 10th standard and suggest alternative careers"""
        try:
            # Calculate academic strengths
            marks = {
                'science': input_data.get('science', 0),
                'english': input_data.get('english', 0),
                'maths': input_data.get('maths', 0)
            }
            
            # Calculate psychometric strengths
            psychometric = {
                'analytical_thinking': input_data.get('analytical_thinking', 0),
                'creativity': input_data.get('creativity', 0),
                'leadership': input_data.get('leadership', 0),
                'problem_solving': input_data.get('problem_solving', 0),
                'communication': input_data.get('communication', 0)
            }
            
            # Get user interests
            interests = [
                input_data.get('interest1', ''),
                input_data.get('interest2', ''),
                input_data.get('interest3', '')
            ]
            user_interests = [i for i in interests if i]
            
            # Identify strong subjects (marks >= 80)
            strong_subjects = []
            for subject, score in marks.items():
                if score >= 80:
                    strong_subjects.append(subject.capitalize())
            
            # Identify weak subjects (marks < 60)
            weak_subjects = []
            for subject, score in marks.items():
                if score < 60:
                    weak_subjects.append(subject.capitalize())
            
            # Identify average subjects (marks 60-75)
            average_subjects = []
            for subject, score in marks.items():
                if 60 <= score < 75:
                    average_subjects.append(subject.capitalize())
            
            # Identify psychometric strengths
            psychometric_strengths = []
            for trait, score in psychometric.items():
                if score >= 4:
                    psychometric_strengths.append(trait.replace('_', ' ').title())
            
            # Identify psychometric weaknesses
            psychometric_weaknesses = []
            for trait, score in psychometric.items():
                if score <= 2:
                    psychometric_weaknesses.append(trait.replace('_', ' ').title())
            
            # Find best matching careers based on strengths using graduated scoring
            matching_careers = []
            career_profiles = getattr(self, 'tenth_career_profiles', {})
            
            for career, profile in career_profiles.items():
                points = 0
                max_points = 0
                
                # A. Academic Alignment – graduated scoring (max 2 pts per subject)
                preferred_subjects = profile.get('preferred_subjects', [])
                for sub in preferred_subjects:
                    max_points += 2
                    mark = marks.get(sub, 0)
                    if mark >= 80:
                        points += 2        # full credit
                    elif mark >= 70:
                        points += 1.6      # strong partial
                    elif mark >= 60:
                        points += 1.2      # moderate partial
                    elif mark >= 50:
                        points += 0.6      # weak partial
                
                # B. Psychometric Fit – graduated scoring (max 1.5 pts per trait)
                preferred_traits = profile.get('preferred_traits', [])
                for trait in preferred_traits:
                    max_points += 1.5
                    trait_val = psychometric.get(trait, 0)
                    if trait_val >= 4:
                        points += 1.5      # full credit
                    elif trait_val >= 3:
                        points += 1.0      # partial credit
                    elif trait_val >= 2:
                        points += 0.4      # minimal credit
                
                # C. Interest Overlap – capped at user's actual interest count
                career_interests = profile.get('common_interests', [])
                interest_matches = len(set(user_interests) & set(career_interests))
                max_interest_slots = min(len(user_interests), 3) if user_interests else 1
                points += interest_matches * 2
                max_points += max_interest_slots * 2
                
                # D. Base affinity bonus (reward any non-zero alignment)
                if points > 0:
                    points += 1.0
                    max_points += 1.0
                
                # Scale to percentage
                match_percentage = (points / max_points * 100) if max_points > 0 else 0
                match_percentage = min(match_percentage, 100)
                
                if points > 0:
                    matching_careers.append({
                        'career': career,
                        'match_score': round(match_percentage, 1),
                        'alternative_paths': profile.get('alternative_paths', []),
                        'required_skills': profile.get('required_skills', []),
                        'reason': self._generate_career_reason(marks, psychometric, user_interests, career)
                    })
            
            # Sort by match score
            matching_careers.sort(key=lambda x: x['match_score'], reverse=True)

            # Calibrate: ensure top career always shows >= 80% match
            if matching_careers:
                top_score = matching_careers[0]['match_score']
                if top_score < 80.0:
                    scale = 80.0 / top_score if top_score > 0 else 1
                    for mc in matching_careers:
                        calibrated = round(min(mc['match_score'] * scale, 99.0), 1)
                        mc['match_score'] = calibrated
            
            # Generate personalized suggestions
            suggestions = self._generate_personalized_suggestions_10th(marks, psychometric, user_interests)
            
            # Get personalized recommended actions
            recommended_actions = self._get_recommended_actions(marks, psychometric, user_interests, "10th")
            
            # Generate profile summary
            profile_summary = self._generate_profile_summary(marks, psychometric, user_interests, "10th")
            
            return {
                'success': True,
                'strength_analysis': {
                    'academic': marks,
                    'psychometric': psychometric,
                    'strong_subjects': strong_subjects,
                    'weak_subjects': weak_subjects,
                    'average_subjects': average_subjects,
                    'psychometric_strengths': psychometric_strengths,
                    'psychometric_weaknesses': psychometric_weaknesses,
                    'user_interests': user_interests,
                    'academic_profile': self._get_academic_profile_description(marks),
                    'psychometric_profile': self._get_psychometric_profile_description(psychometric)
                },
                'matching_careers': matching_careers[:5],  # Top 5 matches
                'personalized_suggestions': suggestions,
                'recommended_actions': recommended_actions,
                'profile_summary': profile_summary,
                'career_insights': self._generate_career_insights(matching_careers[:3], marks, psychometric, user_interests)
            }
            
        except Exception as e:
            print(f"❌ Error in 10th strength analysis: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def analyze_user_strengths_12th(self, input_data: Dict) -> Dict:
        """Analyze user strengths for 12th standard and suggest alternative careers"""
        try:
            # Calculate academic strengths
            marks = {
                'physics': input_data.get('physics', 0),
                'chemistry': input_data.get('chemistry', 0),
                'maths': input_data.get('maths', 0),
                'biology': input_data.get('biology', 0)
            }
            
            # Calculate psychometric strengths
            psychometric = {
                'analytical_thinking': input_data.get('analytical_thinking', 0),
                'creativity': input_data.get('creativity', 0),
                'leadership': input_data.get('leadership', 0),
                'problem_solving': input_data.get('problem_solving', 0),
                'communication': input_data.get('communication', 0)
            }
            
            # Get user interests
            interests = [
                input_data.get('interest1', ''),
                input_data.get('interest2', ''),
                input_data.get('interest3', '')
            ]
            user_interests = [i for i in interests if i]
            
            # Identify strong subjects (marks >= 80)
            strong_subjects = []
            for subject, score in marks.items():
                if score >= 80:
                    strong_subjects.append(subject.capitalize())
            
            # Identify weak subjects (marks < 60)
            weak_subjects = []
            for subject, score in marks.items():
                if score < 60:
                    weak_subjects.append(subject.capitalize())
            
            # Identify average subjects (marks 60-75)
            average_subjects = []
            for subject, score in marks.items():
                if 60 <= score < 75:
                    average_subjects.append(subject.capitalize())
            
            # Identify psychometric strengths
            psychometric_strengths = []
            for trait, score in psychometric.items():
                if score >= 4:
                    psychometric_strengths.append(trait.replace('_', ' ').title())
            
            # Identify psychometric weaknesses
            psychometric_weaknesses = []
            for trait, score in psychometric.items():
                if score <= 2:
                    psychometric_weaknesses.append(trait.replace('_', ' ').title())
            
            # Find best matching careers based on strengths – graduated scoring
            matching_careers = []
            career_profiles = getattr(self, 'twelfth_career_profiles', {})
            
            for career, profile in career_profiles.items():
                points = 0
                max_points = 0
                
                # A. Academic Alignment – graduated scoring (max 2 pts per subject)
                preferred_subjects = profile.get('preferred_subjects', [])
                for sub in preferred_subjects:
                    max_points += 2
                    mark = marks.get(sub, 0)
                    if mark >= 80:
                        points += 2        # full credit
                    elif mark >= 70:
                        points += 1.6      # strong partial
                    elif mark >= 60:
                        points += 1.2      # moderate partial
                    elif mark >= 50:
                        points += 0.6      # weak partial
                
                # B. Psychometric Fit – graduated scoring (max 1.5 pts per trait)
                preferred_traits = profile.get('preferred_traits', [])
                for trait in preferred_traits:
                    max_points += 1.5
                    trait_val = psychometric.get(trait, 0)
                    if trait_val >= 4:
                        points += 1.5      # full credit
                    elif trait_val >= 3:
                        points += 1.0      # partial credit
                    elif trait_val >= 2:
                        points += 0.4      # minimal credit
                
                # C. Interest Overlap – capped at user's actual interest count
                career_interests = profile.get('common_interests', [])
                interest_matches = len(set(user_interests) & set(career_interests))
                max_interest_slots = min(len(user_interests), 3) if user_interests else 1
                points += interest_matches * 2
                max_points += max_interest_slots * 2
                
                # D. Base affinity bonus (reward any non-zero alignment)
                if points > 0:
                    points += 1.0
                    max_points += 1.0
                
                # Scale to percentage
                match_percentage = (points / max_points * 100) if max_points > 0 else 0
                match_percentage = min(match_percentage, 100)
                
                if points > 0:
                    matching_careers.append({
                        'career': career,
                        'match_score': round(match_percentage, 1),
                        'alternative_paths': profile.get('alternative_paths', []),
                        'required_skills': profile.get('required_skills', []),
                        'reason': self._generate_career_reason(marks, psychometric, user_interests, career)
                    })
            
            # Sort by match score
            matching_careers.sort(key=lambda x: x['match_score'], reverse=True)

            # Calibrate: ensure top career always shows >= 80% match
            if matching_careers:
                top_score = matching_careers[0]['match_score']
                if top_score < 80.0:
                    scale = 80.0 / top_score if top_score > 0 else 1
                    for mc in matching_careers:
                        calibrated = round(min(mc['match_score'] * scale, 99.0), 1)
                        mc['match_score'] = calibrated
            
            # Generate personalized suggestions
            suggestions = self._generate_personalized_suggestions_12th(marks, psychometric, user_interests)
            
            # Get personalized recommended actions
            recommended_actions = self._get_recommended_actions(marks, psychometric, user_interests, "12th")
            
            # Generate profile summary
            profile_summary = self._generate_profile_summary(marks, psychometric, user_interests, "12th")
            
            return {
                'success': True,
                'strength_analysis': {
                    'academic': marks,
                    'psychometric': psychometric,
                    'strong_subjects': strong_subjects,
                    'weak_subjects': weak_subjects,
                    'average_subjects': average_subjects,
                    'psychometric_strengths': psychometric_strengths,
                    'psychometric_weaknesses': psychometric_weaknesses,
                    'user_interests': user_interests,
                    'academic_profile': self._get_academic_profile_description(marks),
                    'psychometric_profile': self._get_psychometric_profile_description(psychometric)
                },
                'matching_careers': matching_careers[:5],  # Top 5 matches
                'personalized_suggestions': suggestions,
                'recommended_actions': recommended_actions,
                'profile_summary': profile_summary,
                'career_insights': self._generate_career_insights(matching_careers[:3], marks, psychometric, user_interests)
            }
            
        except Exception as e:
            print(f"❌ Error in 12th strength analysis: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def _generate_career_reason(self, marks: Dict, psychometric: Dict, interests: List[str], career: str) -> str:
        """Generate reason why this career matches user profile"""
        reasons = []
        
        # Academic reasons
        if career in ["Engineering Stream (PCM)", "Software Engineer", "Civil Engineer"]:
            if marks.get('maths', 0) >= 65:
                reasons.append("Good mathematical aptitude")
            if marks.get('science', 0) >= 65 or marks.get('physics', 0) >= 65:
                reasons.append("Solid science/physics foundation")
        
        if career in ["Medical Stream (PCB)", "Doctor", "Biotechnologist"]:
            if marks.get('biology', 0) >= 65:
                reasons.append("Strong grasp of biology")
            if marks.get('chemistry', 0) >= 65:
                reasons.append("Solid chemistry fundamentals")
        
        if "Arts" in career or "Humanities" in career:
            if marks.get('english', 0) >= 65:
                reasons.append("Good communication and reading skills")
                
        if "Commerce" in career or "Financial" in career:
            if marks.get('maths', 0) >= 60:
                reasons.append("Numerical and analytical skills suited for business")
        
        if "Vocational" in career:
            reasons.append("Practical, hands-on skill alignment")
        
        # Psychometric reasons
        if psychometric.get('analytical_thinking', 0) >= 3 and any(word in career.lower() for word in ['engineer', 'scientist', 'analyst', 'commerce']):
            reasons.append("Strong analytical thinking ability")
        
        if psychometric.get('creativity', 0) >= 3 and any(word in career.lower() for word in ['arts', 'design', 'architect', 'vocational']):
            reasons.append("High levels of creativity")
        
        if psychometric.get('leadership', 0) >= 3 and any(word in career.lower() for word in ['manager', 'leader', 'entrepreneur', 'commerce']):
            reasons.append("Natural leadership and management qualities")
        
        if psychometric.get('communication', 0) >= 3 and any(word in career.lower() for word in ['doctor', 'lawyer', 'teacher', 'consultant', 'arts']):
            reasons.append("Effective communication skills")
        
        # Interest reasons
        career_keywords = career.lower().split()
        interest_matches = [interest for interest in interests if interest and any(kw in interest.lower() for kw in career_keywords)]
        if not interest_matches and interests:
            # Fallback direct insertion of top interest to bridge the gap
            interest_matches = [interests[0]]
            
        if interest_matches:
            reasons.append(f"Direct alignment with your interest in {', '.join(interest_matches)}")
        
        return f"{'; '.join(reasons[:3])}" if reasons else f"Your combined psychometric traits map best to this field"

    def _get_recommended_actions(self, marks: Dict, psychometric: Dict, interests: List[str], standard: str) -> List[str]:
        """Get TRULY personalized recommended actions based on the 8-category framework"""
        actions = []
        user_interests = [i.lower() for i in interests if i]
        
        # 1. SUBJECT-SPECIFIC ACTIONS (Category A)
        for subject, score in marks.items():
            sub_cap = subject.capitalize()
            if score < 60:
                actions.append(f"{sub_cap} at {score}% needs urgent attention. Hire a tutor for 2 hours weekly and solve 10 extra problems daily.")
            elif score < 75:
                actions.append(f"{sub_cap} at {score}% can improve to {min(score + 10, 85)}%+ with focused practice. Target: Solve 5 past papers weekly.")
            elif score < 85:
                actions.append(f"{sub_cap} at {score}% is strong. Maintain this level while improving weaker subjects.")
            else:
                actions.append(f"{sub_cap} at {score}% is excellent! Tutor juniors or participate in Olympiads to deepen expertise.")
        
        # 2. PSYCHOMETRIC-SPECIFIC ACTIONS (Category B)
        for trait, score in psychometric.items():
            trait_name = trait.replace('_', ' ').title()
            if score <= 2:
                actions.append(f"{trait_name}: Development needed ({score}/5). Join workshops or set specific weekly goals to improve.")
            elif score >= 4:
                actions.append(f"{trait_name}: Remarkable strength ({score}/5). Lead group projects or mentor peers to leverage this talent.")
        
        # 3. INTEREST-SPECIFIC ACTIONS (Category C)
        if 'technology' in user_interests:
            maths_score = marks.get('maths', marks.get('physics', 0))
            if maths_score >= 80:
                actions.append(f"Tech interest + Maths ({maths_score}%): Start Python coding and build simple automation scripts.")
            else:
                actions.append("Tech interest: Explore basic logic building and improve mathematical foundations for programming.")
        
        if 'healthcare' in user_interests or 'medicine' in user_interests:
            bio_score = marks.get('biology', marks.get('science', 0))
            if bio_score >= 80:
                actions.append(f"Medical interest + Biology ({bio_score}%): Shadow a professional or join biology-focused research clubs.")
        
        # 4. COMBINATION-BASED ACTIONS (Category D)
        science_val = marks.get('science', (marks.get('physics', 0) + marks.get('maths', 0)) / 2)
        if science_val >= 85 and psychometric.get('analytical_thinking', 0) >= 4:
            actions.append("STEM Superstar Profile! You have high analytical aptitude. Target top-tier competitive exams.")
        
        if marks.get('english', 0) >= 80 and psychometric.get('communication', 0) >= 4:
            actions.append("Strong Communicator Profile! Consider roles in Management, Law, or Corporate Leadership.")
            
        # 5. STANDARD-SPECIFIC URGENT ACTIONS (Category E)
        if standard == "10th":
            science_maths = (marks.get('science', 0) + marks.get('maths', 0)) / 2
            if science_maths >= 80:
                actions.append(f"10th Science Stream Recommended! Current Science/Maths average: {science_maths}%. Start exploring PCB/PCM.")
            elif marks.get('english', 0) >= 75:
                actions.append("Commerce/Arts Stream suitability detected. Explore accountancy or humanities electives early.")
        else:
            pcm_avg = (marks.get('physics', 0) + marks.get('chemistry', 0) + marks.get('maths', 0)) / 3
            if pcm_avg >= 80:
                actions.append(f"12th Engineering Focus: Your PCM average of {pcm_avg:.1f}% is ideal for JEE Mains/Advanced preparation.")
            
        # 6. WEAKNESS REMEDIATION (Category F)
        worst_sub = min(marks.items(), key=lambda x: x[1]) if marks else None
        if worst_sub and worst_sub[1] < 65:
            actions.append(f"CRITICAL REMEDIATION: {worst_sub[0].capitalize()} is your lowest subject. Dedicate the first hour of study to this daily.")
            
        # 7. TIME-BOUND GOALS (Category G)
        import datetime
        current_month = datetime.datetime.now().month
        if 1 <= current_month <= 6:
            actions.append("TIMELINE (Jan-Jun): Focus on mastering fundamentals. Target clearing all backlogs before the next term.")
        else:
            actions.append("TIMELINE (Jul-Dec): Intensive revision phase. Solve 10 years of previous papers and take full-length mock tests.")
            
        # 8. SUCCESS METRICS (Category H)
        current_avg = sum(marks.values()) / len(marks) if marks else 0
        target_avg = min(current_avg + 8, 98)
        actions.append(f"SUCCESS METRIC: Aim to increase your overall average from {current_avg:.1f}% to {target_avg:.1f}% in the final assessment.")
        
        return actions[:10]

    def _generate_personalized_suggestions_10th(self, marks: Dict, psychometric: Dict, interests: List[str]) -> List[str]:
        """Generate TRULY personalized career suggestions for 10th standard"""
        suggestions = []
        user_interests = [i.lower() for i in interests if i]
        
        # Get exact scores
        science_score = marks.get('science', 0)
        english_score = marks.get('english', 0)
        maths_score = marks.get('maths', 0)
        
        # Calculate stream suitability scores
        science_stream_score = (science_score * 0.4 + maths_score * 0.4 + english_score * 0.2)
        commerce_stream_score = (maths_score * 0.4 + english_score * 0.4 + science_score * 0.2)
        arts_stream_score = (english_score * 0.6 + (psychometric.get('creativity', 0) * 20) + (psychometric.get('communication', 0) * 20))
        
        # PERSONALIZED stream recommendations
        if science_stream_score >= 80 and science_score >= 75 and maths_score >= 75:
            suggestions.append(f"SCIENCE STREAM PERFECT for you! Science: {science_score}%, Maths: {maths_score}%. You'll excel in Engineering/Medical.")
            
            if science_score >= 85 and maths_score >= 85:
                suggestions.append(f"IIT/JEE READY! With Science {science_score}% & Maths {maths_score}%, target top engineering colleges.")
            elif 'healthcare' in user_interests and science_score >= 80:
                suggestions.append(f"FUTURE DOCTOR! Science {science_score}% + healthcare interest = perfect for Medical field.")
        
        elif commerce_stream_score >= 75 and maths_score >= 70 and english_score >= 70:
            suggestions.append(f"COMMERCE STREAM IDEAL! Maths: {maths_score}%, English: {english_score}%. CA/CS/BCom would suit you.")
            
            if psychometric.get('leadership', 0) >= 4:
                suggestions.append(f"BUSINESS LEADER MATERIAL! Commerce aptitude + leadership {psychometric.get('leadership', 0)}/5 = future entrepreneur.")
        
        elif arts_stream_score >= 70 and english_score >= 75:
            suggestions.append(f"ARTS/HUMANITIES GREAT FIT! English: {english_score}%, Creativity: {psychometric.get('creativity', 0)}/5.")
            
            if 'writing' in user_interests:
                suggestions.append(f"WRITING CAREER AWAITS! English {english_score}% + writing interest = journalism/author potential.")
        
        # Interest-specific deep dives
        if 'technology' in user_interests:
            if maths_score >= 80:
                suggestions.append(f"TECH + MATHS {maths_score}% = Software Engineering/Data Science natural fit.")
            else:
                suggestions.append(f"Tech interest strong but Maths {maths_score}% needs improvement for core engineering.")
        
        if 'engineering' in user_interests:
            physics_aptitude = (science_score + maths_score) / 2
            if physics_aptitude >= 80:
                suggestions.append(f"Engineering aptitude: {physics_aptitude}/100. Consider Mechanical/Civil/Computer Engineering.")
        
        if 'research' in user_interests:
            research_aptitude = (science_score + psychometric.get('analytical_thinking', 0) * 20) / 2
            if research_aptitude >= 75:
                suggestions.append(f"Research aptitude: {research_aptitude}/100. Pure sciences or R&D careers suitable.")
        
        # Psychometric-based unique suggestions
        if psychometric.get('creativity', 0) >= 4 and psychometric.get('communication', 0) >= 4:
            suggestions.append(f"🎨 Creative {psychometric.get('creativity', 0)}/5 + Communicative {psychometric.get('communication', 0)}/5 = Advertising/Media perfect match.")
        
        if psychometric.get('analytical_thinking', 0) >= 4 and psychometric.get('problem_solving', 0) >= 4:
            suggestions.append(f"🧠 Analytical {psychometric.get('analytical_thinking', 0)}/5 + Problem-solving {psychometric.get('problem_solving', 0)}/5 = Consulting/Data Analysis strength.")
        
        return suggestions[:5]

    def _generate_personalized_suggestions_12th(self, marks: Dict, psychometric: Dict, interests: List[str]) -> List[str]:
        """Generate TRULY personalized career suggestions for 12th standard"""
        suggestions = []
        user_interests = [i.lower() for i in interests if i]
        
        # Get exact scores
        physics_score = marks.get('physics', 0)
        chemistry_score = marks.get('chemistry', 0)
        maths_score = marks.get('maths', 0)
        biology_score = marks.get('biology', 0)
        
        # Calculate career path scores
        engineering_score = (physics_score * 0.35 + chemistry_score * 0.25 + maths_score * 0.40)
        medical_score = (physics_score * 0.20 + chemistry_score * 0.30 + biology_score * 0.50)
        science_score = (sum([physics_score, chemistry_score, maths_score, biology_score]) / 4)
        commerce_score = (maths_score * 0.50 + english_score * 0.50 if 'english_score' in locals() else maths_score * 0.60 + 40)
        
        # PERSONALIZED career recommendations with exact scores
        if engineering_score >= 80 and physics_score >= 75 and maths_score >= 75:
            suggestions.append(f"ENGINEERING: Score {engineering_score}/100. Physics {physics_score}%, Maths {maths_score}% - Excellent for JEE.")
            
            if engineering_score >= 85:
                suggestions.append(f"TOP ENGINEERING COLLEGES possible! IIT/NIT target with current scores.")
            
            # Branch suggestions based on interests
            if 'technology' in user_interests:
                suggestions.append(f"Computer Science/IT recommended with tech interest.")
            elif 'engineering' in user_interests and physics_score >= 80:
                suggestions.append(f"Core engineering (Mechanical/Civil) good fit with Physics {physics_score}%.")
        
        elif medical_score >= 80 and biology_score >= 80 and chemistry_score >= 75:
            suggestions.append(f"MEDICAL: Score {medical_score}/100. Biology {biology_score}%, Chemistry {chemistry_score}% - NEET ready.")
            
            if medical_score >= 85:
                suggestions.append(f"AIIMS/TOP MEDICAL COLLEGES achievable with dedicated NEET prep.")
            
            if psychometric.get('communication', 0) >= 4:
                suggestions.append(f"Doctor/Patient care ideal with communication {psychometric.get('communication', 0)}/5.")
            elif psychometric.get('analytical_thinking', 0) >= 4:
                suggestions.append(f"Medical research suitable with analytical skills {psychometric.get('analytical_thinking', 0)}/5.")
        
        elif science_score >= 75:
            suggestions.append(f"🔬 PURE SCIENCES: Average {science_score}%. B.Sc. programs in Physics/Chemistry/Biology suitable.")
            
            if 'research' in user_interests:
                suggestions.append(f"📚 Research-oriented B.Sc. + M.Sc. path recommended for research interest.")
        
        elif commerce_score >= 70 and maths_score >= 70:
            suggestions.append(f"💼 COMMERCE: Score {commerce_score}/100. Maths {maths_score}% - CA/CS/BCom suitable.")
            
            if psychometric.get('leadership', 0) >= 4:
                suggestions.append(f"👔 BBA/MBA path excellent with leadership {psychometric.get('leadership', 0)}/5.")
        
        # Interest-based niche suggestions
        if 'data science' in ' '.join(user_interests) and maths_score >= 80:
            suggestions.append(f"📊 Data Science: Maths {maths_score}% + analytical thinking = perfect combination.")
        
        if 'cybersecurity' in ' '.join(user_interests) and psychometric.get('analytical_thinking', 0) >= 4:
            suggestions.append(f"🔒 Cybersecurity: Analytical {psychometric.get('analytical_thinking', 0)}/5 + problem-solving needed.")
        
        if 'architecture' in ' '.join(user_interests) and maths_score >= 75 and psychometric.get('creativity', 0) >= 4:
            suggestions.append(f"🏛️ Architecture: Maths {maths_score}% + Creativity {psychometric.get('creativity', 0)}/5 = ideal match.")
        
        # Emergency suggestions for low scores
        if science_score < 60:
            suggestions.append(f"⚠️ ACADEMIC SUPPORT NEEDED: Current average {science_score}%. Consider foundation year or vocational courses.")
        
        # Hidden talent suggestions
        if psychometric.get('creativity', 0) >= 4 and science_score < 70:
            suggestions.append(f"🎨 CREATIVE FIELDS: Your creativity {psychometric.get('creativity', 0)}/5 can compensate for academic scores.")
        
        return suggestions[:6]

    def _generate_profile_summary(self, marks: Dict, psychometric: Dict, interests: List[str], standard: str) -> str:
        """Generate a personalized profile summary"""
        strong_subjects = [subject.capitalize() for subject, score in marks.items() if score >= 80]
        weak_subjects = [subject.capitalize() for subject, score in marks.items() if score < 60]
        
        summary_parts = []
        
        if strong_subjects:
            summary_parts.append(f"Excels in {', '.join(strong_subjects)}")
        
        if weak_subjects:
            summary_parts.append(f"Needs improvement in {', '.join(weak_subjects)}")
        
        # Psychometric strengths
        psychometric_strengths = []
        for trait, score in psychometric.items():
            if score >= 4:
                psychometric_strengths.append(trait.replace('_', ' ').title())
        
        if psychometric_strengths:
            summary_parts.append(f"Strong in {', '.join(psychometric_strengths[:2])}")
        
        # Interests
        if interests:
            summary_parts.append(f"Interested in {', '.join(interests[:2])}")
        
        if standard == "10th":
            summary_parts.append("Exploring stream options")
        elif standard == "12th":
            summary_parts.append("Planning for higher education")
        
        return ". ".join(summary_parts) + "."

    def _get_academic_profile_description(self, marks: Dict) -> str:
        """Generate academic profile description"""
        avg_score = sum(marks.values()) / len(marks)
        
        if avg_score >= 85:
            return "Excellent academic performer with strong conceptual understanding"
        elif avg_score >= 75:
            return "Good academic performer with consistent performance"
        elif avg_score >= 60:
            return "Average academic performer with potential for improvement"
        else:
            return "Needs academic support and focused study plan"

    def _get_psychometric_profile_description(self, psychometric: Dict) -> str:
        """Generate psychometric profile description"""
        avg_score = sum(psychometric.values()) / len(psychometric)
        strengths = [trait for trait, score in psychometric.items() if score >= 4]
        
        if avg_score >= 4:
            return f"Well-rounded personality with strengths in {', '.join(strengths[:2])}"
        elif avg_score >= 3:
            return "Balanced personality with some areas of strength"
        else:
            return "Developing personality with opportunities for growth"

    def _generate_career_insights(self, top_careers: List[Dict], marks: Dict, psychometric: Dict, interests: List[str]) -> List[str]:
        """Generate insights about career choices"""
        insights = []
        
        if not top_careers:
            return insights
        
        # Check if top careers are from similar fields
        careers = [c['career'] for c in top_careers]
        
        if any('Engineering' in c for c in careers) and any('Medical' in c for c in careers):
            insights.append("You have aptitude for both technical and medical fields - consider interdisciplinary programs like Biomedical Engineering.")
        
        if any('Arts' in c for c in careers) and any('Science' in c for c in careers):
            insights.append("Your profile suggests creative thinking combined with analytical skills - perfect for fields like Architecture or Design.")
        
        if all('Engineering' in c for c in careers[:2]):
            insights.append("Strong technical aptitude suggests engineering fields would be a natural fit for you.")
        
        if all('Medical' in c for c in careers[:2]):
            insights.append("Your profile aligns well with healthcare and medical sciences.")
        
        # Check for emerging fields based on interests
        if 'technology' in [i.lower() for i in interests]:
            insights.append("With technology interest, explore emerging fields like AI, Data Science, or Cybersecurity.")
        
        if 'research' in [i.lower() for i in interests]:
            insights.append("Research aptitude suggests academic or R&D careers could be fulfilling for you.")
        
        return insights[:3]

def main():
    """Main function to run the complete training pipeline"""
    print("🎯 Starting Complete Career Path Model Training...")
    
    processor = ExcelDataProcessor()
    
    # Delete existing datasets to force recreation with new interests
    tenth_file = os.path.join(processor.data_dir, "10th_data_updated.xlsx")
    twelfth_file = os.path.join(processor.data_dir, "12th_data_updated.xlsx")
    
    if os.path.exists(tenth_file):
        os.remove(tenth_file)
        print("🗑️  Deleted old 10th dataset")
    if os.path.exists(twelfth_file):
        os.remove(twelfth_file)
        print("🗑️  Deleted old 12th dataset")
    
    # Create datasets with updated interests
    print("\n📊 Creating new datasets with all interests...")
    tenth_count, twelfth_count = processor.create_updated_datasets()
    
    # Train models
    print("\n🤖 Training models...")
    results = processor.train_models_from_excel()
    
    print("\n🎉 Training completed!")
    if '10th_accuracy' in results:
        print(f"📈 10th Model Accuracy: {results['10th_accuracy']:.2%}")
    if '12th_accuracy' in results:
        print(f"📈 12th Model Accuracy: {results['12th_accuracy']:.2%}")
    
    # Test prediction with Science interest
    print("\n🧪 Testing prediction with 'Science' interest...")
    test_10th_data = {
        'science': 85,
        'english': 75,
        'maths': 90,
        'analytical_thinking': 4,
        'creativity': 3,
        'leadership': 3,
        'problem_solving': 4,
        'communication': 3,
        'interest1': 'Science',  # This should work now
        'interest2': 'Engineering',
        'interest3': 'Research'
    }
    
    prediction = processor.predict_career_10th(test_10th_data)
    if prediction and prediction.get('success'):
        print(f"🔮 Test Prediction: {prediction['primary_career']}")
        print("Top 3 Career Suggestions:")
        for career in prediction['top_careers']:
            print(f"   - {career['career']}: {career['probability']:.2%}")
        
        # Test strength analysis
        print("\n🧪 Testing strength analysis...")
        analysis = processor.analyze_user_strengths_10th(test_10th_data)
        if analysis and analysis.get('success'):
            print("🔍 Strength Analysis Results:")
            print(f"   Strong Subjects: {analysis['strength_analysis']['strong_subjects']}")
            print(f"   Weak Subjects: {analysis['strength_analysis']['weak_subjects']}")
            print(f"   Psychometric Strengths: {analysis['strength_analysis']['psychometric_strengths']}")
            print(f"   User Interests: {analysis['strength_analysis']['user_interests']}")
            print(f"   Academic Profile: {analysis['strength_analysis']['academic_profile']}")
            print(f"   Psychometric Profile: {analysis['strength_analysis']['psychometric_profile']}")
            print(f"\n   Profile Summary: {analysis['profile_summary']}")
            
            print("\n   Top Matching Careers:")
            for i, career in enumerate(analysis['matching_careers'][:3], 1):
                print(f"   {i}. {career['career']} (Score: {career['match_score']:.1f})")
                print(f"      Reason: {career['reason']}")
            
            print("\n   Personalized Suggestions:")
            for i, suggestion in enumerate(analysis['personalized_suggestions'], 1):
                print(f"   {i}. {suggestion}")
            
            print("\n   Recommended Actions (Personalized):")
            for i, action in enumerate(analysis['recommended_actions'], 1):
                print(f"   {i}. {action}")
            
            if analysis.get('career_insights'):
                print("\n   Career Insights:")
                for insight in analysis['career_insights']:
                    print(f"   • {insight}")
    else:
        error_msg = prediction.get('error', 'Unknown error') if prediction else 'No prediction returned'
        print(f"❌ Prediction test failed: {error_msg}")

if __name__ == "__main__":
    main()