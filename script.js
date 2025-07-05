// ===============================
//   🌟 NEON FREELANCE APP JS 🌟
// ===============================

// Mock Data - Реальные данные для демонстрации
const mockOrders = [
    {
        id: 1,
        title: "Разработка современного сайта с ИИ",
        description: "Нужен крутой сайт с интеграцией ChatGPT API, неоновым дизайном и адаптивной версткой. Должен работать быстро и выглядеть как из будущего!",
        category: "programming",
        price: 2500,
        currency: "USD",
        deadline: "2024-03-15",
        client: "TechStartup",
        rating: 4.9,
        urgent: true,
        views: 234,
        bids: 12
    },
    {
        id: 2,
        title: "Дизайн логотипа для криптопроекта",
        description: "Создать неоновый логотип для DeFi платформы. Стиль - кибerpанк, должен светиться и быть запоминающимся.",
        category: "design",
        price: 800,
        currency: "USD",
        deadline: "2024-02-28",
        client: "CryptoDAO",
        rating: 4.7,
        urgent: false,
        views: 156,
        bids: 8
    },
    {
        id: 3,
        title: "SMM для NFT коллекции",
        description: "Продвижение NFT коллекции в Twitter, Discord, Instagram. Нужен опыт в крипто-маркетинге и понимание Web3.",
        category: "marketing",
        price: 1200,
        currency: "USD",
        deadline: "2024-03-01",
        client: "NFTArtist",
        rating: 4.8,
        urgent: true,
        views: 189,
        bids: 15
    },
    {
        id: 4,
        title: "Мобильное приложение для фитнеса",
        description: "React Native приложение с трекингом тренировок, ИИ-советчиком и социальными функциями.",
        category: "mobile",
        price: 5000,
        currency: "USD",
        deadline: "2024-04-15",
        client: "FitnessTech",
        rating: 5.0,
        urgent: false,
        views: 312,
        bids: 23
    },
    {
        id: 5,
        title: "Копирайтинг для стартапа",
        description: "Написать продающие тексты для лендинга ИИ-сервиса. Нужен опыт в tech-копирайтинге.",
        category: "writing",
        price: 600,
        currency: "USD",
        deadline: "2024-02-25",
        client: "AICompany",
        rating: 4.6,
        urgent: false,
        views: 98,
        bids: 7
    },
    {
        id: 6,
        title: "Видеоролик для TikTok",
        description: "Создать вирусный ролик о блокчейне простым языком. Анимация + монтаж + креативная подача.",
        category: "video",
        price: 400,
        currency: "USD",
        deadline: "2024-02-22",
        client: "BlockchainEdu",
        rating: 4.5,
        urgent: true,
        views: 145,
        bids: 11
    }
];

const mockFreelancers = [
    {
        id: 1,
        name: "Алексей Кодеров",
        avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face",
        rating: 4.9,
        reviews: 127,
        skills: ["React", "Node.js", "Web3", "AI"],
        price: 50,
        online: true,
        verified: true
    },
    {
        id: 2,
        name: "Мария Дизайнер",
        avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b77c?w=80&h=80&fit=crop&crop=face",
        rating: 4.8,
        reviews: 89,
        skills: ["UI/UX", "Figma", "3D", "Branding"],
        price: 35,
        online: true,
        verified: true
    },
    {
        id: 3,
        name: "Сергей Маркетолог",
        avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=80&h=80&fit=crop&crop=face",
        rating: 4.7,
        reviews: 156,
        skills: ["SMM", "Crypto", "Growth", "Analytics"],
        price: 40,
        online: false,
        verified: true
    }
];

// Current user state
let currentUser = null;
let currentFilter = 'all';
let currentOrders = [...mockOrders];

// DOM Elements
const ordersGrid = document.getElementById('orders-grid');
const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    renderOrders();
    initializeAnimations();
    setupEventListeners();
    startBackgroundAnimations();
});

// ===============================
//        CORE FUNCTIONS
// ===============================

function renderOrders() {
    if (!ordersGrid) return;
    
    ordersGrid.innerHTML = '';
    
    currentOrders.forEach(order => {
        const orderCard = createOrderCard(order);
        ordersGrid.appendChild(orderCard);
    });
    
    // Add animation delay to cards
    const cards = ordersGrid.querySelectorAll('.order-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('slide-in');
    });
}

