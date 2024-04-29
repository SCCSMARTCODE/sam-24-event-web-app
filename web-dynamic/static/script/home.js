const images = document.querySelectorAll('.image');

images.forEach(image => {
  image.addEventListener('click', function() {
    const popup = document.createElement('div');
    popup.classList.add('popup');

    const popupImage = document.createElement('img');
    popupImage.src = this.src;

    popup.appendChild(popupImage);
    document.body.appendChild(popup);

    popup.addEventListener('click', function() {
      document.body.removeChild(popup);
    });
  });
});

// // Array of image URLs
// const imageUrls = ["home1.jpg", "home2.jpg", "home3.jpg", "home1.jpg"];

// // Index of the current image
// let currentIndex = 0;

// // Function to change the background image
// function changeBackgroundImage() {
//   // Get the background section element
//   const backgroundSection = document.getElementById('backgroundSection');
  
//   // Update the background image
//   backgroundSection.style.backgroundImage = `url(${imageUrls[currentIndex]})`;
  
//   // Increment the index
//   currentIndex = (currentIndex + 1) % imageUrls.length;
// }

// // Call the changeBackgroundImage function every 5 seconds
// setInterval(changeBackgroundImage, 5000);

// JavaScript for navigating to previous and next slides
const prevSlide = document.querySelector('.prev-slider');
const nextSlide = document.querySelector('.next-slider');
const slider = document.querySelector('.slider');

prevSlide.addEventListener('click', (event) => {
  event.preventDefault(); // Prevent the default behavior of the anchor element
  slider.scrollLeft -= slider.offsetWidth;
});

nextSlide.addEventListener('click', (event) => {
  event.preventDefault(); // Prevent the default behavior of the anchor element
  slider.scrollLeft += slider.offsetWidth;
});

window.onload = function() {
  document.getElementById('loading-overlay').style.display = 'none';
};