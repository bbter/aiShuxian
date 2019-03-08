$(function () {
    init_top_swiper();
    init_must_buy();
});


function init_top_swiper() {
    var mySwiper = new Swiper('#topSwiper', {
        loop: true, // 循环模式选项
        // 如果需要分页器
        pagination: {
            el: '.swiper-pagination',
        },
        autoplay: 2000,
        // 如果需要前进后退按钮
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },

    })
}

function init_must_buy() {
    var swiper = new Swiper('#swiperMenu', {
        slidesPerView: 3,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
    });
}