function createOrderCard(order) {
    const card = document.createElement('div');
    card.className = 'order-card neon-card';
    card.onclick = () => showOrderDetails(order);
    
    const urgentBadge = order.urgent ? '<span class="urgent-badge">🔥 СРОЧНО</span>' : '';
    const categoryIcons = {
        programming: 'fas fa-code',
        design: 'fas fa-palette',
        marketing: 'fas fa-bullhorn',
        writing: 'fas fa-pen',
        video: 'fas fa-video',
        mobile: 'fas fa-mobile-alt'
    };
    
    card.innerHTML = `
        <div class="order-header">
            <div class="order-category">
                <i class="${categoryIcons[order.category]}"></i>
                ${getCategoryName(order.category)}
            </div>
            ${urgentBadge}
        </div>
        <h3 class="order-title neon-text">${order.title}</h3>
        <p class="order-description">${order.description.substring(0, 120)}...</p>
        <div class="order-meta">
            <div class="order-client">
                <i class="fas fa-user"></i>
                ${order.client}
                <span class="rating">
                    <i class="fas fa-star"></i>
                    ${order.rating}
                </span>
            </div>
            <div class="order-stats">
                <span><i class="fas fa-eye"></i> ${order.views}</span>
                <span><i class="fas fa-comments"></i> ${order.bids}</span>
            </div>
        </div>
        <div class="order-footer">
            <div class="order-price neon-text">$${order.price.toLocaleString()}</div>
            <div class="order-deadline">
                <i class="fas fa-clock"></i>
                ${formatDate(order.deadline)}
            </div>
        </div>
        <div class="order-actions">
            <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); placeBid(${order.id})">
                <i class="fas fa-paper-plane"></i>
                Откликнуться
            </button>
            <button class="btn btn-outline btn-sm" onclick="event.stopPropagation(); saveOrder(${order.id})">
                <i class="fas fa-heart"></i>
                Сохранить
            </button>
        </div>
    `;
    
    return card;
}

function getCategoryName(category) {
    const categories = {
        programming: 'Программирование',
        design: 'Дизайн',
        marketing: 'Маркетинг',
        writing: 'Копирайтинг',
        video: 'Видео',
        mobile: 'Мобильные приложения'
    };
    return categories[category] || category;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = date - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'Просрочен';
    if (diffDays === 0) return 'Сегодня';
    if (diffDays === 1) return 'Завтра';
    return `${diffDays} дн.`;
}

// ===============================
//        MODAL FUNCTIONS
// ===============================

function showLogin() {
    showModal('loginModal');
}

function showRegister() {
    showModal('registerModal');
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        modal.style.display = 'flex';
        
        // Add glow effect
        modal.querySelector('.modal-content').style.animation = 'modalGlow 0.5s ease';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
}

// Close modal on backdrop click
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        closeModal(e.target.id);
    }
});

// ===============================
//       ORDER FUNCTIONS
// ===============================

function filterOrders(category) {
    currentFilter = category;
    
    // Update filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    if (category === 'all') {
        currentOrders = [...mockOrders];
    } else {
        currentOrders = mockOrders.filter(order => order.category === category);
    }
    
    renderOrders();
    showNotification(`Показаны заказы: ${getCategoryName(category)}`, 'info');
}

function searchOrders(query) {
    if (!query.trim()) {
        currentOrders = [...mockOrders];
    } else {
        currentOrders = mockOrders.filter(order =>
            order.title.toLowerCase().includes(query.toLowerCase()) ||
            order.description.toLowerCase().includes(query.toLowerCase()) ||
            order.client.toLowerCase().includes(query.toLowerCase())
        );
    }
    renderOrders();
}

