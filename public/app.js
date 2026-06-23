const grid = document.getElementById('product-grid');
const loadingSpinner = document.getElementById('loading-spinner');
const endMessage = document.getElementById('end-message');
const categoryFilter = document.getElementById('category-filter');
const statsText = document.getElementById('stats-text');

let currentCursor = null;
let currentCategory = 'All';
let isFetching = false;
let hasMore = true;
let totalLoaded = 0;

// Format price as currency
const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
};

// Format date relative or absolute
const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// Create a DOM element for a product
const createProductCard = (product) => {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    card.innerHTML = `
        <div class="product-category">${product.category}</div>
        <div class="product-name">${product.name}</div>
        <div class="product-date">Added: ${formatDate(product.created_at)}</div>
        <div class="product-price">${formatPrice(product.price)}</div>
    `;
    
    return card;
};

// Fetch products from the API
const fetchProducts = async () => {
    if (isFetching || !hasMore) return;
    
    isFetching = true;
    loadingSpinner.classList.remove('hidden');
    
    try {
        let url = `/api/products?limit=40`;
        if (currentCursor) url += `&cursor=${currentCursor}`;
        if (currentCategory !== 'All') url += `&category=${encodeURIComponent(currentCategory)}`;
        
        const response = await fetch(url);
        const { data, nextCursor } = await response.json();
        
        if (data.length === 0) {
            hasMore = false;
            loadingSpinner.classList.add('hidden');
            endMessage.classList.remove('hidden');
            return;
        }
        
        // Append products
        data.forEach(product => {
            grid.appendChild(createProductCard(product));
        });
        
        totalLoaded += data.length;
        statsText.textContent = `Showing ${totalLoaded} products`;
        
        currentCursor = nextCursor;
        if (!nextCursor) {
            hasMore = false;
            endMessage.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Failed to fetch products:', error);
    } finally {
        isFetching = false;
        loadingSpinner.classList.add('hidden');
    }
};

// Fetch distinct categories to populate the filter
const fetchCategories = async () => {
    try {
        const response = await fetch('/api/categories');
        const { data } = await response.json();
        
        data.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categoryFilter.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to fetch categories:', error);
    }
};

// Handle category change
categoryFilter.addEventListener('change', (e) => {
    currentCategory = e.target.value;
    
    // Reset state
    grid.innerHTML = '';
    currentCursor = null;
    hasMore = true;
    totalLoaded = 0;
    endMessage.classList.add('hidden');
    
    // Fetch fresh
    fetchProducts();
});

// Intersection Observer for Infinite Scroll
const setupIntersectionObserver = () => {
    const observer = new IntersectionObserver((entries) => {
        const target = entries[0];
        if (target.isIntersecting && hasMore && !isFetching) {
            fetchProducts();
        }
    }, {
        root: null,
        rootMargin: '100px', // Fetch before reaching exactly the bottom
        threshold: 0.1
    });
    
    observer.observe(loadingSpinner);
};

// Simulate 50 new items added concurrently
document.getElementById('add-mock-data-btn').addEventListener('click', async (e) => {
    const btn = e.target;
    btn.disabled = true;
    btn.textContent = 'Simulating...';
    
    try {
        await fetch('/api/simulate', { method: 'POST' });
        alert('Simulated 50 new products added to the DB. If you continue scrolling, you will notice no duplicates are shown or skipped, thanks to cursor pagination!');
    } catch (error) {
        console.error('Failed to simulate:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Simulate 50 New Arrivals';
    }
});

// Initialize
const init = async () => {
    await fetchCategories();
    setupIntersectionObserver();
    // fetchProducts is triggered by the intersection observer initially seeing the loading spinner
};

init();
