// Festival Sale Navigation Functions
let currentSaleIndex = 1;
const totalSales = 3;

function previousSale() {
    currentSaleIndex = currentSaleIndex > 1 ? currentSaleIndex - 1 : totalSales;
    updateSaleDisplay();
    updateIndicators();
}

function nextSale() {
    currentSaleIndex = currentSaleIndex < totalSales ? currentSaleIndex + 1 : 1;
    updateSaleDisplay();
    updateIndicators();
}

function goToSale(index) {
    currentSaleIndex = index;
    updateSaleDisplay();
    updateIndicators();
}

function updateSaleDisplay() {
    // This function would update the sale content based on currentSaleIndex
    // For now, we'll just add a visual feedback
    const saleBanner = document.querySelector('.sale-banner');
    if (saleBanner) {
        saleBanner.style.opacity = '0.7';
        setTimeout(() => {
            saleBanner.style.opacity = '1';
        }, 300);
    }
}

function updateIndicators() {
    const indicators = document.querySelectorAll('.indicator');
    indicators.forEach((indicator, index) => {
        indicator.classList.toggle('active', index + 1 === currentSaleIndex);
    });
}

// Auto-advance slides every 5 seconds
function autoAdvance() {
    setInterval(() => {
        nextSale();
    }, 5000);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateIndicators();
    // Uncomment the line below if you want auto-advancing slides
    // autoAdvance();
    
    // Add keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') {
            previousSale();
        } else if (e.key === 'ArrowRight') {
            nextSale();
        }
    });
    
    // Add touch/swipe support for mobile
    let startX = 0;
    let endX = 0;
    
    const saleContainer = document.querySelector('.sale-container');
    if (saleContainer) {
        saleContainer.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
        });
        
        saleContainer.addEventListener('touchend', function(e) {
            endX = e.changedTouches[0].clientX;
            handleSwipe();
        });
    }
    
    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = startX - endX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                nextSale(); // Swipe left - next slide
            } else {
                previousSale(); // Swipe right - previous slide
            }
        }
    }
});

// Add smooth scroll behavior for better UX
document.documentElement.style.scrollBehavior = 'smooth';