function showOrderDetails(order) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.style.display = 'flex';
    modal.id = 'orderModal';
    
    modal.innerHTML = `
        <div class="modal-content order-modal">
            <div class="modal-header">
                <h2 class="neon-text">${order.title}</h2>
                <span class="close" onclick="closeModal('orderModal')">&times;</span>
            </div>
            <div class="modal-body">
                <div class="order-full-info">
                    <div class="order-badges">
                        <span class="category-badge">
                            <i class="fas fa-tag"></i>
                            ${getCategoryName(order.category)}
                        </span>
                        ${order.urgent ? '<span class="urgent-badge">🔥 СРОЧНО</span>' : ''}
                    </div>
                    
                    <div class="order-description-full">
                        <h3>Описание проекта</h3>
                        <p>${order.description}</p>
                    </div>
                    
                    <div class="order-details-grid">
                        <div class="detail-item">
                            <i class="fas fa-dollar-sign neon-icon"></i>
                            <div>
                                <strong>Бюджет</strong>
                                <span class="neon-text">$${order.price.toLocaleString()}</span>
                            </div>
                        </div>
                        
                        <div class="detail-item">
                            <i class="fas fa-clock neon-icon"></i>
                            <div>
                                <strong>Срок</strong>
                                <span>${formatDate(order.deadline)}</span>
                            </div>
                        </div>
                        
                        <div class="detail-item">
                            <i class="fas fa-user neon-icon"></i>
                            <div>
                                <strong>Заказчик</strong>
                                <span>${order.client}</span>
                            </div>
                        </div>
                        
                        <div class="detail-item">
                            <i class="fas fa-star neon-icon"></i>
                            <div>
                                <strong>Рейтинг</strong>
                                <span>${order.rating} ⭐</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="order-stats-full">
                        <div class="stat">
                            <i class="fas fa-eye"></i>
                            <span>${order.views} просмотров</span>
                        </div>
                        <div class="stat">
                            <i class="fas fa-comments"></i>
                            <span>${order.bids} откликов</span>
                        </div>
                    </div>
                    
                    <div class="order-actions-full">
                        <button class="btn btn-primary btn-large" onclick="placeBid(${order.id})">
                            <i class="fas fa-paper-plane"></i>
                            Откликнуться на проект
                        </button>
                        <button class="btn btn-outline btn-large" onclick="contactClient(${order.id})">
                            <i class="fas fa-message"></i>
                            Написать заказчику
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function placeBid(orderId) {
    const order = mockOrders.find(o => o.id === orderId);
    if (!order) return;
    
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.style.display = 'flex';
    modal.id = 'bidModal';
    
    modal.innerHTML = `
        <div class="modal-content bid-modal">
            <div class="modal-header">
                <h2 class="neon-text">Откликнуться на проект</h2>
                <span class="close" onclick="closeModal('bidModal')">&times;</span>
            </div>
            <div class="modal-body">
                <form id="bidForm" onsubmit="submitBid(event, ${orderId})">
                    <div class="form-group">
                        <label>Ваша цена (USD)</label>
                        <input type="number" min="1" required placeholder="Введите сумму">
                    </div>
                    
                    <div class="form-group">
                        <label>Срок выполнения (дней)</label>
                        <select required>
                            <option value="">Выберите срок</option>
                            <option value="1">1 день</option>
                            <option value="3">3 дня</option>
                            <option value="7">1 неделя</option>
                            <option value="14">2 недели</option>
                            <option value="30">1 месяц</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Сопроводительное письмо</label>
                        <textarea rows="5" required placeholder="Расскажите, почему именно вы подходите для этого проекта..."></textarea>
                    </div>
                    
                    <button type="submit" class="btn btn-primary btn-full">
                        <i class="fas fa-rocket"></i>
                        Отправить отклик
                    </button>
                </form>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function submitBid(event, orderId) {
    event.preventDefault();
    
    // Simulate bid submission
    showNotification('Отклик успешно отправлен! 🚀', 'success');
    closeModal('bidModal');
    closeModal('orderModal');
    
    // Update order bids count
    const order = mockOrders.find(o => o.id === orderId);
    if (order) {
        order.bids++;
        renderOrders();
    }
}

function saveOrder(orderId) {
    showNotification('Заказ добавлен в избранное ❤️', 'success');
}

function contactClient(orderId) {
    showNotification('Чат с заказчиком открыт 💬', 'info');
}

// ===============================
//       CREATE ORDER
// ===============================

