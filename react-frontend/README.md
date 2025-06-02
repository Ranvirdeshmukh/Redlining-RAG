# Contract Redlining RAG System - React Frontend

A modern, responsive React frontend for the Contract Redlining RAG System with Apple/Notion-inspired design.

## Features

- 🎨 **Modern Design**: Apple/Notion-inspired UI with clean aesthetics
- 📱 **Responsive**: Works perfectly on desktop, tablet, and mobile
- ⚡ **Fast**: Optimized React components with smooth animations
- 🔍 **Interactive**: Drag & drop upload, clickable risk analysis, detailed modals
- 🎯 **TypeScript**: Full type safety and better developer experience
- 🛡️ **Risk Analysis**: Color-coded risk levels with comprehensive details

## Components

- **Upload**: Drag & drop PDF upload with progress indicators
- **Dashboard**: Risk summary cards and document analysis controls  
- **Results**: Redlined contract viewer with clickable clause analysis
- **ClauseModal**: Detailed risk assessment with confidence scores
- **Toast**: Beautiful notification system
- **LoadingOverlay**: Smooth loading states with progress steps

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm start
   ```

3. **Make sure the FastAPI backend is running** on `http://localhost:8000`

## Design System

- **Colors**: RED (#ff4757), AMBER (#ffa502), GREEN (#2ed573), PRIMARY (#007bff)
- **Typography**: System fonts with clear hierarchy
- **Spacing**: Consistent 8px grid system
- **Shadows**: Subtle depth with multiple shadow levels
- **Animations**: Smooth 0.2s transitions for all interactions

## API Integration

The frontend integrates with the FastAPI backend through:
- Document upload and processing
- Real-time analysis with progress tracking
- Interactive clause exploration
- Results export functionality

## Build for Production

```bash
npm run build
```

The build folder will contain the optimized production build ready for deployment.
