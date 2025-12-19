// const video = document.getElementById("postVideo");
// const overlay = document.getElementById("playOverlay");

// function toggleVideo() {
//     if (video.paused) {
//         video.play();
//         overlay.style.opacity = "0";
//         overlay.style.pointerEvents = "none";
//     } else {
//         video.pause();
//         overlay.style.opacity = "1";
//         overlay.style.pointerEvents = "auto";
//     }
// }

// video.addEventListener("ended", () => {
//     video.currentTime = 0;
//     overlay.style.opacity = "1";
//     overlay.style.pointerEvents = "auto";
// });

function toggleVideo(video) {
    const overlay = video.nextElementSibling;
    if (video.paused) {
        video.play();
        overlay.style.display = "none";
    } else {
        video.pause();
        overlay.style.display = "flex";
    }
}