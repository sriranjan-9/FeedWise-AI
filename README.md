# FeedWise

> An AI-powered Recommendation Intelligence Layer for Transparent and Healthier Recommendation Systems.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-black)
![Status](https://img.shields.io/badge/Status-Prototype-success)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

FeedWise is an AI-powered Recommendation Intelligence Layer that sits on top of existing recommendation systems rather than replacing them.

Modern recommendation engines are extremely effective at personalization, but they often operate as opaque "black boxes." Users rarely understand why specific content appears in their feed or when their recommendations begin narrowing into repetitive loops.

FeedWise improves recommendation transparency by continuously analyzing recommendation diversity, generating natural-language explanations, and suggesting lightweight interventions that encourage healthier content discovery while preserving personalization.

To demonstrate the concept, this project also includes **InstaKilogram**, a synthetic short-form social media platform built specifically for evaluating FeedWise.

---

## Features

- Explainable AI for recommendations
- Feed Health Score
- Recommendation diversity analysis
- Real-time recommendation monitoring
- Automatic intervention suggestions
- Session analytics dashboard
- Synthetic social media test platform (InstaKilogram)
- Lightweight architecture suitable for real-time deployment

---

## Project Architecture

```
                    User
                      │
                      ▼
              InstaKilogram Feed
                      │
                      ▼
          Recommendation Engine
                      │
                      ▼
         FeedWise Analysis Layer
      ┌──────────────────────────┐
      │ Feed Diversity Analysis  │
      │ Shannon Entropy          │
      │ Repetition Detection     │
      │ Explainable AI           │
      │ Feed Health Score        │
      └──────────────────────────┘
                      │
                      ▼
          Intervention Suggestions
                      │
                      ▼
            Analytics Dashboard
```

---

## How FeedWise Works

1. A recommendation engine generates personalized content.

2. FeedWise observes the recommendation stream.

3. Recommendation diversity is measured using normalized Shannon entropy.

4. Repetitive recommendation patterns are detected.

5. A Feed Health Score is calculated.

6. Natural-language explanations are generated.

7. When diversity drops below a threshold, FeedWise recommends introducing underrepresented categories.

---

## Tech Stack

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- Flask
- Python

### Analytics

- Normalized Shannon Entropy
- Feed Health Score
- Recommendation Diversity Analysis
- Repetition Detection

### Development

- Git
- GitHub

---

## Repository Structure

```
FeedWise/
│
├── app/
│   ├── frontend/
│   ├── backend/
│   └── assets/
│
├── instakilogram/
│
├── dataset/
│
├── screenshots/
│
├── docs/
│
├── README.md
└── requirements.txt
```

---

## Prototype

The prototype consists of two connected applications.

### InstaKilogram

A synthetic short-form social media platform used to simulate recommendation behavior.

Features

- Personalized feed
- User interactions
- Recommendation simulation
- Multiple content categories

### FeedWise Dashboard

A real-time transparency dashboard providing:

- Feed Health Score
- Recommendation explanations
- Session statistics
- Diversity trend
- Intervention history

---

## Evaluation

Synthetic Dataset

- ~400 posts
- 19 content categories

Evaluation Metrics

| Metric | Result |
|---------|---------|
| Feed Classification Accuracy | 92% |
| Intervention Success Rate | 89% |
| Feed Diversity Improvement | 31% |
| Average Response Time | 41 ms |

---

## Future Work

- Browser extension deployment
- Integration with existing recommendation platforms
- Larger user studies
- Adaptive intervention thresholds
- Embedding-based semantic diversity analysis
- Cross-platform recommendation monitoring

---

## Research

This project was developed as part of **The Innovation Story** research program.

Research Paper included in the repository.

---

## Screenshots

### InstaKilogram

*(Insert screenshot)*

### FeedWise Dashboard

*(Insert screenshot)*

---

## Author

**Sriranjan Balaji**

Delhi Public School Gurgaon

Email:
sriranjanbalaji@gmail.com

---

## Acknowledgements

Special thanks to

- The Innovation Story
- My mentor Shishir
- MIT Project NANDA / NandaHack
- Everyone who provided valuable feedback throughout development.

---

## License

MIT License

Feel free to use, modify, and build upon this work with attribution.
