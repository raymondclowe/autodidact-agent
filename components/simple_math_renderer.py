"""
Simple client-side math renderer for basic LaTeX expressions
as a fallback when MathJax CDN is not available.
"""

MATH_RENDERER_JS = """
<script>
// Simple math renderer for basic LaTeX expressions
window.SimpleMathRenderer = {
    // Map of common LaTeX symbols to Unicode
    symbols: {
        '\\\\times': '×',
        '\\\\cdot': '·',
        '\\\\div': '÷',
        '\\\\pm': '±',
        '\\\\mp': '∓',
        '\\\\leq': '≤',
        '\\\\geq': '≥',
        '\\\\neq': '≠',
        '\\\\ne': '≠',
        '\\\\approx': '≈',
        '\\\\sim': '∼',
        '\\\\equiv': '≡',
        '\\\\propto': '∝',
        '\\\\infty': '∞',
        '\\\\alpha': 'α',
        '\\\\beta': 'β',
        '\\\\gamma': 'γ',
        '\\\\delta': 'δ',
        '\\\\epsilon': 'ε',
        '\\\\theta': 'θ',
        '\\\\lambda': 'λ',
        '\\\\mu': 'μ',
        '\\\\pi': 'π',
        '\\\\sigma': 'σ',
        '\\\\phi': 'φ',
        '\\\\omega': 'ω',
        '\\\\Gamma': 'Γ',
        '\\\\Delta': 'Δ',
        '\\\\Theta': 'Θ',
        '\\\\Lambda': 'Λ',
        '\\\\Sigma': 'Σ',
        '\\\\Phi': 'Φ',
        '\\\\Omega': 'Ω'
    },
    
    // Render simple math expressions
    renderExpression: function(latex) {
        let result = latex;
        
        // Replace symbols
        for (let symbol in this.symbols) {
            result = result.replace(new RegExp(symbol, 'g'), this.symbols[symbol]);
        }
        
        // Handle fractions (simple case: \\frac{a}{b})
        result = result.replace(/\\\\frac\s*\{([^}]+)\}\s*\{([^}]+)\}/g, function(match, num, den) {
            return '<span style="display: inline-block; vertical-align: middle;"><span style="display: block; text-align: center; border-bottom: 1px solid; padding: 0 4px;">' + num + '</span><span style="display: block; text-align: center; padding: 0 4px;">' + den + '</span></span>';
        });
        
        // Handle superscripts (simple case: ^{n} or ^n)
        result = result.replace(/\^(\{[^}]+\}|\w)/g, function(match, exp) {
            let cleanExp = exp.replace(/[{}]/g, '');
            return '<sup>' + cleanExp + '</sup>';
        });
        
        // Handle subscripts (simple case: _{n} or _n)
        result = result.replace(/_(\{[^}]+\}|\w)/g, function(match, sub) {
            let cleanSub = sub.replace(/[{}]/g, '');
            return '<sub>' + cleanSub + '</sub>';
        });
        
        // Handle square roots (simple case: \\sqrt{expression})
        result = result.replace(/\\\\sqrt\s*\{([^}]+)\}/g, function(match, expr) {
            return '√(' + expr + ')';
        });
        
        // Clean up remaining backslashes and spaces
        result = result.replace(/\\\\/g, '');
        result = result.replace(/\s+/g, ' ');
        
        return result;
    },
    
    // Process all math expressions on the page
    processPage: function() {
        console.log('Processing page with SimpleMathRenderer...');
        
        // Find all display math [expression]
        let displayMath = document.querySelectorAll('p, div, span');
        displayMath.forEach(function(element) {
            let content = element.innerHTML;
            if (content.includes('[') && content.includes(']')) {
                // Replace display math expressions
                content = content.replace(/\[([^[\]]+)\]/g, function(match, expr) {
                    let rendered = SimpleMathRenderer.renderExpression(expr);
                    return '<span style="display: block; text-align: center; margin: 10px 0; font-style: italic; font-weight: bold;">' + rendered + '</span>';
                });
                element.innerHTML = content;
            }
            
            // Replace inline math expressions (expression)
            content = element.innerHTML;
            if (content.includes('(') && content.includes(')')) {
                content = content.replace(/\(([^()]*\\\\[^()]*[^()]*)\)/g, function(match, expr) {
                    if (expr.includes('\\\\')) { // Only process if it contains LaTeX
                        let rendered = SimpleMathRenderer.renderExpression(expr);
                        return '<span style="font-style: italic;">' + rendered + '</span>';
                    }
                    return match;
                });
                element.innerHTML = content;
            }
        });
        
        console.log('SimpleMathRenderer processing completed');
    }
};

// Auto-process the page when it loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(SimpleMathRenderer.processPage, 100);
    });
} else {
    setTimeout(SimpleMathRenderer.processPage, 100);
}
</script>
"""