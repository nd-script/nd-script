# ND-Script Documentation Fonts Setup
## إعداد الخطوط لتوثيق ND-Script

This guide explains how to set up local fonts for the ND-Script documentation to work in offline or enterprise environments.

## Font Requirements / متطلبات الخطوط

The documentation uses three font families:
- **Inter**: Modern sans-serif for UI elements
- **Amiri**: Arabic serif font for Arabic text
- **Fira Code**: Monospace font for code blocks

## Local Font Setup / إعداد الخطوط المحلية

### Step 1: Create Fonts Directory
```bash
mkdir -p docs/fonts
```

### Step 2: Download Required Fonts

#### Inter Font
Download from: https://fonts.google.com/specimen/Inter
Required weights: 400, 500, 600, 700
Files needed:
- `Inter-Regular.woff2`
- `Inter-Regular.woff`
- `Inter-Medium.woff2`
- `Inter-Medium.woff`
- `Inter-SemiBold.woff2`
- `Inter-SemiBold.woff`
- `Inter-Bold.woff2`
- `Inter-Bold.woff`

#### Amiri Font (Arabic)
Download from: https://fonts.google.com/specimen/Amiri
Required weights: 400, 700
Files needed:
- `Amiri-Regular.woff2`
- `Amiri-Regular.woff`
- `Amiri-Bold.woff2`
- `Amiri-Bold.woff`

#### Fira Code Font
Download from: https://fonts.google.com/specimen/Fira+Code
Required weights: 400
Files needed:
- `FiraCode-Regular.woff2`
- `FiraCode-Regular.woff`

### Step 3: Font File Structure
```
docs/
├── fonts/
│   ├── Inter-Regular.woff2
│   ├── Inter-Regular.woff
│   ├── Inter-Medium.woff2
│   ├── Inter-Medium.woff
│   ├── Inter-SemiBold.woff2
│   ├── Inter-SemiBold.woff
│   ├── Inter-Bold.woff2
│   ├── Inter-Bold.woff
│   ├── Amiri-Regular.woff2
│   ├── Amiri-Regular.woff
│   ├── Amiri-Bold.woff2
│   ├── Amiri-Bold.woff
│   ├── FiraCode-Regular.woff2
│   └── FiraCode-Regular.woff
├── styles.css
├── scripts.js
└── index.html
```

## Configuration / التكوين

The CSS file (`styles.css`) is already configured with `@font-face` declarations that will automatically use local fonts when available and fallback to Google Fonts when not.

### Font Loading Priority:
1. Local fonts (from `fonts/` directory)
2. Google Fonts (CDN)
3. System fonts (fallback)

## Testing Local Fonts / اختبار الخطوط المحلية

1. Disconnect from internet
2. Open `docs/index.html` in browser
3. Check if fonts load correctly
4. Verify Arabic text displays properly

## Troubleshooting / استكشاف الأخطاء

### Fonts Not Loading
- Check file paths in `styles.css`
- Verify font files are in correct directory
- Check browser developer tools for 404 errors

### Arabic Text Issues
- Ensure Amiri font files are present
- Check `dir="rtl"` attribute is set
- Verify Unicode support in browser

### Performance Issues
- Use WOFF2 format for better compression
- Enable font-display: swap for faster loading
- Consider preloading critical fonts

## Enterprise Deployment / النشر المؤسسي

For enterprise environments that block external CDNs:

1. Download all font files locally
2. Update Content Security Policy if needed
3. Test in isolated network environment
4. Consider using font subsetting for smaller files

## Browser Support / دعم المتصفحات

- WOFF2: Modern browsers (recommended)
- WOFF: Legacy browser support
- Fallback fonts: All browsers

## License Information / معلومات الترخيص

- **Inter**: SIL Open Font License 1.1
- **Amiri**: SIL Open Font License 1.1  
- **Fira Code**: SIL Open Font License 1.1

All fonts are free for commercial and personal use.

---

For technical support, contact: f5@hotmail.com
للدعم التقني، اتصل بـ: f5@hotmail.com
