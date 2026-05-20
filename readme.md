# 🍽️ AI Meal Planner

AI-powered web app that generates personalized meal plans based on user preferences.

---

## 🚀 Overview

- ⚛️ React frontend  
- ⚡ FastAPI backend  
- 🤖 Ollama (local LLM)  
- 🗄️ MongoDB (meal history storage)  

---

## 🧠 How it works

1. User submits preferences  
2. Backend builds a base meal plan  
3. Recipes are added as context  
4. LLM improves the plan  
5. Output is validated  
6. Plan is saved and returned  

---

## 🔌 API

- `POST /generate-meal-plan`  
- `POST /preferences`  
- `GET /preferences`  
- `GET /meal-history`  

---

## ▶️ Run

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload