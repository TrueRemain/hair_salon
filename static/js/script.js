// мобильное меню
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// закрытие мобильного меню при нажатии на кнопку
document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', () => {
    hamburger.classList.remove('active');
    navMenu.classList.remove('active');
}));

// мягкий скролл для ссылок на странице
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// разымытие хедера 
window.addEventListener('scroll', () => {
    const header = document.querySelector('.header');
    if (window.scrollY > 100) {
        header.style.background = 'rgba(255, 255, 255, 0.95)';
        header.style.backdropFilter = 'blur(10px)';
    } else {
        header.style.background = 'var(--white)';
        header.style.backdropFilter = 'none';
    }
});

class Carousel {
    constructor() {
        this.track = document.querySelector('.carousel-track');
        this.items = Array.from(document.querySelectorAll('.carousel-item'));
        this.dots = Array.from(document.querySelectorAll('.dot'));
        this.prevBtn = document.querySelector('.prev-btn');
        this.nextBtn = document.querySelector('.next-btn');

        // Стартовый индекс
        const initialIndex = this.items.findIndex(it => it.classList.contains('active'));
        this.currentIndex = initialIndex >= 0 ? initialIndex : Math.floor(this.items.length / 2);

        this.totalItems = this.items.length;
        this.isAnimating = false;
        this.isVisible = false; // Добавляем отслеживание видимости

        // Автопрокрутка
        this.autoSlideInterval = null;
        this.autoSlideDelay = 10000;
        this.autoSlidePeriod = 5000;

        // Базовое положение трека
        this.baseTrackLeft = null;

        this.init();
        
        // Отслеживаем видимость галереи
        this.initVisibilityObserver();
        
        window.addEventListener('load', () => {
            this.calculateBaseTrackLeft();
            this.centerCarousel();
        });
        window.addEventListener('resize', () => {
            this.calculateBaseTrackLeft();
            this.centerCarousel();
        });
    }