function showCreateOrder() {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.style.display = 'flex';
    modal.id = 'createOrderModal';
    
    modal.innerHTML = `
        <div class="modal-content create-order-modal">
            <div class="modal-header">
                <h2 class="neon-text">Создать новый заказ</h2>
                <span class="close" onclick="closeModal('createOrderModal')">&times;</span>
            </div>
            <div class="modal-body">
                <form id="createOrderForm" onsubmit="submitOrder(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Название проекта</label>
                            <input type="text" required placeholder="Например: Разработка мобильного приложения">
                        </div>
                        
                        <div class="form-group">
                            <label>Категория</label>
                            <select required>
                                <option value="">Выберите категорию</option>
                                <option value="programming">🖥️ Программирование</option>
                                <option value="design">🎨 Дизайн</option>
                                <option value="marketing">📊 Маркетинг</option>
                                <option value="writing">📝 Копирайтинг</option>
                                <option value="video">🎬 Видео</option>
                                <option value="mobile">📱 Мобильные приложения</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Описание проекта</label>
                        <textarea rows="6" required placeholder="Детально опишите что нужно сделать, какой результат ожидаете..."></textarea>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Бюджет (USD)</label>
                            <input type="number" min="1" required placeholder="1000">
                        </div>
                        
                        <div class="form-group">
                            <label>Срок выполнения</label>
                            <input type="date" required>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <div class="checkbox-group">
                            <label class="checkbox-label">
                                <input type="checkbox" name="urgent">
                                <span class="checkmark"></span>
                                🔥 Срочный заказ (+20% к бюджету)
                            </label>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-primary btn-full">
                        <i class="fas fa-plus"></i>
                        Опубликовать заказ
                    </button>
                </form>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function submitOrder(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    const newOrder = {
        id: mockOrders.length + 1,
        title: formData.get('title') || form.querySelector('input[type="text"]').value,
        description: form.querySelector('textarea').value,
        category: form.querySelector('select').value,
        price: parseInt(form.querySelector('input[type="number"]').value),
        currency: 'USD',
        deadline: form.querySelector('input[type="date"]').value,
        client: 'Вы',
        rating: 5.0,
        urgent: form.querySelector('input[name="urgent"]').checked,
        views: 0,
        bids: 0
    };
    
    mockOrders.unshift(newOrder);
    currentOrders = [...mockOrders];
    renderOrders();
    
    showNotification('Заказ успешно опубликован! 🎉', 'success');
    closeModal('createOrderModal');
}

// ===============================
//       FREELANCERS
// ===============================

function showFreelancers() {
    const section = document.createElement('section');
    section.className = 'freelancers-section';
    section.innerHTML = `
        <div class="container">
            <h2 class="section-title neon-text">Топ исполнители</h2>
            <div class="freelancers-grid" id="freelancers-grid"></div>
        </div>
    `;
    
    // Replace orders section temporarily
    const ordersSection = document.querySelector('.orders-section');
    ordersSection.style.display = 'none';
    ordersSection.parentNode.insertBefore(section, ordersSection.nextSibling);
    
    renderFreelancers();
}

function renderFreelancers() {
    const grid = document.getElementById('freelancers-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    mockFreelancers.forEach(freelancer => {
        const card = createFreelancerCard(freelancer);
        grid.appendChild(card);
    });
}

function createFreelancerCard(freelancer) {
    const card = document.createElement('div');
    card.className = 'freelancer-card neon-card';
    
    const onlineStatus = freelancer.online ? 
        '<span class="online-status online">🟢 В сети</span>' : 
        '<span class="online-status offline">⚫ Не в сети</span>';
    
    const verifiedBadge = freelancer.verified ? 
        '<span class="verified-badge">✅ Проверен</span>' : '';
    
    card.innerHTML = `
        <div class="freelancer-header">
            <div class="freelancer-avatar">
                <img src="${freelancer.avatar}" alt="${freelancer.name}">
                ${onlineStatus}
            </div>
            <div class="freelancer-info">
                <h3 class="freelancer-name neon-text">${freelancer.name}</h3>
                <div class="freelancer-rating">
                    <i class="fas fa-star"></i>
                    ${freelancer.rating} (${freelancer.reviews} отзывов)
                </div>
                ${verifiedBadge}
            </div>
        </div>
        
        <div class="freelancer-skills">
            ${freelancer.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
        </div>
        
        <div class="freelancer-price">
            <span class="price neon-text">$${freelancer.price}/час</span>
        </div>
        
        <div class="freelancer-actions">
            <button class="btn btn-primary" onclick="contactFreelancer(${freelancer.id})">
                <i class="fas fa-message"></i>
                Написать
            </button>
            <button class="btn btn-outline" onclick="inviteToProject(${freelancer.id})">
                <i class="fas fa-user-plus"></i>
                Пригласить
            </button>
        </div>
    `;
    
    return card;
}

function contactFreelancer(freelancerId) {
    showNotification('Чат с исполнителем открыт 💬', 'info');
}

function inviteToProject(freelancerId) {
    showNotification('Приглашение отправлено! 📩', 'success');
}

// ===============================
//       ANIMATIONS
// ===============================

function initializeAnimations() {
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slide-in {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .slide-in {
            animation: slide-in 0.6s ease forwards;
        }
        
        @keyframes modalGlow {
            0% {
                box-shadow: 0 0 0 rgba(0, 255, 255, 0);
            }
            50% {
                box-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
            }
            100% {
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
            }
        }
        
        .neon-card {
            transition: all 0.4s ease;
        }
        
        .neon-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 
                0 0 20px rgba(0, 255, 255, 0.4),
                0 0 40px rgba(0, 255, 255, 0.2);
        }
        
        .neon-text {
            text-shadow: 0 0 10px currentColor;
        }
        
        .neon-icon {
            color: var(--neon-cyan);
            text-shadow: 0 0 10px var(--neon-cyan);
        }
    `;
    document.head.appendChild(style);
}

function startBackgroundAnimations() {
    // Create floating particles
    createFloatingParticles();
    
    // Animate stats numbers
    animateNumbers();
}

function createFloatingParticles() {
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'particles-container';
    particlesContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    `;
    
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.cssText = `
            position: absolute;
            width: 2px;
            height: 2px;
            background: ${i % 2 === 0 ? '#00ffff' : '#ff00ff'};
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: float ${5 + Math.random() * 10}s linear infinite;
            box-shadow: 0 0 6px currentColor;
        `;
        particlesContainer.appendChild(particle);
    }
    
    document.body.appendChild(particlesContainer);
}

function animateNumbers() {
    const stats = document.querySelectorAll('.stat-number');
    stats.forEach(stat => {
        const target = parseInt(stat.textContent);
        let current = 0;
        const increment = target / 100;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                stat.textContent = stat.textContent; // Keep original format
                clearInterval(timer);
            } else {
                stat.textContent = Math.floor(current) + (stat.textContent.includes('+') ? '+' : '');
            }
        }, 20);
    });
}

// ===============================
//       NOTIFICATIONS
// ===============================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 15px 20px;
        background: rgba(20, 20, 20, 0.9);
        border: 2px solid var(--neon-cyan);
        border-radius: 10px;
        color: white;
        z-index: 10001;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        animation: slideInRight 0.5s ease;
    `;
    
    if (type === 'success') {
        notification.style.borderColor = '#00ff00';
        notification.style.boxShadow = '0 0 20px rgba(0, 255, 0, 0.5)';
    } else if (type === 'error') {
        notification.style.borderColor = '#ff073a';
        notification.style.boxShadow = '0 0 20px rgba(255, 7, 58, 0.5)';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.5s ease';
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

// ===============================
//       UTILITY FUNCTIONS
// ===============================

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

function setupEventListeners() {
    // Form submissions
    document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
    document.getElementById('registerForm')?.addEventListener('submit', handleRegister);
    
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', handleNavigation);
    });
}

function handleLogin(event) {
    event.preventDefault();
    currentUser = { name: 'Пользователь', type: 'client' };
    showNotification('Добро пожаловать! 🎉', 'success');
    closeModal('loginModal');
}

function handleRegister(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    currentUser = { 
        name: formData.get('name') || 'Новый пользователь', 
        type: formData.get('userType') || 'client' 
    };
    showNotification('Регистрация успешна! Добро пожаловать! 🚀', 'success');
    closeModal('registerModal');
}

function handleNavigation(event) {
    event.preventDefault();
    const href = event.target.getAttribute('href');
    
    if (href === '#freelancers') {
        showFreelancers();
    } else if (href.startsWith('#')) {
        scrollToSection(href.substring(1));
    }
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');
}

// Add CSS animations
const additionalStyles = document.createElement('style');
additionalStyles.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .particles-container .particle {
        animation: float 10s linear infinite;
    }
    
    @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg); }
        100% { transform: translateY(-100px) rotate(360deg); }
    }
`;
document.head.appendChild(additionalStyles);

// Initialize everything when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('🌟 Neon Freelance App Loaded! 🌟');
    });
} else {
    console.log('🌟 Neon Freelance App Loaded! 🌟');
}