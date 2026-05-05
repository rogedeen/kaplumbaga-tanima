# SeaTurtleID: Advanced Sea Turtle Identification & XAI Platform

SeaTurtleID is a premium, autonomous, AI-powered platform designed to identify individual sea turtles using their unique facial scale patterns (post-ocular scales), analogous to human fingerprints.

## 1. Core Mission
The system provides high-accuracy identification of turtle species and individuals using Metric Learning (ArcFace). It prioritizes **Explainable AI (XAI)** to provide visual insights and statistical confidence scores, ensuring conservation research is transparent and data-driven.

## 2. Technical Architecture (SOLID Compliant)

### Model (Python/PyTorch)
- **Architecture:** ConvNeXt-Tiny backbone with **ArcFace** Metric Learning head.
- **Classes:** 367 distinct turtle individuals.
- **Inference:** High-speed single-image inference script (`evaluate_single_image.py`).
- **Precision:** $384 \times 384$ input normalization for maximum detail extraction.

### Backend (NestJS / TypeScript)
- **Architecture:** Strictly **SOLID** compliant architecture.
- **Dependency Inversion:** Decoupled Inference Engine (`IInferenceEngine`) interface allowing plug-and-play model engines.
- **Persistence:** Prisma ORM with Supabase (PostgreSQL) integration.
- **Audit Logging:** Integrated audit trail for all inference requests.

### Frontend (React)
- **UI/UX:** "Premium Research Tool" aesthetics with Tailwind CSS.
- **Design:** Glassmorphism, dark-mode optimized, and reactive layout.
- **Features:** Interactive Drag-and-Drop uploader, real-time log streaming, and visual confidence indicators.

## 3. Multi-Agent Development System
This project was developed and refactored using a specialized Multi-Agent System (MAS):
- **Senior Full-Stack Architect (Agent):** Orchestrated the SOLID refactoring and premium UI integration.
- **Model Trainer:** Managed the PyTorch training pipeline on 367 classes.
- **Reviewer Agent:** Continuous code auditing and quality assurance.

## 4. Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+ (with PyTorch, Pillow)
- Git

### Installation & Launch

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Rogedeen/kaplumbaga-tanima.git
   ```

2. **Backend Setup:**
   ```bash
   cd src/backend
   npm install
   npm run start:dev
   ```

3. **Frontend Setup:**
   ```bash
   cd src/frontend_app
   npm install
   npm run dev
   ```

4. **Python Inference Environment:**
   Ensure `torch` and `Pillow` are installed in your environment.

## 5. Academic Standards
This project adheres to the highest academic coding standards:
- **SRP:** Every service and component has a single responsibility.
- **DRY:** Eliminated redundant code through modularization.
- **Auditability:** Every prediction is logged and traceable.

---
*Developed for sea turtle conservation and advanced biometric research.*