    // НОВЫЙ МЕТОД: отслеживание видимости галереи
    initVisibilityObserver() {
        const gallerySection = document.querySelector('.gallery-section');
        if (!gallerySection) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                this.isVisible = entry.isIntersecting;
                
                if (this.isVisible) {
                    // Галерея видна - запускаем автопрокрутку
                    this.startAutoSlide();
                } else {
                    // Галерея не видна - останавливаем автопрокрутку
                    this.stopAutoSlide();
                }
            });
        }, {
            threshold: 0.3 // Срабатывает когда 30% галереи видно
        });

        observer.observe(gallerySection);
    }

    stopAutoSlide() {
        clearInterval(this.autoSlideInterval);
        if (this._resetTimeout) {
            clearTimeout(this._resetTimeout);
            this._resetTimeout = null;
        }
    }

    // Остальные методы остаются такими же, но обновляем startAutoSlide:
    startAutoSlide() {
        // Запускаем только если галерея видна
        if (!this.isVisible) return;
        
        this.stopAutoSlide();
        this.autoSlideInterval = setInterval(() => {
            if (!this.isAnimating && this.isVisible) {
                this.nextSlide();
            }
        }, this.autoSlidePeriod);
    }

    resetAutoSlide() {
        // Сбрасываем только если галерея видна
        if (!this.isVisible) return;
        
        this.stopAutoSlide();
        this._resetTimeout = setTimeout(() => {
            this.startAutoSlide();
            this._resetTimeout = null;
        }, this.autoSlideDelay);
    }

    calculateBaseTrackLeft() {
        const computed = getComputedStyle(this.track).transform;
        let currentTranslate = 0;
        if (computed && computed !== 'none') {
            currentTranslate = new DOMMatrix(computed).m41;
        }
        const rect = this.track.getBoundingClientRect();
        this.baseTrackLeft = rect.left - currentTranslate;
    }

    centerCarousel() {
        const activeItem = this.items[this.currentIndex];
        const carousel = document.querySelector('.carousel');

        if (!activeItem || !carousel) return;

        const carouselRect = carousel.getBoundingClientRect();
        const carouselCenter = carouselRect.left + carouselRect.width / 2;

        // ТОЧНОЕ ВЫЧИСЛЕНИЕ С УЧЕТОМ ВСЕХ КАРТОЧЕК
        let totalOffset = 0;
        
        // Проходим по всем карточкам до активной и суммируем их ширины + gap
        for (let i = 0; i < this.currentIndex; i++) {
            const item = this.items[i];
            if (item.classList.contains('active')) {
                totalOffset += 300; // активная карточка
            } else {
                totalOffset += 250; // неактивная карточка
            }
            totalOffset += 20; // gap между карточками
        }
        
        // Добавляем половину активной карточки
        const activeCardWidth = activeItem.classList.contains('active') ? 300 : 250;
        const activeCenterInsideTrack = totalOffset + (activeCardWidth / 2);

        const desiredTranslate = carouselCenter - this.baseTrackLeft - activeCenterInsideTrack;

        this.track.style.transform = `translateX(${desiredTranslate}px)`;
    }

    updateCarousel() {
        this.isAnimating = true;

        this.items.forEach(item => {
            item.classList.remove('active', 'prev-slide', 'next-slide');
        });

        const prevIndex = this.getPrevIndex();
        const nextIndex = this.getNextIndex();

        this.items[prevIndex].classList.add('prev-slide');
        this.items[this.currentIndex].classList.add('active');
        this.items[nextIndex].classList.add('next-slide');

        this.updateDots();

        if (this.baseTrackLeft === null) this.calculateBaseTrackLeft();
        this.centerCarousel();

        setTimeout(() => {
            this.isAnimating = false;
        }, 620);
    }

    getPrevIndex() {
        return (this.currentIndex - 1 + this.totalItems) % this.totalItems;
    }

    getNextIndex() {
        return (this.currentIndex + 1) % this.totalItems;
    }

    updateDots() {
        this.dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === this.currentIndex);
        });
    }

    prevSlide() {
        this.currentIndex = this.getPrevIndex();
        this.updateCarousel();
        this.resetAutoSlide();
    }

    nextSlide() {
        this.currentIndex = this.getNextIndex();
        this.updateCarousel();
        this.resetAutoSlide();
    }

    goToSlide(index) {
        if (index < 0 || index >= this.totalItems) return;
        this.currentIndex = index;
        this.updateCarousel();
        this.resetAutoSlide();
    }

    init() {
        this.updateCarousel();

        this.prevBtn.addEventListener('click', () => {
            if (!this.isAnimating) {
                this.prevSlide();
            }
        });

        this.nextBtn.addEventListener('click', () => {
            if (!this.isAnimating) {
                this.nextSlide();
            }
        });

        this.dots.forEach(dot => {
            dot.addEventListener('click', (e) => {
                if (!this.isAnimating) {
                    const index = parseInt(e.target.getAttribute('data-index'), 10);
                    if (!Number.isNaN(index)) {
                        this.goToSlide(index);
                    }
                }
            });
        });

        this.startAutoSlide();
    }
}

// Умная система записи
class SmartBookingSystem {
    constructor() {
        this.mastersSchedule = {
            'alexander': {
                name: 'Александр Петров',
                services: ['male_haircut', 'machine_haircut', 'royal_shave', 'beard_trim'],
                workDays: [1, 2, 3, 4, 5, 6],
            },
            'mikhail': {
                name: 'Михаил Козлов', 
                services: ['model_haircut', 'styling', 'gray_camouflage'],
                workDays: [0, 2, 3, 4, 5, 6],
            },
            'dmitry': {
                name: 'Дмитрий Соколов',
                services: ['model_haircut', 'beard_complex', 'gray_camouflage'],
                workDays: [1, 2, 3, 4, 5],
            }
        };

        this.services = {
            'male_haircut': { name: 'Мужская стрижка', duration: 60, price: '1200-2000 руб.' },
            'machine_haircut': { name: 'Стрижка машинкой', duration: 30, price: '800-1200 руб.' },
            'model_haircut': { name: 'Модельная стрижка', duration: 60, price: '1500-2500 руб.' },
            'styling': { name: 'Укладка и стайлинг', duration: 20, price: '500-1000 руб.' },
            'beard_trim': { name: 'Стрижка бороды', duration: 45, price: '800-1500 руб.' },
            'royal_shave': { name: 'Королевское бритье', duration: 45, price: '1200-2000 руб.' },
            'beard_complex': { name: 'Комплекс "Борода+"', duration: 75, price: '2000-3000 руб.' },
            'gray_camouflage': { name: 'Камуфляж седины', duration: 60, price: '1500-2500 руб.' }
        };
 
        this.handleFormSubmit = this.handleFormSubmit.bind(this);
        this.handleMasterChange = this.handleMasterChange.bind(this);
        this.handleDateChange = this.handleDateChange.bind(this);

        this.init();
    }

