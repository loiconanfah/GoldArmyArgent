# 🎨 Dashboard Design System - GoldArmy Agent

## Vue d'ensemble

Le nouveau dashboard de GoldArmy Agent adopte un design moderne **dark glassmorphism** avec une identité visuelle cohérente centrée sur l'or/amber comme couleur principale.

## 🎯 Philosophie Design

### **Dark First**
- Thème sombre par défaut pour réduire la fatigue oculaire
- Contraste élevé pour une meilleure lisibilité
- Adaptation aux préférences modernes des développeurs

### **Glassmorphism**
- Effets de verre avec `backdrop-filter: blur()`
- Transparence et profondeur visuelle
- Cartes flottantes avec bordures subtiles

### **Gradient Gold Identity**
- Palette principale : `#fbbf24` → `#f59e0b` → `#d97706`
- Accent militaire avec l'emoji 🪖
- Cohérence avec le nom "GoldArmy"

## 🎨 Palette de Couleurs

### **Couleurs Principales**
```css
--gold-light: #fbbf24    /* Accent principal */
--gold-medium: #f59e0b   /* Hover states */
--gold-dark: #d97706     /* Active states */
```

### **Couleurs Neutres**
```css
--bg-primary: #0c0c0c    /* Fond principal */
--bg-secondary: #1a1a2e  /* Fond secondaire */
--bg-accent: #16213e     /* Accents */

--text-primary: #e2e8f0  /* Texte principal */
--text-secondary: #cbd5e1 /* Texte secondaire */
--text-muted: #94a3b8    /* Texte atténué */
--text-disabled: #64748b /* Texte désactivé */
```

### **Couleurs Glassmorphism**
```css
--glass-bg: rgba(30, 41, 59, 0.4)
--glass-border: rgba(148, 163, 184, 0.1)
--glass-hover: rgba(251, 191, 36, 0.3)
```

## 🔤 Typographie

### **Fontes**
- **Principal** : `Poppins` (300, 400, 500, 600, 700, 800)
- **Monospace** : `JetBrains Mono` (pour le code)
- **Fallback** : `-apple-system, BlinkMacSystemFont, sans-serif`

### **Hiérarchie**
```css
.hero-title     { font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 800; }
.section-title  { font-size: 1.5rem; font-weight: 700; }
.card-title     { font-size: 1.2rem; font-weight: 600; }
.body-text      { font-size: 0.9rem; font-weight: 400; }
.caption        { font-size: 0.8rem; font-weight: 500; }
```

## 🧩 Composants

### **Cards (Cartes)**
```css
.glass-card {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(20px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    transform: translateY(-4px);
    border-color: rgba(251, 191, 36, 0.3);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}
```

### **Boutons**
```css
/* Bouton principal */
.btn-primary {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    color: #0f172a;
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 15px rgba(251, 191, 36, 0.3);
}

/* Bouton secondaire */
.btn-secondary {
    background: rgba(148, 163, 184, 0.1);
    border: 1px solid rgba(148, 163, 184, 0.2);
    color: #cbd5e1;
    backdrop-filter: blur(10px);
}
```

### **Inputs**
```css
.input-field {
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 12px;
    color: #e2e8f0;
    padding: 12px 16px;
    backdrop-filter: blur(10px);
}

.input-field:focus {
    border-color: rgba(251, 191, 36, 0.6);
    box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.1);
}
```

### **Badges**
```css
.match-badge {
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    color: #0f172a;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
}
```

## 🏗️ Layout Structure

### **Sidebar**
- Largeur fixe avec navigation sticky
- Background glassmorphism semi-transparent
- Menu hiérarchique avec états hover/active

### **Main Content**
- Layout fluide et responsive
- Chat interface au centre
- Hero section pour l'état vide

### **Responsive Breakpoints**
```css
/* Mobile */
@media (max-width: 768px) {
    .hero-container { padding: 2rem 1rem; }
    .template-grid { grid-template-columns: 1fr; }
}

/* Desktop */
@media (min-width: 1024px) {
    .main-content { max-width: 1200px; margin: 0 auto; }
}
```

## ✨ Animations

### **Micro-interactions**
```css
/* Hover lift */
.hover-lift:hover {
    transform: translateY(-4px);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Slide effect */
.slide-effect:hover {
    transform: translateX(4px);
}

/* Glow animation */
@keyframes glow {
    from { filter: drop-shadow(0 0 5px rgba(251, 191, 36, 0.3)); }
    to { filter: drop-shadow(0 0 20px rgba(251, 191, 36, 0.6)); }
}
```

### **Loading States**
- Skeleton loaders avec shimmer effect
- Spinners avec couleur gold
- Status messages avec animations douces

## 🎯 Composants Spécialisés

### **Job Cards**
- Background glassmorphism avec hover effects
- Badge de matching score avec couleurs conditionnelles
- Layout flex pour l'alignement parfait
- Links stylisés avec transitions

### **Chat Interface**
- Messages avec background semi-transparent
- Avatar différencié (🪖 pour l'assistant, 👤 pour l'utilisateur)
- Input collant en bas avec glassmorphism

### **Premium Card**
- Gradient border avec animation
- Call-to-action proéminent
- Effet de brillance subtil

## 📱 Mobile Experience

### **Touch-Friendly**
- Boutons avec taille minimum 44px
- Espacements généreux entre éléments
- Scroll momentum natif

### **Navigation Mobile**
- Sidebar collapsible
- Gestures swipe pour navigation
- Bottom navigation alternative

## ⚡ Performance

### **Optimisations CSS**
```css
/* GPU Acceleration */
.gpu-accelerated {
    transform: translateZ(0);
    will-change: transform;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

### **Bundle Size**
- CSS critique inline
- Fonts preloaded
- Images optimisées WebP

## 🔧 Customisation

### **CSS Variables**
```css
:root {
    /* Couleurs customisables */
    --brand-primary: var(--gold-medium);
    --brand-secondary: var(--text-secondary);
    
    /* Spacing system */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    
    /* Border radius */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
}
```

## 🚀 Évolutions Futures

### **V2 Roadmap**
- [ ] Theme switcher (Dark/Light)
- [ ] Customizable accent colors
- [ ] Advanced animations library
- [ ] Component library extraction

### **Accessibilité**
- [ ] ARIA labels complets
- [ ] Focus management
- [ ] Keyboard navigation
- [ ] Screen reader optimization

## 📊 Métriques Design

### **Performance**
- **First Paint**: < 1s
- **LCP**: < 2.5s
- **CLS**: < 0.1

### **Utilisabilité**
- **Contrast Ratio**: 4.5:1 minimum
- **Touch Target**: 44px minimum
- **Loading States**: Toujours visibles

---

*Design System v1.0 - GoldArmy Agent*  
*Créé avec ❤️ et beaucoup de ☕*