    init() {
        this.setMinDate();
        this.setupEventListeners();
    }

    setMinDate() {
        const dateInput = document.getElementById('date');
        if (dateInput) {
            const today = new Date().toISOString().split('T')[0];
            dateInput.min = today;
        }
    }

    setupEventListeners() {
        const form = document.getElementById('booking-form');
        const masterSelect = document.getElementById('master');
        const dateInput = document.getElementById('date');

        if (masterSelect) {
            masterSelect.addEventListener('change', this.handleMasterChange);
        }

        if (dateInput) {
            dateInput.addEventListener('change', this.handleDateChange);
        }

        if (form) {
            form.addEventListener('submit', this.handleFormSubmit);
        }
    } 
    // Добавьте эти новые методы:
    handleMasterChange() {
        this.updateServices();
        this.clearTimeSlots();
    }

    handleDateChange() {
        this.updateTimeSlots();
    }

    clearTimeSlots() {
        const timeSelect = document.getElementById('time');
        if (timeSelect) {
            timeSelect.innerHTML = '<option value="">-- Сначала выберите мастера и дату --</option>';
        }
    }

    updateServices() {
        const masterSelect = document.getElementById('master');
        const serviceSelect = document.getElementById('service');
        const selectedMaster = masterSelect.value;

        if (!serviceSelect) return;

        serviceSelect.innerHTML = '<option value="">-- Выберите услугу --</option>';

        if (selectedMaster && this.mastersSchedule[selectedMaster]) {
            const masterServices = this.mastersSchedule[selectedMaster].services;
            
            masterServices.forEach(serviceKey => {
                const service = this.services[serviceKey];
                const option = document.createElement('option');
                option.value = serviceKey;
                option.textContent = `${service.name} (${service.price})`;
                serviceSelect.appendChild(option);
            });
        }
    }

    async updateTimeSlots() {
        const masterSelect = document.getElementById('master');
        const dateInput = document.getElementById('date');
        const timeSelect = document.getElementById('time');

        if (!timeSelect) return;

        const selectedMaster = masterSelect.value;
        const selectedDate = dateInput.value;

        timeSelect.innerHTML = '<option value="">Загрузка...</option>';

        if (!selectedMaster || !selectedDate) {
            timeSelect.innerHTML = '<option value="">-- Сначала выберите мастера и дату --</option>';
            return;
        }

        try {
            // Пробуем разные URL для получения слотов
            const urls = [
                `/api/booking/slots/?master=${selectedMaster}&date=${selectedDate}`,
                `/homepage/api/booking/slots/?master=${selectedMaster}&date=${selectedDate}`,
            ];

            let response;
            let lastError;

            for (const url of urls) {
                try {
                    console.log('Запрос слотов по URL:', url);
                    response = await fetch(url);
                    if (response.ok) {
                        console.log('Успешный ответ от:', url);
                        break;
                    }
                } catch (err) {
                    lastError = err;
                    console.log('Ошибка для URL', url, err);
                }
            }

            if (!response || !response.ok) {
                throw new Error(`HTTP error! status: ${response?.status}`);
            }

            const data = await response.json();
            console.log('Получены данные слотов:', data);
            
            timeSelect.innerHTML = '<option value="">-- Выберите время --</option>';
            
            if (data.available_slots && data.available_slots.length > 0) {
                data.available_slots.forEach(time => {
                    const option = document.createElement('option');
                    option.value = time;
                    option.textContent = time;
                    timeSelect.appendChild(option);
                });
                console.log('Добавлено слотов:', data.available_slots.length);
            } else {
                timeSelect.innerHTML = '<option value="">На этот день нет свободных слотов</option>';
            }
            
        } catch (error) {
            console.error('Error fetching time slots:', error);
            timeSelect.innerHTML = '<option value="">Ошибка загрузки времени</option>';
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('name').value.trim(),
            phone: document.getElementById('phone').value.trim(),
            master: document.getElementById('master').value,
            service: document.getElementById('service').value,
            date: document.getElementById('date').value,
            time: document.getElementById('time').value,
        };

        const feedback = document.getElementById('booking-feedback');

        // Базовая валидация на клиенте
        if (!formData.name || !formData.phone || !formData.master || !formData.service || !formData.date || !formData.time) {
            feedback.innerHTML = '❌ Пожалуйста, заполните все поля';
            feedback.className = 'booking-feedback error';
            return;
        }

        // Показываем загрузку
        feedback.innerHTML = '<div style="color: #666;"><i class="fas fa-spinner fa-spin"></i> Отправка данных...</div>';
        feedback.className = 'booking-feedback';

        try {
            // Пробуем разные URL
            const urls = [
                '/api/booking/create/',  // Правильный URL
                '/homepage/api/booking/create/',
            ];

            let response;
            let lastError;

            for (const url of urls) {
                try {
                    console.log('Пробуем URL:', url);
                    response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCSRFToken(),
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    if (response.ok) {
                        console.log('Успешный ответ от:', url);
                        break;
                    }
                } catch (err) {
                    lastError = err;
                    console.log('Ошибка для URL', url, err);
                }
            }

            if (!response || !response.ok) {
                throw new Error(`HTTP error! status: ${response?.status}`);
            }

            const result = await response.json();
            console.log('Результат:', result);

            if (result.success) {
                let successHTML = result.message.replace(/\n/g, '<br>');
                
                // Добавляем информацию о ссылке для отзыва
                if (result.review_url) {
                    successHTML += `
                        <div style="margin-top: 1rem; padding: 1rem; background: #e7f3ff; border-radius: 8px; border: 1px solid #b3d9ff;">
                            <strong>🎉 Ссылка для оставления отзыва:</strong><br>
                            <a href="${result.review_url}" target="_blank" style="color: #0066cc; word-break: break-all; display: inline-block; margin: 0.5rem 0;">
                                ${result.review_url}
                            </a>
                            <br>
                            <small style="color: #666;">
                                ⚠️ Сохраните эту ссылку - она действительна 7 дней и может быть использована только один раз
                            </small>
                        </div>
                    `;
                }
                
                feedback.innerHTML = successHTML;
                feedback.className = 'booking-feedback success';
                document.getElementById('booking-form').reset();
                this.clearTimeSlots();
            } else {
                feedback.innerHTML = '❌ ' + result.message;
                feedback.className = 'booking-feedback error';
            }
            
        } catch (error) {
            console.error('Error submitting form:', error);
            feedback.innerHTML = '❌ Ошибка соединения с сервером. Проверьте консоль (F12) для деталей.';
            feedback.className = 'booking-feedback error';
        }
    }
    

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// выбор пакета
document.addEventListener('DOMContentLoaded', function() {
    const packageButtons = document.querySelectorAll('.package-btn');
    
    packageButtons.forEach(button => {
        button.addEventListener('click', function() {
            const packageCard = this.closest('.package-card');
            const packageName = packageCard.querySelector('h3').textContent;
            const packagePrice = packageCard.querySelector('.package-price').textContent;
            const bookingSection = document.getElementById('booking');
            if (bookingSection) {
                bookingSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                setTimeout(() => {
                    alert(`Вы выбрали пакет: ${packageName} за ${packagePrice}`);
                }, 1000);
            }
        });
    });
    
    // анимация для service
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.service-item, .package-card').forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(30px)';
        item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(item);
    });
}); 

// анимации страницы
document.addEventListener('DOMContentLoaded', function() {
    // анимация stats 
    function animateStats() {
        const stats = document.querySelectorAll('.stat-number');
        const durations = [2000, 2500, 3000];
        
        stats.forEach((stat, index) => {
            const target = parseInt(stat.textContent);
            const duration = durations[index];
            let start = 0;
            const increment = target / (duration / 16);
            
            function updateCount() {
                start += increment;
                if (start < target) {
                    stat.textContent = Math.floor(start) + '+';
                    requestAnimationFrame(updateCount);
                } else {
                    stat.textContent = target + '+';
                }
            }
            updateCount();
        });
    }
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                
                if (entry.target.classList.contains('about-hero')) {
                    setTimeout(animateStats, 500);
                }
            }
        });
    }, observerOptions);
    
    const animatedElements = document.querySelectorAll(
        '.philosophy-card, .story-content, .story-image, .team-member, .value-item'
    );
    
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // Observe hero section for stats animation
    const heroSection = document.querySelector('.about-hero');
    if (heroSection) {
        observer.observe(heroSection);
    }
    
    // Team member hover effects
    const teamMembers = document.querySelectorAll('.team-member');
    teamMembers.forEach(member => {
        member.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        member.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Инициализация системы записи - ПЕРЕНЕСЕНО СЮДА
    new SmartBookingSystem();
    
    // Инициализация карусели, если она есть на странице
    if (typeof Carousel !== 'undefined') {
        new Carousel();
    }
});